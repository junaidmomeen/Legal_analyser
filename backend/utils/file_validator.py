import os
import magic
from fastapi import UploadFile
from typing import Set
import logging

from models.analysis_models import FileValidationResult
from config import settings

logger = logging.getLogger(__name__)

class FileValidator:
    """Service for validating uploaded files"""
    
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        self.allowed_extensions: Set[str] = set(settings.ALLOWED_EXTENSIONS)
        self.allowed_mime_types: Set[str] = {
            'application/pdf',
            'image/png',
            'image/jpeg',
            'image/tiff',
            'image/bmp'
        }
    
    async def validate_file(self, file: UploadFile) -> FileValidationResult:
        """
        Validate an uploaded file
        
        Args:
            file: The uploaded file to validate
            
        Returns:
            FileValidationResult: Validation result with details
        """
        try:
            if not file.filename:
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension="",
                    file_size=0,
                    error_message="No filename provided"
                )
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension not in self.allowed_extensions:
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=0,
                    error_message=f"File extension '{file_extension}' not allowed. Supported: {', '.join(self.allowed_extensions)}"
                )
            
            content = await file.read()
            file_size = len(content)
            
            await file.seek(0)
            
            if file_size > self.max_file_size:
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=file_size,
                    error_message=f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum allowed size ({self.max_file_size / 1024 / 1024}MB)"
                )
            
            if file_size == 0:
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=file_size,
                    error_message="File is empty"
                )
            
            mime_type = magic.from_buffer(content, mime=True)
            if mime_type not in self.allowed_mime_types:
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=file_size,
                    error_message=f"Invalid file type: {mime_type}. Supported types are: {', '.join(self.allowed_mime_types)}"
                )

            # Check if the extension matches the MIME type
            if file_extension == ".pdf" and mime_type != "application/pdf":
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=file_size,
                    error_message=f"File extension '{file_extension}' does not match MIME type '{mime_type}'"
                )
            
            if file_extension in {".jpg", ".jpeg"} and mime_type != "image/jpeg":
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=file_size,
                    error_message=f"File extension '{file_extension}' does not match MIME type '{mime_type}'"
                )

            if file_extension == ".png" and mime_type != "image/png":
                return FileValidationResult(
                    is_valid=False,
                    file_type="unknown",
                    file_extension=file_extension,
                    file_size=file_size,
                    error_message=f"File extension '{file_extension}' does not match MIME type '{mime_type}'"
                )

            file_type = "pdf" if "pdf" in mime_type else "image"
            
            return FileValidationResult(
                is_valid=True,
                file_type=file_type,
                file_extension=file_extension.lstrip('.'),
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return FileValidationResult(
                is_valid=False,
                file_type="unknown",
                file_extension="",
                file_size=0,
                error_message=f"Validation error: {str(e)}"
            )
    
    def get_max_file_size_mb(self) -> float:
        return self.max_file_size / 1024 / 1024
    
    def get_allowed_extensions(self) -> Set[str]:
        return self.allowed_extensions.copy()

    def get_supported_formats(self) -> dict:
        supported_formats_dict = {
            "pdf": {
                "extensions": [],
                "mime_types": [],
                "max_size_mb": self.get_max_file_size_mb()
            },
            "images": {
                "extensions": [],
                "mime_types": [],
                "max_size_mb": self.get_max_file_size_mb()
            }
        }

        for ext in self.allowed_extensions:
            if ext == ".pdf":
                supported_formats_dict["pdf"]["extensions"].append(ext)
            else:
                supported_formats_dict["images"]["extensions"].append(ext)
        
        for mime in self.allowed_mime_types:
            if "pdf" in mime:
                supported_formats_dict["pdf"]["mime_types"].append(mime)
            elif "image" in mime:
                supported_formats_dict["images"]["mime_types"].append(mime)
                
        return supported_formats_dict