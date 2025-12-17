import pandas as pd

file_path = "_для бд/2_PI_Shenzhen_Wofly 20231211 (1).xls"
try:
    df = pd.read_excel(file_path, header=None, nrows=20)
    print(df)
except Exception as e:
    print(f"Error: {e}")
