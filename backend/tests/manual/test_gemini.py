import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyAtm6OyAgwcNgYc67ENp7Vs1FymAstGjxc"
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
