import pytest
import io
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from auth import create_token
import os


@pytest.fixture(scope="module")
def test_client():
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key", "JWT_SECRET": "test-secret"}):
        from main import app
        client = TestClient(app)
        yield client


@pytest.fixture
def auth_headers():
    """Generate valid auth headers for testing"""
    token = create_token("test-user")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def invalid_auth_headers():
    """Generate invalid auth headers for testing"""
    return {"Authorization": "Bearer invalid-token"}


def make_dummy_pdf_bytes():
    """Create minimal valid PDF bytes for testing"""
    return (
        b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000120 00000 n \n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n180\n%%EOF\n"
    )


class TestAuthenticationIntegration:
    """Test suite for authentication integration across all protected endpoints"""

    def test_root_endpoint_no_auth_required(self, test_client):
        """Root endpoint should be accessible without authentication"""
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == "Legal Document Analyzer API"

    def test_health_endpoint_no_auth_required(self, test_client):
        """Health endpoint should be accessible without authentication"""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_supported_formats_no_auth_required(self, test_client):
        """Supported formats endpoint should be accessible without authentication"""
        response = test_client.get("/supported-formats")
        assert response.status_code == 200
        assert "formats" in response.json()

    def test_analyze_endpoint_requires_auth(self, test_client):
        """Analyze endpoint should require authentication"""
        files = {"file": ("test.pdf", io.BytesIO(make_dummy_pdf_bytes()), "application/pdf")}
        
        # Test without auth
        response = test_client.post("/analyze", files=files)
        assert response.status_code == 401

    def test_analyze_endpoint_with_valid_auth(self, test_client, auth_headers):
        """Analyze endpoint should work with valid authentication"""
        from models.analysis_models import AnalysisResult, KeyClause
        
        dummy_result = AnalysisResult(
            summary="Test summary",
            key_clauses=[
                KeyClause(
                    type="Payment",
                    content="Pay X",
                    importance="high",
                    classification="Financial",
                    risk_score=7.0,
                    page=1,
                    confidence=0.9,
                )
            ],
            document_type="Contract",
            confidence=0.8,
        )

        with patch("utils.file_validator.magic.from_buffer", return_value="application/pdf"):
            from main import ai_analyzer
            ai_analyzer.analyze_document = AsyncMock(return_value=dummy_result)

            files = {"file": ("test.pdf", io.BytesIO(make_dummy_pdf_bytes()), "application/pdf")}
            response = test_client.post("/analyze", files=files, headers=auth_headers)

        assert response.status_code == 200

    def test_analyze_endpoint_with_invalid_auth(self, test_client, invalid_auth_headers):
        """Analyze endpoint should reject invalid authentication"""
        files = {"file": ("test.pdf", io.BytesIO(make_dummy_pdf_bytes()), "application/pdf")}
        response = test_client.post("/analyze", files=files, headers=invalid_auth_headers)
        assert response.status_code == 401

    def test_get_analysis_requires_auth(self, test_client):
        """Get analysis endpoint should require authentication"""
        response = test_client.get("/analysis/non-existent-id")
        assert response.status_code == 401

    def test_get_stats_requires_auth(self, test_client):
        """Get stats endpoint should require authentication"""
        response = test_client.get("/stats")
        assert response.status_code == 401

    def test_get_stats_with_valid_auth(self, test_client, auth_headers):
        """Get stats endpoint should work with valid authentication"""
        response = test_client.get("/stats", headers=auth_headers)
        assert response.status_code == 200
        assert "analysis_cache_size" in response.json()

    def test_clear_analyses_requires_auth(self, test_client):
        """Clear analyses endpoint should require authentication"""
        response = test_client.delete("/analyses")
        assert response.status_code == 401

    def test_clear_analyses_with_valid_auth(self, test_client, auth_headers):
        """Clear analyses endpoint should work with valid authentication"""
        response = test_client.delete("/analyses", headers=auth_headers)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_get_document_requires_auth(self, test_client):
        """Get document endpoint should require authentication"""
        response = test_client.get("/documents/non-existent-id")
        assert response.status_code == 401

    def test_export_analysis_requires_auth(self, test_client):
        """Export analysis endpoint should require authentication"""
        response = test_client.post("/export/non-existent-id/json")
        assert response.status_code == 401

    def test_get_export_status_requires_auth(self, test_client):
        """Get export status endpoint should require authentication"""
        response = test_client.get("/export/non-existent-task-id")
        assert response.status_code == 401

    def test_download_export_no_auth_required(self, test_client):
        """Download export endpoint uses signed URLs, not Bearer auth"""
        response = test_client.get("/export/non-existent-task-id/download?token=invalid")
        # Should return 404 for non-existent task, not 401 for auth failure
        assert response.status_code == 404

    def test_all_protected_endpoints_reject_invalid_auth(self, test_client, invalid_auth_headers):
        """All protected endpoints should reject invalid authentication"""
        protected_endpoints = [
            ("GET", "/analysis/test-id"),
            ("GET", "/stats"),
            ("DELETE", "/analyses"),
            ("GET", "/documents/test-id"),
            ("POST", "/export/test-id/json"),
            ("GET", "/export/test-task-id"),
        ]
        
        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = test_client.get(endpoint, headers=invalid_auth_headers)
            elif method == "POST":
                response = test_client.post(endpoint, headers=invalid_auth_headers)
            elif method == "DELETE":
                response = test_client.delete(endpoint, headers=invalid_auth_headers)
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require valid auth"

    def test_auth_token_expiration(self, test_client):
        """Test that expired tokens are rejected"""
        # Create a token that expires in 1 second
        expired_token = create_token("test-user", expires_in_seconds=1)
        import time
        time.sleep(2)  # Wait for token to expire
        
        files = {"file": ("test.pdf", io.BytesIO(make_dummy_pdf_bytes()), "application/pdf")}
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = test_client.post("/analyze", files=files, headers=headers)
        assert response.status_code == 401

    def test_malformed_auth_header(self, test_client):
        """Test that malformed auth headers are rejected"""
        malformed_headers = [
            {"Authorization": "InvalidFormat token"},
            {"Authorization": "Bearer"},
            {"Authorization": ""},
            {},  # No auth header
        ]
        
        files = {"file": ("test.pdf", io.BytesIO(make_dummy_pdf_bytes()), "application/pdf")}
        
        for headers in malformed_headers:
            response = test_client.post("/analyze", files=files, headers=headers)
            assert response.status_code == 401, f"Should reject malformed auth: {headers}"

    def test_retention_status_requires_auth(self, test_client):
        """Test that retention status endpoint requires authentication"""
        response = test_client.get("/retention/status")
        assert response.status_code == 401

    def test_retention_status_with_valid_auth(self, test_client, auth_headers):
        """Test that retention status endpoint works with valid authentication"""
        response = test_client.get("/retention/status", headers=auth_headers)
        assert response.status_code == 200
        assert "running" in response.json()
        assert "config" in response.json()

    def test_retention_cleanup_requires_auth(self, test_client):
        """Test that retention cleanup endpoint requires authentication"""
        response = test_client.post("/retention/cleanup")
        assert response.status_code == 401

    def test_retention_cleanup_with_valid_auth(self, test_client, auth_headers):
        """Test that retention cleanup endpoint works with valid authentication"""
        response = test_client.post("/retention/cleanup?cleanup_type=all", headers=auth_headers)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_retention_cleanup_invalid_type(self, test_client, auth_headers):
        """Test that retention cleanup rejects invalid cleanup types"""
        response = test_client.post("/retention/cleanup?cleanup_type=invalid", headers=auth_headers)
        assert response.status_code == 400
