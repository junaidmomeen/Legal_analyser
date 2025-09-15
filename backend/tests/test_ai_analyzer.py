import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.ai_analyzer import AIAnalyzer
from models.analysis_models import AnalysisResult, KeyClause
import os
import json
import asyncio

@pytest.fixture
def ai_analyzer():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        with patch('google.generativeai.GenerativeModel') as mock_model:
            return AIAnalyzer()

@pytest.mark.asyncio
async def test_analyze_document_success(ai_analyzer):
    mock_response_data = {
        "summary": "This is a test summary.",
        "key_clauses": [
            {
                "type": "Test Clause",
                "content": "This is a test clause.",
                "importance": "high",
                "classification": "Contractual",
                "risk_score": 8.0,
                "page": 1
            }
        ],
        "document_type": "Test Document",
        "total_pages": 1,
        "confidence": 0.9
    }

    mock_gemini_response = MagicMock()
    mock_gemini_response.text = json.dumps(mock_response_data)
    ai_analyzer.model.generate_content.return_value = mock_gemini_response

    result = await ai_analyzer.analyze_document(
        text="This is a test document.",
        document_type="Test Document",
        filename="test.pdf",
        total_pages=1
    )

    assert isinstance(result, AnalysisResult)
    assert result.summary == "This is a test summary."
    assert len(result.key_clauses) == 1
    assert result.key_clauses[0].type == "Test Clause"

@pytest.mark.asyncio
async def test_analyze_document_fallback(ai_analyzer):
    ai_analyzer.model.generate_content.side_effect = Exception("API Error")

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await ai_analyzer.analyze_document(
            text="This is a test document.",
            document_type="Test Document",
            filename="test.pdf",
            total_pages=1
        )
        assert mock_sleep.await_count > 0

    assert isinstance(result, AnalysisResult)
    assert "Analysis failed" in result.summary
    assert len(result.key_clauses) == 1
    assert result.key_clauses[0].type == "Error"