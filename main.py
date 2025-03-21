import os
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
import io
import re

# Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ ERROR: GOOGLE_API_KEY is missing! Check your .env file.")

# Configure Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# FastAPI setup
app = FastAPI()

# CORS setup (allow frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to format math expressions
def format_math_expression(text):
    match = re.match(r"(\d+)\s*([\+\-\/])\s(\d+)", text)
    if match:
        a, operator, b = match.groups()
        try:
            a, b = int(a), int(b)
            result = eval(f"{a} {operator} {b}")
            return f"{a} {operator} {b} = {result}"
        except:
            return text  # Return original text if eval fails
    return text  # If no match, return original text

@app.post("/analyze/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert image to binary format
        image_bytes_io = io.BytesIO()
        image.save(image_bytes_io, format="PNG")
        image_bytes = image_bytes_io.getvalue()

        # Send to Gemini API
        response = model.generate_content(
            [{"mime_type": "image/png", "data": image_bytes}]
        )

        # Process response
        if response and response.text:
            raw_result = response.text.strip()
            print("🔹 AI Response:", raw_result)
            formatted_result = format_math_expression(raw_result)
            return {"result": formatted_result}
        else:
            return {"result": "⚠️ No response from AI"}
    
    except Exception as e:
        print("❌ Error processing image:", str(e))
        return {"error": str(e)}
