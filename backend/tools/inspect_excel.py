import pandas as pd

file_path = "_для бд/2_PI_Shenzhen_Wofly 20231211 (1).xls"
try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
except Exception as e:
    print(f"Error reading Excel: {e}")
