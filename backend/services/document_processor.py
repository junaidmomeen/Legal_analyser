import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import io
import time
import logging
import shutil
import subprocess
from typing import Optional, Tuple
from pathlib import Path
import os
import numpy as np

from models.analysis_models import DocumentProcessingResult

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing documents and extracting text with robust validation and OCR detection"""
    
    def __init__(self):
        # File size limits (in bytes)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_pdf_pages = 100
        self.max_image_dimension = 5000  # pixels
        
        # OCR configuration
        self.tesseract_available = self._detect_tesseract()
        self.tesseract_config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()[]{}"/\-@#$%^&*+=<>|~'

        
        # Supported formats
        self.supported_pdf_extensions = {'.pdf'}
        self.supported_image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        
        logger.info(f"DocumentProcessor initialized. Tesseract available: {self.tesseract_available}")
    
    def _detect_tesseract(self) -> bool:
        """Detect if Tesseract is available and properly configured"""
        try:
            # Try common Tesseract paths
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows default
                '/usr/bin/tesseract',  # Linux default
                '/opt/homebrew/bin/tesseract',  # macOS Homebrew
                '/usr/local/bin/tesseract',  # macOS/Linux alternative
                'tesseract'  # System PATH
            ]
            
            for path in tesseract_paths:
                try:
                    if os.path.exists(path) or path == 'tesseract':
                        pytesseract.pytesseract.tesseract_cmd = path
                        # Test with version command
                        version = pytesseract.get_tesseract_version()
                        logger.info(f"Tesseract detected at {path}, version: {version}")
                        return True
                except Exception as e:
                    continue
            
            # Final attempt with system call
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("Tesseract detected via system PATH")
                return True
                
        except Exception as e:
            logger.warning(f"Tesseract detection failed: {e}")
        
        logger.warning("⚠️ Tesseract OCR not detected. Image processing will be limited.")
        return False
    
    async def process_document(self, file_path: str, file_type: str = None) -> DocumentProcessingResult:
        """
        Process a document and extract text with comprehensive error handling
        
        Args:
            file_path: Path to the document file
            file_type: Type of file (pdf, image) - auto-detected if None
            
        Returns:
            DocumentProcessingResult: Processing result with extracted text
        """
        start_time = time.time()
        
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return DocumentProcessingResult(
                    success=False,
                    error_message=f"File not found: {file_path}",
                    processing_time=time.time() - start_time
                )
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Use detected type if not provided
            # file_type is now expected to be passed from main.py after validation
            
            logger.info(f"Processing {file_type} file: {Path(file_path).name} ({file_size} bytes)")
            
            # Process based on file type
            if file_type == "pdf":
                result = await self._process_pdf(file_path)
            elif file_type == "image":
                result = await self._process_image(file_path)
            else:
                return DocumentProcessingResult(
                    success=False,
                    error_message=f"Unsupported file type: {file_type}",
                    processing_time=time.time() - start_time
                )
            
            # Set processing time
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            # Log results
            if result.success:
                logger.info(f"Document processed successfully in {processing_time:.2f}s "
                          f"- {result.word_count} words extracted from {result.total_pages} pages")
            else:
                logger.error(f"Document processing failed after {processing_time:.2f}s: {result.error_message}")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Unexpected error processing document: {str(e)}")
            return DocumentProcessingResult(
                success=False,
                error_message=f"Processing error: {str(e)}",
                processing_time=processing_time
            )
    
    async def _process_pdf(self, file_path: str) -> DocumentProcessingResult:
        """Process PDF file and extract text with OCR fallback"""
        doc = None
        try:
            doc = fitz.open(file_path)
            extracted_text = ""
            total_pages = len(doc)
            ocr_pages = 0
            
            logger.info(f"Processing PDF with {total_pages} pages")
            
            for page_num in range(total_pages):
                try:
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    # If no text found or very little text, try OCR
                    if not text.strip() or len(text.strip()) < 50:
                        if self.tesseract_available:
                            logger.info(f"No text found on page {page_num + 1}, attempting OCR...")
                            try:
                                ocr_text = await self._ocr_pdf_page(page)
                                if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                                    text = ocr_text
                                    ocr_pages += 1
                            except Exception as ocr_error:
                                logger.warning(f"OCR failed for page {page_num + 1}: {ocr_error}")
                        else:
                            logger.warning(f"No text on page {page_num + 1} and OCR unavailable")
                            text = f"[Page {page_num + 1}: Text extraction failed - OCR not available]"
                    
                    extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
                    
                except Exception as page_error:
                    logger.error(f"Error processing page {page_num + 1}: {page_error}")
                    extracted_text += f"\n--- Page {page_num + 1} ---\n[Error extracting text from this page]\n"
            
            word_count = len(extracted_text.split())
            
            # Add processing notes
            processing_notes = []
            if ocr_pages > 0:
                processing_notes.append(f"OCR applied to {ocr_pages} pages")
            if not self.tesseract_available and total_pages > 0:
                processing_notes.append("OCR unavailable - some text may be missing")
            
            return DocumentProcessingResult(
                success=True,
                extracted_text=extracted_text.strip(),
                total_pages=total_pages,
                word_count=word_count,
                processing_notes=processing_notes
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
        finally:
            if doc:
                doc.close()
    
    async def _ocr_pdf_page(self, page) -> str:
        """Extract text from PDF page using OCR"""
        try:
            # Convert PDF page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Enhance image for OCR
            img = self._enhance_image_for_ocr(img)
            
            # Perform OCR
            text = pytesseract.image_to_string(img, config=self.tesseract_config)
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF page OCR failed: {e}")
            raise
    
    async def _process_image(self, file_path: str) -> DocumentProcessingResult:
        """Process image file using OCR with fallback handling"""
        try:
            if not self.tesseract_available:
                return DocumentProcessingResult(
                    success=False,
                    error_message="OCR not available. Please install Tesseract to process images.",
                    processing_notes=["Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract"]
                )
            
            logger.info(f"Processing image with OCR: {Path(file_path).name}")
            
            # Open and validate image
            img = Image.open(file_path)
            original_size = img.size
            
            # Enhance image for better OCR results
            enhanced_img = self._enhance_image_for_ocr(img)
            
            # Extract text using Tesseract OCR
            extracted_text = pytesseract.image_to_string(enhanced_img, config=self.tesseract_config)
            
            if not extracted_text.strip():
                # Try with different OCR settings
                logger.warning("No text extracted with default settings, trying alternative OCR config...")
                alt_config = '--psm 3'  # Different page segmentation mode
                extracted_text = pytesseract.image_to_string(enhanced_img, config=alt_config)
            
            if not extracted_text.strip():
                logger.warning("No text extracted from image")
                extracted_text = "[No text could be extracted from this image. Try improving image quality or contrast.]"
                processing_notes = [
                    "No text detected in image",
                    "Tips: Ensure text is clear, high contrast, and properly oriented"
                ]
            else:
                processing_notes = [f"OCR processed image: {original_size[0]}x{original_size[1]}px"]
            
            word_count = len(extracted_text.split())
            
            return DocumentProcessingResult(
                success=True,
                extracted_text=extracted_text.strip(),
                total_pages=1,
                word_count=word_count,
                processing_notes=processing_notes
            )
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
    
    def _enhance_image_for_ocr(self, img: Image.Image) -> Image.Image:
        """Enhanced image preprocessing for better OCR results"""
        try:
            # Convert to grayscale if not already
            if img.mode != 'L':
                img = img.convert('L')
            
            # Resize if too small (OCR works better with larger text)
            width, height = img.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Denoise
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Apply threshold to create high contrast black and white image
            img_array = np.array(img)
            threshold = np.mean(img_array) * 0.9  # Adaptive threshold
            img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
            img = Image.fromarray(img_array)
            
            return img
            
        except Exception as e:
            logger.warning(f"Image enhancement failed, using original: {e}")
            return img
    
    def get_supported_formats(self) -> dict:
        """Return information about supported file formats"""
        return {
            "pdf": {
                "extensions": list(self.supported_pdf_extensions),
                "max_pages": self.max_pdf_pages,
                "description": "PDF documents with text extraction and OCR fallback"
            },
            "images": {
                "extensions": list(self.supported_image_extensions),
                "max_dimension": f"{self.max_image_dimension}px",
                "description": "Images processed with OCR",
                "ocr_available": self.tesseract_available,
                "ocr_note": "Install Tesseract OCR for image processing" if not self.tesseract_available else None
            },
            "limits": {
                "max_file_size": self.max_file_size // (1024*1024),
                "tesseract_available": self.tesseract_available
            }
        }