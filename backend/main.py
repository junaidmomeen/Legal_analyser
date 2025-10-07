from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
import uvicorn
from typing import Dict, Any, Optional
import os
import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid
import shutil
import asyncio
from pathlib import Path
import aiofiles.os

from services.document_processor import DocumentProcessor
from services.ai_analyzer import AIAnalyzer
from services.report_generator import ReportGenerator
from models.analysis_models import AnalysisResult
from utils.file_validator import FileValidator
from middleware.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# API Version
API_VERSION = "1.1.0"

# Configure structured logging
def setup_logging():
    """Setup structured logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json")  # json or text

    if log_format.lower() == "json":
        import sys

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                    "request_id": getattr(record, "request_id", None),
                }

                # Add extra fields if present
                for attr in ['user_id', 'file_id', 'processing_time', 'error_type', 'uploaded_filename']:
                    if hasattr(record, attr):
                        log_entry[attr] = getattr(record, attr)

                return json.dumps(log_entry)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
    else:
        log_format_str = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_format_str))

    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=[handler],
        force=True
    )

    log_file = os.path.join("logs", "backend.log")
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(handler.formatter)
    logging.getLogger().addHandler(file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger(__name__)

logger = setup_logging()

# Configuration
TEMP_STORAGE_PATH = os.getenv("TEMP_STORAGE_PATH", "temp_uploads")
CLEANUP_INTERVAL = int(os.getenv("CLEANUP_INTERVAL_HOURS", "1"))
CACHE_RETENTION_HOURS = int(os.getenv("CACHE_RETENTION_HOURS", "24"))
MAX_CONCURRENT_ANALYSES = int(os.getenv("MAX_CONCURRENT_ANALYSES", "5"))

# Create directories
Path(TEMP_STORAGE_PATH).mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Document Analyzer API",
    description="AI-powered legal document analysis and clause extraction with comprehensive reporting",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

app.add_middleware(RequestIDMiddleware)

# CORS configuration
APP_ENV = os.getenv("APP_ENV", "development")
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]

# In production, ensure that the allowed origins are explicitly set and not the default ones
if APP_ENV == "production" and ("http://localhost:5173" in allowed_origins or "http://localhost:3000" in allowed_origins):
    logger.warning("In production, but ALLOWED_ORIGINS is not set or is using default development values.")

# Define allowed headers
allowed_headers = [
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-Request-ID",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=allowed_headers,
)

# Initialize services
try:
    document_processor = DocumentProcessor()
    ai_analyzer = AIAnalyzer()
    report_generator = ReportGenerator()
    file_validator = FileValidator()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}", exc_info=True, extra={"error_type": "service_initialization"})
    raise

# In-memory cache for analysis results
analysis_cache: Dict[str, Dict[str, Any]] = {}
analysis_lock = asyncio.Lock()
analysis_semaphore = asyncio.Semaphore(MAX_CONCURRENT_ANALYSES)
export_tasks: Dict[str, Dict[str, Any]] = {}

# Custom exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded", "message": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    logger.warning(f"Validation error for {request.url}: {exc.errors()}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors(),
            "request_id": request_id
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"HTTP exception for {request.url}: {exc.detail}", 
                extra={"error_type": "http_exception", "status_code": exc.status_code, "request_id": request_id})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request Failed",
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled exception for {request.url}", exc_info=True, 
                extra={"error_type": "unhandled_exception", "request_id": request_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request_id
        }
    )

# Background task for cleanup
async def cleanup_old_files():
    """Background task to clean up old files and analyses"""
    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL * 3600)
            logger.info("Starting cleanup task")
            cleanup_count = 0
            now = datetime.now()
            cutoff_time = now - timedelta(hours=CACHE_RETENTION_HOURS)
            
            # Create a copy of the dictionary items to avoid a race condition
            for file_id, data in list(analysis_cache.items()):
                try:
                    if data['timestamp'] < cutoff_time:
                        file_path = data.get('file_path')
                        if file_path:
                            try:
                                await aiofiles.os.stat(file_path)
                                await aiofiles.os.remove(file_path)
                            except FileNotFoundError:
                                pass
                        del analysis_cache[file_id]
                        cleanup_count += 1
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_id}: {e}", 
                               extra={"error_type": "cleanup_error", "file_id": file_id})
            
            logger.info(f"Cleanup completed: {cleanup_count} files removed", 
                       extra={"cleanup_count": cleanup_count})
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}", exc_info=True, extra={"error_type": "cleanup_task_error"})

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    request_id = request.state.request_id
    logger.info("Health check requested", extra={"request_id": request_id})
    try:
        services_status = {
            "document_processor": "healthy",
            "ai_analyzer": "healthy", 
            "report_generator": "healthy",
            "tesseract_ocr": document_processor.tesseract_available
        }
        try:
            disk_usage = shutil.disk_usage(TEMP_STORAGE_PATH)
            free_space_gb = disk_usage.free / (1024**3)
            services_status["disk_space_gb"] = round(free_space_gb, 2)
        except:
            services_status["disk_space_gb"] = "unknown"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "cache_size": len(analysis_cache),
            "active_analyses": MAX_CONCURRENT_ANALYSES - analysis_semaphore._value,
            "services": services_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True, extra={"request_id": request_id})
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Service Unavailable",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/")
async def root(request: Request):
    request_id = request.state.request_id
    logger.info("Root endpoint requested", extra={"request_id": request_id})
    return {
        "name": "Legal Document Analyzer API",
        "version": API_VERSION,
        "description": "AI-powered legal document analysis with comprehensive reporting",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "export": "/export/{file_id}/{format}",
            "supported_formats": "/supported-formats",
            "docs": "/docs"
        }
    }

# ---- FIXED: Add supported-formats endpoint below ----
@app.get("/supported-formats")
async def get_supported_formats():
    return {
        "formats": ["PDF", "PNG", "JPG", "JPEG", "GIF", "BMP", "TIFF", "WEBP"]
    }
# ---- (nothing else changed here) ----

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_document(request: Request, file: UploadFile = File(...)):
    request_id = request.state.request_id
    start_time = datetime.now()
    
    logger.info(f"Analysis request received", extra={
        "request_id": request_id,
        "uploaded_filename": file.filename,
        "content_type": file.content_type,
        "file_size": getattr(file, 'size', 'unknown')
    })
    
    async with analysis_semaphore:
        file_id = str(uuid.uuid4())
        file_extension = None
        original_filename = file.filename or "unknown_file"
        temp_file_path = None
        
        try:
            file_content = await file.read()
            file_size = len(file_content)
            await file.seek(0)
            
            validation_result = await file_validator.validate_file(file)
            if not validation_result.is_valid:
                logger.warning(f"File validation failed: {validation_result.error_message}", 
                              extra={"file_id": file_id, "error_type": "validation_error", "request_id": request_id})
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File validation failed: {validation_result.error_message}"
                )
            
            file_extension = validation_result.file_extension
            stored_filename = f"{file_id}.{file_extension}"
            temp_file_path = os.path.join(TEMP_STORAGE_PATH, stored_filename)
            
            async with aiofiles.open(temp_file_path, "wb") as buffer:
                await file.seek(0)
                content = await file.read()
                await buffer.write(content)
            
            logger.info(f"File saved for processing", extra={
                "file_id": file_id,
                "file_path": temp_file_path,
                "file_size": file_size,
                "request_id": request_id
            })
            
            processing_result = await document_processor.process_document(
                temp_file_path, 
                validation_result.file_type
            )
            
            if not processing_result.success:
                logger.error(f"Document processing failed: {processing_result.error_message}", 
                            extra={"file_id": file_id, "error_type": "processing_error", "request_id": request_id})
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Document processing failed: {processing_result.error_message}"
                )
            
            logger.info(f"Document processed successfully", extra={
                "file_id": file_id,
                "processing_time": processing_result.processing_time,
                "word_count": processing_result.word_count,
                "total_pages": processing_result.total_pages,
                "request_id": request_id
            })
            
            analysis_result = await ai_analyzer.analyze_document(
                text=processing_result.extracted_text,
                document_type=validation_result.file_type,
                filename=original_filename
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            analysis_cache[file_id] = {
                "analysis": analysis_result.dict(),
                "file_path": temp_file_path,
                "original_filename": original_filename,
                "content_type": file.content_type,
                "timestamp": datetime.now(),
                "processing_time": processing_time,
                "file_size": file_size,
                "processing_notes": getattr(processing_result, 'processing_notes', []) or []
            }
            
            logger.info(f"Analysis completed successfully", extra={
                "file_id": file_id,
                "total_processing_time": processing_time,
                "confidence": analysis_result.confidence,
                "clauses_found": len(analysis_result.key_clauses),
                "request_id": request_id
            })
            
            response_data = analysis_result.dict()
            response_data.update({
                "file_id": file_id,
                "processing_time": processing_time,
                "total_pages": processing_result.total_pages,
                "word_count": processing_result.word_count,
                "processing_notes": getattr(processing_result, 'processing_notes', []) or []
            })
            
            return response_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Analysis failed with unexpected error: {str(e)}", exc_info=True, extra={
                "file_id": file_id,
                "error_type": "analysis_error",
                "request_id": request_id
            })
            if temp_file_path:
                try:
                    await aiofiles.os.stat(temp_file_path)
                    await aiofiles.os.remove(temp_file_path)
                except FileNotFoundError:
                    pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {str(e)}"
            )

@app.get("/analysis/{file_id}")
async def get_analysis(file_id: str):
    if file_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_cache[file_id]["analysis"]

@app.get("/stats")
async def get_stats():
    return {
        "analysis_cache_size": len(analysis_cache),
        "export_tasks_size": len(export_tasks),
        "max_concurrent_analyses": MAX_CONCURRENT_ANALYSES,
        "active_analyses": MAX_CONCURRENT_ANALYSES - analysis_semaphore._value,
    }

@app.get("/documents/{file_id}")
async def get_document(file_id: str):
    try:
        # Validate that file_id is a legitimate UUID
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file_id format")

    if file_id not in analysis_cache:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or expired")

    file_path_str = analysis_cache[file_id].get("file_path")
    if not file_path_str:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File path not found in cache")

    # Security: Prevent path traversal attacks
    try:
        # Resolve the absolute path and ensure it's within the designated temporary storage
        temp_storage_abs_path = Path(TEMP_STORAGE_PATH).resolve()
        resolved_path = Path(file_path_str).resolve()
        
        if not resolved_path.is_relative_to(temp_storage_abs_path):
            logger.warning(f"Path traversal attempt detected for file_id: {file_id}", extra={"file_id": file_id})
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this resource is forbidden")
            
    except (ValueError, TypeError):
        logger.error(f"Invalid file path encountered for file_id: {file_id}", extra={"file_id": file_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid file path")


    original_filename = analysis_cache[file_id].get("original_filename", "downloaded_file")

    try:
        await aiofiles.os.stat(resolved_path)
    except FileNotFoundError:
        logger.warning(f"Document file not found on disk for file_id: {file_id}", extra={"file_id": file_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original document file not found on disk")

    return FileResponse(path=resolved_path, filename=original_filename)

async def run_export(file_id: str, format: str, task_id: str):
    cached_data = analysis_cache[file_id]
    analysis = cached_data['analysis']
    original_filename = cached_data['original_filename'].rsplit('.', 1)[0]
    
    try:
        if format.lower() == 'json':
            file_path = report_generator.export_as_json(analysis, original_filename)
        else:  # pdf
            file_path = report_generator.export_as_pdf(analysis, original_filename)
        
        export_tasks[task_id]["status"] = "completed"
        export_tasks[task_id]["file_path"] = file_path
            
    except Exception as e:
        export_tasks[task_id]["status"] = "failed"
        logger.error(f"Export failed: {str(e)}", exc_info=True, extra={
            "file_id": file_id,
            "format": format,
            "error_type": "export_error"
        })

@app.post("/export/{file_id}/{format}")
async def export_analysis(file_id: str, format: str, background_tasks: BackgroundTasks):
    if file_id not in analysis_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or expired"
        )
    
    if format.lower() not in ['json', 'pdf']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Use 'json' or 'pdf'"
        )
    
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = {"status": "processing", "file_path": None}
    
    background_tasks.add_task(run_export, file_id, format, task_id)
    
    return {"task_id": task_id, "status": "processing"}

@app.get("/export/{task_id}")
async def get_export_status(task_id: str):
    if task_id not in export_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export task not found"
        )
    
    task = export_tasks[task_id]
    
    if task["status"] == "completed":
        return FileResponse(
            path=task["file_path"],
            media_type="application/octet-stream",
            filename=os.path.basename(task["file_path"])
        )
    elif task["status"] == "failed":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Export Failed",
                "message": "The export task failed. Please try again later."
            }
        )
    else:
        return {"status": task["status"]}

if __name__ == "__main__":
    # This block is crucial for Windows compatibility when using --reload
    # It ensures that the Uvicorn server is only started when the script is executed directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)