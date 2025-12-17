import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mocking necessary imports if they depend on DB or other things not present in standalone script
# But generator.py seems mostly standalone (depends on docx)

try:
    from app.services.generator import generate_decision_130_notification
except ImportError as e:
    print(f"ImportError: {e}")
    # Try to setup path better if needed, but /app should work in docker
    sys.exit(1)

class SimplePart:
    def __init__(self, designation, name, quantity):
        self.designation = designation
        self.name = name
        self.quantity = quantity

items = [
    SimplePart("PART-001", "Test Part 1", 10),
    SimplePart("PART-002", "Test Part 2", 5)
]

output_path = "test_output_130.docx"

print("Starting generation test...")
try:
    generate_decision_130_notification(
        items=items,
        output_path=output_path,
        contract_no="CONTRACT-123",
        contract_date="2025-01-01",
        invoice_no="INVOICE-456",
        invoice_date="2025-01-02",
        add_facsimile=True
    )
    print(f"Successfully generated document at {output_path}")
    
    # Verify file exists
    if os.path.exists(output_path):
        print(f"File {output_path} exists. Size: {os.path.getsize(output_path)} bytes")
    else:
        print(f"File {output_path} does NOT exist!")

except Exception as e:
    print(f"Error during generation: {e}")
    import traceback
    traceback.print_exc()
