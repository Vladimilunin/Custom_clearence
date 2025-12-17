import pdfplumber
import os

base_dir = r"d:/Work/_develop/_gen_for_ tamozh/_dev/ПРимеры документов"
files = [
    "Исх 64 от 15.08.2026 Письмо о не страховании HBEST-AS001 Guizhou Hbest.pdf",
    "УВЕДОМЛЕНИЕ по 130 Решению (БСЛ-Лаб).pdf"
]

for filename in files:
    path = os.path.join(base_dir, filename)
    print(f"\n{'='*20}\nProcessing: {filename}\n{'='*20}")
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                print(text)
                print("-" * 20)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
