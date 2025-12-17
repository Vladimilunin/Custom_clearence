import pandas as pd

file_path = "_для бд/2_PI_Shenzhen_Wofly 20231211 (1).xls"
try:
    df = pd.read_excel(file_path, header=None, nrows=15)
    print("Row 9:", df.iloc[9].tolist())
except Exception as e:
    print(f"Error: {e}")
