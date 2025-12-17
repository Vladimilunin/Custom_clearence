import re

filename = "FL202510240002  New request R1.01.00.001a, R1.01.00.002, R1.04.00.101 material Inconel 625 and SUS316L.pdf"

print(f"Testing filename: {filename}")

# 1. Extract Designations
designations = re.findall(r'(R1[\.\d\w]+)', filename)
print(f"Designations found: {designations}")

# 2. Extract Material
# Current logic: re.search(r'material\s+([^\.]+)', filename, re.IGNORECASE)
mat_match = re.search(r'material\s+([^\.]+)', filename, re.IGNORECASE)
if mat_match:
    material = mat_match.group(1).strip()
    print(f"Material found: '{material}'")
else:
    print("Material NOT found")

# User wants: "Inconel 625 and SUS316L" presumably?
# Or maybe they want to map specific materials to specific parts?
# "R1.01.00.001a, R1.01.00.002, R1.04.00.101 material Inconel 625 and SUS316L"
# It's ambiguous which material belongs to which part without more context.
# But for now, extracting the whole string "Inconel 625 and SUS316L" is better than nothing.
