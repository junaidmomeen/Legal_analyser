from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request, status, Depends
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
import aiofiles
import aiofiles.os
import hashlib

from services.document_processor import DocumentProcessor
from services.ai_analyzer import AIAnalyzer
from services.report_generator import ReportGenerator
from models.analysis_models import AnalysisResult
from utils.file_validator import FileValidator
from utils.error_handler import error_handler
from middleware.rate_limiter import limiter, analysis_limiter, export_limiter
from middleware.security_headers import SecurityHeadersMiddleware
from slowapi.errors import RateLimitExceeded
from utils.request_guards import enforce_content_length_limit
from services.tasks import celery_app
from services.retention_jobs import get_retention_manager, start_retention_jobs, stop_retention_jobs
from observability import setup_prometheus

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
app.add_middleware(SecurityHeadersMiddleware)
setup_prometheus(app)

# CORS configuration
APP_ENV = os.getenv("APP_ENV", "development")
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]

# In production, ensure that the allowed origins are explicitly set and not the default ones
if APP_ENV == "production" and ("http://localhost:5173" in allowed_origins or "http://localhost:3000" in allowed_origins):
    logger.warning("In production, but ALLOWED_ORIGINS is not set or is using default development values.")

# Configure CORS using ALLOWED_ORIGINS (comma-separated). Default to development-friendly values.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type", "X-Requested-With", "X-Request-ID"],
)

# Initialize services
try:
    document_processor = DocumentProcessor()
    ai_analyzer = AIAnalyzer()
    report_generator = ReportGenerator()
    file_validator = FileValidator()

    # Expose service instances on app.state for health checks and other modules
    app.state.document_processor = document_processor
    app.state.ai_analyzer = ai_analyzer
    app.state.report_generator = report_generator
    app.state.file_validator = file_validator

    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}", exc_info=True, extra={"error_type": "service_initialization"})
    raise

# In-memory cache for analysis results
analysis_cache: Dict[str, Dict[str, Any]] = {}
analysis_lock = asyncio.Lock()
analysis_semaphore = asyncio.Semaphore(MAX_CONCURRENT_ANALYSES)
export_tasks: Dict[str, Dict[str, Any]] = {}

# Expose shared state for routers
app.state.analysis_cache = analysis_cache
app.state.analysis_lock = analysis_lock
app.state.analysis_semaphore = analysis_semaphore
app.state.export_tasks = export_tasks

# Custom exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return error_handler.handle_rate_limit_exceeded(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_handler.handle_validation_error(request, exc)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_handler.handle_http_exception(request, exc)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return error_handler.handle_general_exception(request, exc)

# Initialize retention jobs
async def initialize_retention_jobs():
    """Initialize the retention jobs system"""
    try:
        retention_manager = get_retention_manager()
        
        # Set the analysis cache and lock for the retention manager
        retention_manager.analysis_cache = analysis_cache
        retention_manager.analysis_lock = analysis_lock
        
        # Start retention jobs
        await retention_manager.start()
        logger.info("Retention jobs initialized and started")
        
    except Exception as e:
        logger.error(f"Failed to initialize retention jobs: {e}", exc_info=True)

from routers.system import router as system_router
app.include_router(system_router)

# Startup and shutdown event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_retention_jobs()

# No authentication endpoints; application operates without login

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        retention_manager = get_retention_manager()
        await retention_manager.stop()
        logger.info("Retention jobs stopped during shutdown")
    except Exception as e:
        logger.error(f"Error stopping retention jobs during shutdown: {e}")

@app.post("/analyze")
@analysis_limiter.limit("10/minute")
async def analyze_document(
    request: Request,
    file: UploadFile = File(...),
    _size_guard=Depends(enforce_content_length_limit),
):
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
            # Stream to temp file while hashing to avoid buffering entire file
            file_id = str(uuid.uuid4())
            file_extension = None
            original_filename = file.filename or "unknown_file"
            temp_file_path = None

            hasher = hashlib.sha256()
            size_counter = 0
            chunk_size = 1024 * 1024
            # Need extension to build path after validation; for streaming we hash first
            content_peek = await file.read(1024 * 64)
            await file.seek(0)
            # Validate using peek content
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
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    size_counter += len(chunk)
                    hasher.update(chunk)
                    await buffer.write(chunk)
            file_size = size_counter
            file_hash = hasher.hexdigest()
            
            # Deduplicate by hash
            for existing_id, data in analysis_cache.items():
                if data.get("file_hash") == file_hash:
                    logger.info("Duplicate upload detected, returning cached analysis", extra={"file_id": existing_id})
                    cached = data["analysis"]
                    response_data = cached.copy()
                    response_data.update({
                        "file_id": existing_id,
                        "processing_time": data.get("processing_time", 0),
                        "total_pages": data.get("total_pages", 0),
                        "word_count": data.get("word_count", 0),
                        "processing_notes": data.get("processing_notes", [])
                    })
                    return response_data
            
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
                "analysis": analysis_result.model_dump(),
                "file_path": temp_file_path,
                "original_filename": original_filename,
                "content_type": file.content_type,
                "timestamp": datetime.now(),
                "processing_time": processing_time,
                "file_size": file_size,
                "processing_notes": getattr(processing_result, 'processing_notes', []) or [],
                "file_hash": file_hash
            }
            
            logger.info(f"Analysis completed successfully", extra={
                "file_id": file_id,
                "total_processing_time": processing_time,
                "confidence": analysis_result.confidence,
                "clauses_found": len(analysis_result.key_clauses),
                "request_id": request_id
            })
            
            response_data = analysis_result.model_dump()
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

@app.delete("/analyses")
async def clear_analyses(request: Request):
    request_id = request.state.request_id
    logger.info("Clear analyses request received", extra={"request_id": request_id})
    
    async with analysis_lock:
        cleared_count = len(analysis_cache)
        # Create a copy of the dictionary items to avoid a race condition
        for file_id, data in list(analysis_cache.items()):
            try:
                file_path = data.get('file_path')
                if file_path:
                    try:
                        await aiofiles.os.stat(file_path)
                        await aiofiles.os.remove(file_path)
                    except FileNotFoundError:
                        pass
            except Exception as e:
                logger.error(f"Error cleaning up file {file_id}: {e}", 
                           extra={"error_type": "cleanup_error", "file_id": file_id})
        
        analysis_cache.clear()
        export_tasks.clear()

    logger.info(f"All analyses cleared: {cleared_count} items removed", 
               extra={"cleared_count": cleared_count, "request_id": request_id})
    
    return {"message": f"Successfully cleared {cleared_count} analysis records."}


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

    if celery_app:
        # Defer to Celery task
        celery_app.send_task(
            "backend.tasks.run_export_task",
            args=[file_id, format, task_id],
        )
    else:
        background_tasks.add_task(run_export, file_id, format, task_id)
    
    return {"task_id": task_id, "status": "processing"}

@app.get("/export/{task_id}")
async def get_export_status(task_id: str,):
    if task_id not in export_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export task not found"
        )
    
    task = export_tasks[task_id]
    
    if task["status"] == "completed":
        return {"status": "ready"}
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


@app.get("/export/{task_id}/download")
async def download_export(task_id: str):
    if task_id not in export_tasks:
        raise HTTPException(status_code=404, detail="Export task not found")
    task = export_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Export not ready")
    return FileResponse(
        path=task["file_path"],
        media_type="application/octet-stream",
        filename=os.path.basename(task["file_path"]) 
    )

if __name__ == "__main__":
    # This block is crucial for Windows compatibility when using --reload
    # It ensures that the Uvicorn server is only started when the script is executed directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)