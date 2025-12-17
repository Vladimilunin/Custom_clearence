"""
Integration tests for the Invoices API endpoints.
Uses real Groq API calls for invoice parsing.
"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestUploadInvoiceEndpoint:
    """Tests for /api/v1/invoices/upload endpoint."""
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Get sample PDF content for testing."""
        # Minimal valid PDF
        return b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF'
    
    @pytest.fixture
    def real_pdf_path(self):
        """Get path to real PDF for integration testing."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        pdf_files = [
            os.path.join(base_dir, "3_PI For Алексей Семенов- 20241225.pdf"),
            os.path.join(base_dir, "PI PTJ20251023B1.pdf"),
        ]
        
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):
                return pdf_path
        
        return None
    
    def test_upload_validates_pdf_format(self, client):
        """Test that non-PDF files are rejected."""
        # Create fake PDF with wrong extension
        fake_content = b"Not a PDF"
        
        response = client.post(
            "/api/v1/invoices/upload",
            files={"file": ("test.pdf", fake_content, "application/pdf")},
            data={"method": "groq"}
        )
        
        assert response.status_code == 400
        assert "not a valid PDF" in response.json()["detail"]
    
    def test_upload_validates_extension(self, client):
        """Test that non-PDF extensions are rejected."""
        pdf_content = b'%PDF-1.4\ntest'
        
        response = client.post(
            "/api/v1/invoices/upload",
            files={"file": ("test.docx", pdf_content, "application/pdf")},
            data={"method": "groq"}
        )
        
        assert response.status_code == 400
        assert "Invalid extension" in response.json()["detail"]
    
    @pytest.mark.integration
    def test_upload_real_pdf(self, client, real_pdf_path):
        """Integration test: Upload real PDF and parse with Groq."""
        if real_pdf_path is None:
            pytest.skip("No real PDF found for integration test")
        
        with open(real_pdf_path, "rb") as f:
            pdf_content = f.read()
        
        response = client.post(
            "/api/v1/invoices/upload",
            files={"file": (os.path.basename(real_pdf_path), pdf_content, "application/pdf")},
            data={"method": "groq"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "debug_info" in data
        assert isinstance(data["items"], list)


class TestDebugUploadEndpoint:
    """Tests for /api/v1/invoices/debug_upload endpoint."""
    
    def test_path_traversal_blocked(self, client):
        """Test that path traversal attempts are blocked."""
        response = client.post(
            "/api/v1/invoices/debug_upload",
            json={"file_path": "../../../etc/passwd", "method": "groq"}
        )
        
        # Should be rejected at validation level
        assert response.status_code in [400, 422]
    
    def test_nonexistent_file(self, client):
        """Test handling of non-existent file."""
        response = client.post(
            "/api/v1/invoices/debug_upload",
            json={"file_path": "/nonexistent/path/file.pdf", "method": "groq"}
        )
        
        # Could be 400 (validation) or 404 (not found)
        assert response.status_code in [400, 404]


class TestGenerateReportEndpoint:
    """Tests for /api/v1/invoices/generate endpoint."""
    
    def test_generate_tech_description(self, client):
        """Test generating technical description document."""
        request_data = {
            "items": [
                {
                    "designation": "TEST-001",
                    "name": "Test Part",
                    "material": "Steel",
                    "weight": 1.5,
                    "dimensions": "100x50x25",
                    "description": "Test description",
                    "found_in_db": False,
                    "image_path": None
                }
            ],
            "country_of_origin": "Китай",
            "supplier": "Test Supplier",
            "gen_tech_desc": True,
            "gen_non_insurance": False,
            "gen_decision_130": False
        }
        
        response = client.post("/api/v1/invoices/generate", json=request_data)
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    def test_generate_multiple_documents(self, client):
        """Test generating multiple documents (returns ZIP)."""
        request_data = {
            "items": [
                {
                    "designation": "TEST-001",
                    "name": "Test Part",
                    "material": "Steel",
                    "weight": 1.5,
                    "dimensions": "100x50x25",
                    "found_in_db": False,
                    "image_path": None
                }
            ],
            "gen_tech_desc": True,
            "gen_non_insurance": True,
            "gen_decision_130": True
        }
        
        response = client.post("/api/v1/invoices/generate", json=request_data)
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/zip"
    
    def test_generate_no_documents_selected(self, client):
        """Test error when no documents are selected."""
        request_data = {
            "items": [{"designation": "TEST-001", "name": "Test", "found_in_db": False, "image_path": None}],
            "gen_tech_desc": False,
            "gen_non_insurance": False,
            "gen_decision_130": False
        }
        
        response = client.post("/api/v1/invoices/generate", json=request_data)
        
        assert response.status_code == 400
        assert "No documents selected" in response.json()["detail"]
    
    def test_generate_empty_items(self, client):
        """Test generating with empty items list."""
        request_data = {
            "items": [],
            "gen_tech_desc": True
        }
        
        response = client.post("/api/v1/invoices/generate", json=request_data)
        
        # Should either succeed with empty document or return validation error
        assert response.status_code in [200, 400, 422]
    
    def test_generate_with_facsimile(self, client):
        """Test generating with facsimile (stamp and signature)."""
        request_data = {
            "items": [
                {
                    "designation": "TEST-001",
                    "name": "Test Part",
                    "found_in_db": False,
                    "image_path": None
                }
            ],
            "gen_tech_desc": True,
            "add_facsimile": True
        }
        
        response = client.post("/api/v1/invoices/generate", json=request_data)
        
        assert response.status_code == 200


class TestHealthAndRoot:
    """Tests for health check and root endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns hello world."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
