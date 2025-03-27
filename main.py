import os
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
import io
import re
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ ERROR: GOOGLE_API_KEY is missing! Check your .env file.")

# Configure Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize currency converter with timeout
c = CurrencyRates()

# Fallback exchange rates (will be used if API fails)
FALLBACK_RATES = {
    'USD': {'INR': 83.50, 'EUR': 0.93, 'GBP': 0.80, 'JPY': 151.50},
    'EUR': {'USD': 1.07, 'INR': 89.50, 'GBP': 0.86, 'JPY': 162.00},
    'GBP': {'USD': 1.25, 'EUR': 1.16, 'INR': 104.50, 'JPY': 189.00},
    'JPY': {'USD': 0.0066, 'EUR': 0.0062, 'GBP': 0.0053, 'INR': 0.55},
    'INR': {'USD': 0.012, 'EUR': 0.011, 'GBP': 0.0096, 'JPY': 1.82}
}

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

def format_math_expression(text):
    """
    Extract just the final answer from math explanations.
    Returns:
    - For boxed answers: \boxed{7/12} → "7/12"
    - For simple results: "The answer is 7/12" → "7/12"
    - For direct expressions: "1/3 + 1/4" → "7/12"
    """
    # Remove common LaTeX formatting
    text = text.replace("$", "").replace("\\dfrac", "\\frac")
    
    # Pattern 1: Look for \boxed{answer}
    boxed_pattern = r"\\boxed\{([^}]+)\}"
    boxed_match = re.search(boxed_pattern, text)
    if boxed_match:
        return boxed_match.group(1).strip()
    
    # Pattern 2: Look for "the answer is X"
    answer_pattern = r"(?:answer|result|solution)[\s:is]*([^\n]+)"
    answer_match = re.search(answer_pattern, text, re.IGNORECASE)
    if answer_match:
        answer = answer_match.group(1).strip()
        # Clean up any remaining formatting
        answer = re.sub(r"[\\{}]", "", answer)
        return answer
    
    # Pattern 3: Try to evaluate simple expressions directly
    try:
        # Remove all non-math characters
        clean_expr = re.sub(r"[^\d\+\-\*\/\(\)\.]", "", text)
        if clean_expr:
            result = eval(clean_expr)
            # Convert to fraction if needed
            if isinstance(result, float) and not result.is_integer():
                from fractions import Fraction
                return str(Fraction(result).limit_denominator())
            return str(result)
    except:
        pass
    
    # Fallback: Return the original text if no answer found
    return text.strip()

def convert_currency(text):
    """
    Handle currency conversion requests in formats like:
    - 2$->₹
    - 100 USD to INR
    - €50 in rupees
    """
    # Normalize the text
    text = text.replace('->', ' to ').replace('in', ' to ')
    
    # Pattern for currency conversion
    pattern = r"(\d+\.?\d*)\s*([$€£¥₹]|[A-Za-z]{3})\s*to\s*([$€£¥₹]|[A-Za-z]{3})"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    
    amount, from_curr, to_curr = match.groups()
    
    # Convert symbol to currency code if needed
    symbol_to_code = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR'
    }
    
    from_curr = symbol_to_code.get(from_curr, from_curr.upper())
    to_curr = symbol_to_code.get(to_curr, to_curr.upper())
    
    try:
        amount = float(amount)
        
        # First try with live rates
        try:
            converted = c.convert(from_curr, to_curr, amount)
            return f"{amount} {from_curr} = {round(converted, 2)} {to_curr} (live rate)"
        except Exception as api_error:
            print(f"API Error: {api_error}. Using fallback rates.")
            
            # Fallback to static rates if API fails
            if from_curr in FALLBACK_RATES and to_curr in FALLBACK_RATES[from_curr]:
                rate = FALLBACK_RATES[from_curr][to_curr]
                converted = amount * rate
                return f"{amount} {from_curr} ≈ {round(converted, 2)} {to_curr} (approximate rate)"
            else:
                return f"Currency conversion not available for {from_curr} to {to_curr}"
                
    except Exception as e:
        print(f"Currency conversion error: {e}")
        return None

