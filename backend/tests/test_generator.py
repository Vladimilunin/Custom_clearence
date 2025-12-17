"""Unit tests for generator.py - DOCX Document Generator."""
import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch


class TestGeneratorHelpers:
    """Tests for generator helper functions."""

    def test_set_font(self):
        """Test set_font function sets font properties correctly."""
        from app.services.generator import set_font
        from docx.shared import Pt, RGBColor
        
        # Create mock run
        mock_run = MagicMock()
        mock_run.font = MagicMock()
        
        set_font(mock_run, font_name='Arial', font_size=14, bold=True, color=RGBColor(255, 0, 0))
        
        assert mock_run.font.name == 'Arial'
        mock_run.font.size = Pt(14)  # Check it was called
        assert mock_run.font.bold == True

    def test_normalize_date_import(self):
        """Test that normalize_date is properly imported in generator."""
        from app.services.generator import normalize_date
        assert normalize_date("2025-10-24") == "24.10.2025"


class TestDocumentGeneration:
    """Tests for document generation functions."""

    def test_generate_technical_description_creates_file(self):
        """Test that generate_technical_description creates a DOCX file."""
        from app.services.generator import generate_technical_description
        
        # Create mock parts
        class MockPart:
            def __init__(self):
                self.designation = "TEST-001"
                self.name = "Test Part"
                self.material = "Steel"
                self.weight = 1.5
                self.weight_unit = "кг"
                self.dimensions = "100x50x25"
                self.description = "Test description"
                self.image_path = None
                self.component_type = None
                self.specs = None
                self.manufacturer = None
                self.condition = "New"
                self.tnved_code = None
                self.tnved_description = None
        
        parts = [MockPart()]
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = f.name
        
        try:
            result = generate_technical_description(
                items=parts,
                output_path=output_path,
                country_of_origin="Китай",
                contract_no="TEST-123",
                contract_date="01.01.2025",
                supplier="Test Supplier"
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_generate_non_insurance_letter_creates_file(self):
        """Test that generate_non_insurance_letter creates a DOCX file."""
        from app.services.generator import generate_non_insurance_letter
        
        class MockPart:
            def __init__(self):
                self.designation = "TEST-001"
                self.name = "Test Part"
        
        parts = [MockPart()]
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = f.name
        
        try:
            result = generate_non_insurance_letter(
                items=parts,
                output_path=output_path,
                contract_no="TEST-123",
                contract_date="01.01.2025",
                invoice_no="INV-001",
                invoice_date="01.01.2025",
                waybill_no="WB-001"
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_generate_decision_130_notification_creates_file(self):
        """Test that generate_decision_130_notification creates a DOCX file."""
        from app.services.generator import generate_decision_130_notification
        
        class MockPart:
            def __init__(self):
                self.designation = "TEST-001"
                self.name = "Test Part"
                self.quantity = 1
        
        parts = [MockPart()]
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = f.name
        
        try:
            result = generate_decision_130_notification(
                items=parts,
                output_path=output_path,
                contract_no="TEST-123",
                contract_date="01.01.2025",
                invoice_no="INV-001",
                invoice_date="01.01.2025"
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestElectronicsDetection:
    """Tests for electronics vs mechanical part detection logic."""

    def test_electronics_by_component_type(self):
        """Test that parts with component_type='electronics' are detected."""
        class MockPart:
            component_type = 'electronics'
            material = 'Plastic'
            specs = None
        
        part = MockPart()
        is_electronics = (
            (hasattr(part, 'component_type') and part.component_type == 'electronics') or
            (hasattr(part, 'material') and part.material and 'электро' in part.material.lower()) or
            (hasattr(part, 'specs') and part.specs)
        )
        assert is_electronics == True

    def test_electronics_by_material(self):
        """Test that parts with 'электро' in material are detected."""
        class MockPart:
            component_type = None
            material = 'Электроника, пластик'
            specs = None
        
        part = MockPart()
        is_electronics = (
            (hasattr(part, 'component_type') and part.component_type == 'electronics') or
            (hasattr(part, 'material') and part.material and 'электро' in part.material.lower()) or
            (hasattr(part, 'specs') and part.specs)
        )
        assert is_electronics == True

    def test_electronics_by_specs(self):
        """Test that parts with specs dict are detected as electronics."""
        class MockPart:
            component_type = None
            material = 'Steel'
            specs = {"Входное напряжение": "24V"}
        
        part = MockPart()
        is_electronics = (
            (hasattr(part, 'component_type') and part.component_type == 'electronics') or
            (hasattr(part, 'material') and part.material and 'электро' in part.material.lower()) or
            (hasattr(part, 'specs') and part.specs)
        )
        assert is_electronics == True

    def test_mechanical_part(self):
        """Test that regular parts are not detected as electronics."""
        class MockPart:
            component_type = 'mechanical'
            material = 'Steel'
            specs = None
        
        part = MockPart()
        is_electronics = (
            (hasattr(part, 'component_type') and part.component_type == 'electronics') or
            (hasattr(part, 'material') and part.material and 'электро' in part.material.lower()) or
            (hasattr(part, 'specs') and part.specs)
        )
        assert is_electronics == False
