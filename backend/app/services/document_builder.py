"""
Document builder utilities for DOCX generation.

This module provides helper classes and functions for building
Word documents with consistent formatting.
"""
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os
from datetime import datetime
from typing import Optional, List, Any
from dataclasses import dataclass, field


@dataclass
class DocumentStyle:
    """Document styling configuration."""
    font_name: str = 'Times New Roman'
    font_size: int = 12
    bold: bool = False
    color: Optional[RGBColor] = None


@dataclass  
class PartInfo:
    """Internal representation of a part for document generation."""
    designation: str
    name: str = ""
    material: str = ""
    weight: float = 0.0
    weight_unit: str = "кг"
    dimensions: str = ""
    description: str = ""
    image_path: Optional[str] = None
    component_type: str = ""
    manufacturer: str = ""
    
    # Electronics specific
    is_electronics: bool = False
    tnved_code: str = ""
    tnved_description: str = ""
    input_voltage: str = ""
    input_current: str = ""
    processor: str = ""
    ram_kb: int = 0
    rom_mb: int = 0
    current_type: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PartInfo':
        """Create PartInfo from dictionary."""
        return cls(
            designation=data.get('designation', ''),
            name=data.get('name', ''),
            material=data.get('material', ''),
            weight=float(data.get('weight', 0) or 0),
            weight_unit=data.get('weight_unit', 'кг'),
            dimensions=data.get('dimensions', ''),
            description=data.get('description', ''),
            image_path=data.get('image_path'),
            component_type=data.get('component_type', ''),
            manufacturer=data.get('manufacturer', ''),
            is_electronics=data.get('component_type', '').lower() == 'electronics',
            tnved_code=data.get('tnved_code', ''),
            tnved_description=data.get('tnved_description', ''),
            input_voltage=data.get('input_voltage', ''),
            input_current=data.get('input_current', ''),
            processor=data.get('processor', ''),
            ram_kb=int(data.get('ram_kb', 0) or 0),
            rom_mb=int(data.get('rom_mb', 0) or 0),
            current_type=data.get('current_type', ''),
        )
    
    @classmethod
    def from_model(cls, part: Any) -> 'PartInfo':
        """Create PartInfo from database model."""
        return cls(
            designation=getattr(part, 'designation', ''),
            name=getattr(part, 'name', ''),
            material=getattr(part, 'material', ''),
            weight=float(getattr(part, 'weight', 0) or 0),
            weight_unit=getattr(part, 'weight_unit', 'кг') or 'кг',
            dimensions=getattr(part, 'dimensions', ''),
            description=getattr(part, 'description', ''),
            image_path=getattr(part, 'image_path', None),
            component_type=getattr(part, 'component_type', ''),
            manufacturer=getattr(part, 'manufacturer', ''),
            is_electronics=str(getattr(part, 'component_type', '')).lower() == 'electronics',
            tnved_code=getattr(part, 'tnved_code', ''),
            tnved_description=getattr(part, 'tnved_description', ''),
            input_voltage=getattr(part, 'input_voltage', ''),
            input_current=getattr(part, 'input_current', ''),
            processor=getattr(part, 'processor', ''),
            ram_kb=int(getattr(part, 'ram_kb', 0) or 0),
            rom_mb=int(getattr(part, 'rom_mb', 0) or 0),
            current_type=getattr(part, 'current_type', ''),
        )


class FontHelper:
    """Helper class for font formatting."""
    
    @staticmethod
    def set_font(
        run, 
        font_name: str = 'Times New Roman', 
        font_size: int = 12, 
        bold: bool = False, 
        color: Optional[RGBColor] = None
    ):
        """Apply font settings to a run."""
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.bold = bold
        if color:
            run.font.color.rgb = color
    
    @staticmethod
    def apply_style(run, style: DocumentStyle):
        """Apply DocumentStyle to a run."""
        FontHelper.set_font(
            run, 
            font_name=style.font_name,
            font_size=style.font_size,
            bold=style.bold,
            color=style.color
        )