def analyze_physics_equation(text):
    """
    Identify physics equations and provide information about them.
    Returns None if the text doesn't contain a recognizable physics equation.
    """
    # Common physics equations pattern
    physics_patterns = {
        r"F\s*=\s*m\s*a": "Newton's Second Law of Motion (Force = mass × acceleration)",
        r"E\s*=\s*m\s*c\^2": "Einstein's Mass-Energy Equivalence",
        r"v\s*=\s*u\s*\+\s*a\s*t": "Kinematic Equation (Final velocity = initial velocity + acceleration × time)",
        r"s\s*=\s*u\s*t\s*\+\s*0\.5\s*a\s*t\^2": "Kinematic Equation (Displacement = initial velocity × time + 0.5 × acceleration × time²)",
        r"P\s*=\s*V\s*I": "Electric Power (Power = Voltage × Current)",
        r"V\s*=\s*I\s*R": "Ohm's Law (Voltage = Current × Resistance)",
        r"a\s*=\s*v\^2\s*\/\s*r": "Centripetal Acceleration",
        r"F\s*=\s*G\s*m1\s*m2\s*\/\s*r\^2": "Newton's Law of Universal Gravitation",
        r"K\.E\.\s*=\s*0\.5\s*m\s*v\^2": "Kinetic Energy",
        r"P\.E\.\s*=\s*m\s*g\s*h": "Gravitational Potential Energy",
        r"λ\s*=\s*v\s*\/\s*f": "Wave Equation (Wavelength = velocity / frequency)"
    }
    
    # Remove spaces for better matching
    clean_text = re.sub(r"\s+", "", text)
    
    for pattern, description in physics_patterns.items():
        if re.fullmatch(pattern, clean_text, re.IGNORECASE):
            return description
    
    # If no match found
    return None

@app.post("/analyze/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read the image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert image to binary format
        image_bytes_io = io.BytesIO()
        image.save(image_bytes_io, format="PNG")
        image_bytes = image_bytes_io.getvalue()

        # Use Gemini API for image analysis with specific instruction
        response = model.generate_content(
            [
                {"mime_type": "image/png", "data": image_bytes},
                """Analyze this content and respond based on what it is:
                - For Programs: give us the output , For example  if The image shows print('hi') you have give it's result , here hi is the result and for print('2+2') its result is 2+2 
                - For math problems: provide only the final numerical answer
                - For currency conversions: provide the query in format 'X USD to INR'
                - For physics equations: provide the equation exactly as written and explain it in one line 
                - For Symbols: provide the name of that Symbol , For example if The image shows four overlapping circles then its Audi symbol, like this.
                - For pictures: provide the things in that picture and explain it in one line 
                - For Symbols: provide the name of that Symbol
                - see the color for better result
                
                - For other content: provide the text as-is"""
            ]
        )

        # Process the response
        if response and response.text:
            raw_result = response.text.strip()
            print("🔹 Raw AI Response:", raw_result)  # Debug print
            
            # First try currency conversion
            currency_result = convert_currency(raw_result)
            if currency_result:
                return {"result": currency_result}
            
            # Then try physics equation identification
            physics_result = analyze_physics_equation(raw_result)
            if physics_result:
                return {"result": f"Physics Equation: {physics_result}"}
            
            # Then try math expression
            formatted_result = format_math_expression(raw_result)
            if formatted_result != raw_result:  # Only return if formatting changed
                return {"result": formatted_result}
            
            # Fallback: return original text
            return {"result": raw_result}
        else:
            return {"result": "No response from AI"}
    
    except Exception as e:
        print("❌ Error processing image:", str(e))
        return {"error": str(e)}
