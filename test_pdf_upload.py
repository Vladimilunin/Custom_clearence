"""Test script to upload PDF and check parsing."""
import requests
import sys

def test_pdf_upload():
    """Test uploading PI PTJ20251023B1.pdf to the API."""
    
    api_url = "http://localhost:8001/api/v1/invoices/upload"
    pdf_path = "PI PTJ20251023B1.pdf"
    
    print(f"Testing PDF upload: {pdf_path}")
    print(f"API endpoint: {api_url}")
    print("-" * 60)
    
    try:
        # Open PDF file
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            data = {
                'method': 'openrouter_gemini_2_5_flash_lite',
                'api_key': ''  # Will use default from .env
            }
            
            print("Sending request...")
            response = requests.post(api_url, files=files, data=data, timeout=60)
            
            print(f"Status code: {response.status_code}")
            print("-" * 60)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Items found: {len(result.get('items', []))}")
                print(f"Method used: {result.get('debug_info', {}).get('method_used', 'N/A')}")
                
                if result.get('items'):
                    print("\nFirst item:")
                    item = result['items'][0]
                    print(f"  Designation: {item.get('designation')}")
                    print(f"  Name: {item.get('name')}")
                    print(f"  Found in DB: {item.get('found_in_db')}")
                    
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text[:500])
                return False
                
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the backend running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_upload()
    sys.exit(0 if success else 1)
