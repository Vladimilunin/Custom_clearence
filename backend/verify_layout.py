import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def verify_docx_layout(docx_path):
    print(f"Verifying layout for: {docx_path}")
    
    if not os.path.exists(docx_path):
        print("Error: File not found.")
        return False

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            # Namespaces
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # 1. Check Page Margins (Section Properties)
            # Usually in the last sectPr or body/sectPr
            sectPr = tree.find('.//w:body/w:sectPr', ns)
            if sectPr is None:
                # Try finding the last pPr/sectPr
                sectPrs = tree.findall('.//w:p/w:pPr/w:sectPr', ns)
                if sectPrs:
                    sectPr = sectPrs[-1]
            
            page_width_dxa = 11906 # A4 width (21cm) in DXA (approx)
            left_margin = 0
            right_margin = 0
            
            if sectPr is not None:
                pgSz = sectPr.find('w:pgSz', ns)
                pgMar = sectPr.find('w:pgMar', ns)
                
                if pgSz is not None:
                    w = pgSz.get(f"{{{ns['w']}}}w")
                    if w: page_width_dxa = int(w)
                    print(f"Page Width: {page_width_dxa} DXA ({page_width_dxa/567:.2f} cm)")
                
                if pgMar is not None:
                    left = pgMar.get(f"{{{ns['w']}}}left")
                    right = pgMar.get(f"{{{ns['w']}}}right")
                    if left: left_margin = int(left)
                    if right: right_margin = int(right)
                    print(f"Margins: Left={left_margin} DXA ({left_margin/567:.2f} cm), Right={right_margin} DXA ({right_margin/567:.2f} cm)")
            
            printable_width_dxa = page_width_dxa - left_margin - right_margin
            print(f"Printable Width: {printable_width_dxa} DXA ({printable_width_dxa/567:.2f} cm)")
            
            # 2. Check Tables
            tables = tree.findall('.//w:tbl', ns)
            print(f"Found {len(tables)} tables.")
            
            all_pass = True
            
            for i, tbl in enumerate(tables):
                tblPr = tbl.find('w:tblPr', ns)
                tblW = tblPr.find('w:tblW', ns)
                
                width_val = 0
                width_type = "unknown"
                
                if tblW is not None:
                    w = tblW.get(f"{{{ns['w']}}}w")
                    t = tblW.get(f"{{{ns['w']}}}type")
                    if w: width_val = int(w)
                    if t: width_type = t
                
                # If type is 'pct', value is 50ths of a percent
                # If type is 'dxa', value is 20ths of a point
                
                calculated_width_dxa = 0
                if width_type == 'dxa':
                    calculated_width_dxa = width_val
                elif width_type == 'pct':
                    # 5000 = 100%
                    calculated_width_dxa = (width_val / 5000) * printable_width_dxa
                elif width_type == 'auto':
                    print(f"Table {i+1}: Width is AUTO. Cannot strictly verify, but usually safe if content fits.")
                    continue
                
                print(f"Table {i+1}: Width={width_val} ({width_type}) -> {calculated_width_dxa:.0f} DXA ({calculated_width_dxa/567:.2f} cm)")
                
                # Check overflow
                # Allow small epsilon (e.g. 100 DXA ~ 0.17cm)
                if calculated_width_dxa > (printable_width_dxa + 100):
                    print(f"  [FAIL] Table {i+1} overflows by {calculated_width_dxa - printable_width_dxa} DXA")
                    all_pass = False
                else:
                    print(f"  [PASS] Table {i+1} fits.")

            return all_pass

    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return False

if __name__ == "__main__":
    # Test with the generated file
    target_file = "/app/test_output_130.docx"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        
    success = verify_docx_layout(target_file)
    if success:
        print("\n>>> LAYOUT VERIFICATION PASSED <<<")
        sys.exit(0)
    else:
        print("\n>>> LAYOUT VERIFICATION FAILED <<<")
        sys.exit(1)