class TableHelper:
    """Helper class for table manipulation."""
    
    @staticmethod
    def remove_borders(table):
        """Remove all borders from a table."""
        tbl = table._tbl
        tblPr = tbl.tblPr
        tblBorders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'nil')
            tblBorders.append(border)
        tblPr.append(tblBorders)
    
    @staticmethod
    def set_cell_padding(cell, padding_pt: int = 1):
        """Set cell padding in points."""
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        # Convert points to twentieths of a point
        twips = padding_pt * 20
        for side in ['top', 'bottom', 'left', 'right']:
            node = OxmlElement(f'w:{side}')
            node.set(qn('w:w'), str(twips))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)
    
    @staticmethod
    def set_row_cant_split(row):
        """Prevent row from splitting across pages."""
        trPr = row._tr.get_or_add_trPr()
        cantSplit = OxmlElement('w:cantSplit')
        trPr.append(cantSplit)
    
    @staticmethod
    def set_column_widths(table, widths_cm: List[float]):
        """Set column widths in centimeters."""
        for i, width in enumerate(widths_cm):
            if i < len(table.columns):
                table.columns[i].width = Cm(width)


class ImageHelper:
    """Helper class for image handling."""
    
    @staticmethod
    def find_image_path(relative_path: str) -> Optional[str]:
        """Find absolute path for an image, checking multiple locations."""
        if not relative_path:
            return None
            
        # Direct path
        if os.path.exists(relative_path):
            return relative_path
        
        # Docker path
        docker_path = f"/app/{relative_path}"
        if os.path.exists(docker_path):
            return docker_path
        
        # Relative to backend
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        local_path = os.path.join(base_dir, relative_path)
        if os.path.exists(local_path):
            return local_path
        
        return None
    
    @staticmethod
    def add_float_picture(run, image_path: str, width, pos_x: int, pos_y: int):
        """
        Insert a floating image (In Front of Text) anchored to the paragraph.
        pos_x, pos_y: offsets in EMUs from the anchor point.
        """
        # Add the picture normally first to get the relationship ID
        inline = run.add_picture(image_path, width=width)._inline
        
        # Get the graphic object
        graphic = inline.graphic
        
        # Create the anchor element
        anchor = OxmlElement('wp:anchor')
        anchor.set('distT', "0")
        anchor.set('distB', "0")
        anchor.set('distL', "114300")
        anchor.set('distR', "114300")
        anchor.set('simplePos', "0")
        anchor.set('relativeHeight', "251658240")
        anchor.set('behindDoc', "0")
        anchor.set('locked', "0")
        anchor.set('layoutInCell', "1")
        anchor.set('allowOverlap', "1")
        
        # Simple Positioning
        simplePos = OxmlElement('wp:simplePos')
        simplePos.set('x', "0")
        simplePos.set('y', "0")
        anchor.append(simplePos)
        
        # Horizontal Position
        positionH = OxmlElement('wp:positionH')
        positionH.set('relativeFrom', "column")
        posOffsetH = OxmlElement('wp:posOffset')
        posOffsetH.text = str(pos_x)
        positionH.append(posOffsetH)
        anchor.append(positionH)
        
        # Vertical Position
        positionV = OxmlElement('wp:positionV')
        positionV.set('relativeFrom', "paragraph")
        posOffsetV = OxmlElement('wp:posOffset')
        posOffsetV.text = str(pos_y)
        positionV.append(posOffsetV)
        anchor.append(positionV)
        
        # Extent (Size)
        extent = OxmlElement('wp:extent')
        extent.set('cx', str(inline.extent.cx))
        extent.set('cy', str(inline.extent.cy))
        anchor.append(extent)
        
        # Wrap None (In Front of Text behavior)
        wrapNone = OxmlElement('wp:wrapNone')
        anchor.append(wrapNone)
        
        # DocPr
        docPr = OxmlElement('wp:docPr')
        docPr.set('id', '666')
        docPr.set('name', 'Floating Image')
        anchor.append(docPr)
        
        # Graphic
        anchor.append(graphic)
        
        # Replace inline with anchor
        inline.getparent().replace(inline, anchor)
        return anchor


class PageNumberHelper:
    """Helper for adding page numbers."""
    
    @staticmethod
    def add_page_number(paragraph):
        """Add page number field to a paragraph."""
        run = paragraph.add_run()
        
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar1)
        
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        run._r.append(instrText)
        
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar2)
