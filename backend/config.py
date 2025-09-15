import os
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # API Settings
    API_TITLE: str = "Legal Document Analyzer API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered legal document analysis and clause extraction"
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # File Processing Settings
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    TEMP_DIR: str = "/tmp"
    
    # OCR Settings
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD")
    OCR_LANGUAGE: str = "eng"
    
    # AI Analysis Settings
    MAX_CLAUSES_PER_DOCUMENT: int = 10
    MIN_CLAUSE_LENGTH: int = 50
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # OpenAI Settings (for future AI integration)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Database Settings (for future use)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    @classmethod
    def get_tesseract_cmd(cls) -> Optional[str]:
        """Get Tesseract command path"""
        if cls.TESSERACT_CMD:
            return cls.TESSERACT_CMD
        
        # Try common installation paths
        common_paths = [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None

settings = Settings()
