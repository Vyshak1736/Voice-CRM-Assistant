from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, Any, List

# Initialize FastAPI app
app = FastAPI(title="Voice CRM API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5500", "http://127.0.0.1:5500", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    conn = sqlite3.connect('crm_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            audio_file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id INTEGER,
            customer_data TEXT,
            interaction_data TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transcription_id) REFERENCES transcriptions (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT,
            expected_output TEXT,
            actual_output TEXT,
            passed BOOLEAN,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Pydantic models
class ExtractionRequest(BaseModel):
    text: str

class CustomerData(BaseModel):
    full_name: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    locality: str = ""

class InteractionData(BaseModel):
    summary: str = ""
    created_at: str = ""

class CRMResponse(BaseModel):
    customer: CustomerData
    interaction: InteractionData

# Helper functions
def extract_phone_number(text: str) -> str:
    """Extract phone number from text"""
    # Remove spaces and convert digits
    cleaned_text = re.sub(r'[^\d]', '', text)
    
    # Look for 10-digit sequences
    phone_pattern = r'(\d{10})'
    matches = re.findall(phone_pattern, cleaned_text)
    
    if matches:
        return matches[0]
    
    # Look for phone number patterns with spaces
    phone_pattern_spaced = r'(\d\s*){10}'
    matches = re.findall(phone_pattern_spaced, text)
    if matches:
        return re.sub(r'\s', '', matches[0])
    
    return ""

def extract_name(text: str) -> str:
    """Extract person name from text - simplified version"""
    # Common name patterns
    name_patterns = [
        r'(?:customer|client|spoke with|met with|called|contacted)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:called|contacted|spoke|met)',
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return ""

def extract_address_info(text: str) -> Dict[str, str]:
    """Extract address, city, and locality from text"""
    address = ""
    city = ""
    locality = ""
    
    # Common Indian cities
    cities = ["mumbai", "delhi", "bangalore", "kolkata", "chennai", "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow", "noida", "gurgaon"]
    
    # Extract city
    text_lower = text.lower()
    for city_name in cities:
        if city_name in text_lower:
            city = city_name.title()
            break
    
    # Extract address (look for street/road patterns)
    address_patterns = [
        r'\d+\s+[\w\s]+(?:street|road|lane|avenue|colony|society|nagar)',
        r'[\w\s]+(?:street|road|lane|avenue|colony|society|nagar)\s*\d*',
    ]
    
    for pattern in address_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            address = matches[0].strip()
            break
    
    # Extract locality (area within city)
    if city:
        # Look for locality patterns
        locality_pattern = r'(\w+(?:\s+\w+)*?)\s*,\s*' + re.escape(city)
        matches = re.findall(locality_pattern, text, re.IGNORECASE)
        if matches:
            locality = matches[0].strip().title()
    
    return {"address": address, "city": city, "locality": locality}

def extract_interaction_summary(text: str) -> str:
    """Extract interaction summary from text"""
    action_words = ["discussed", "talked", "spoke", "meeting", "demo", "presentation", "follow-up", "next steps", "pricing", "proposal", "contract", "implementation"]
    
    for word in action_words:
        if word in text.lower():
            # Extract the part of text containing this action
            sentences = text.split('.')
            for sentence in sentences:
                if word in sentence.lower():
                    return sentence.strip()
    
    # Default fallback
    sentences = text.split('.')
    if len(sentences) > 1:
        return sentences[-2].strip()
    return text.strip()

def extract_structured_data(text: str) -> CRMResponse:
    """Extract structured CRM data from transcribed text"""
    
    # Extract customer information
    name = extract_name(text)
    phone = extract_phone_number(text)
    address_info = extract_address_info(text)
    
    customer = CustomerData(
        full_name=name,
        phone=phone,
        address=address_info["address"],
        city=address_info["city"],
        locality=address_info["locality"]
    )
    
    # Extract interaction information
    summary = extract_interaction_summary(text)
    interaction = InteractionData(
        summary=summary,
        created_at=datetime.now().isoformat() + "Z"
    )
    
    return CRMResponse(customer=customer, interaction=interaction)

# API endpoints
@app.get("/")
async def root():
    return {"message": "Voice CRM API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Mock transcription for demo purposes"""
    try:
        # Mock transcription since we don't have Whisper working
        # Using the user's example for better demo
        mock_transcription = "I spoke with customer Amit Verma today. His phone number is nine nine eight eight seven seven six six five five. He stays at 45 Park Street, Salt Lake, Kolkata. We discussed demo and next steps."
        
        # Save to database
        conn = sqlite3.connect('crm_data.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transcriptions (text, audio_file_path) VALUES (?, ?)",
            (mock_transcription, audio.filename)
        )
        conn.commit()
        conn.close()
        
        return {"transcription": mock_transcription}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/api/extract")
async def extract_data(request: ExtractionRequest):
    """Extract structured CRM data from transcribed text"""
    try:
        extracted_data = extract_structured_data(request.text)
        
        # Calculate confidence score (mock implementation)
        confidence = 0.85
        
        # Save to database
        conn = sqlite3.connect('crm_data.db')
        cursor = conn.cursor()
        
        # Get latest transcription ID
        cursor.execute("SELECT id FROM transcriptions ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        trans_id = result[0] if result else None
        
        cursor.execute(
            """INSERT INTO extracted_data 
               (transcription_id, customer_data, interaction_data, confidence_score) 
               VALUES (?, ?, ?, ?)""",
            (trans_id, json.dumps(extracted_data.customer.dict()), 
             json.dumps(extracted_data.interaction.dict()), confidence)
        )
        conn.commit()
        conn.close()
        
        return extracted_data.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")

@app.get("/api/evaluation/results")
async def get_evaluation_results():
    """Get evaluation test results"""
    try:
        conn = sqlite3.connect('crm_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, input_text, expected_output, actual_output, passed, confidence_score, created_at
            FROM evaluation_results 
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "input": row[1],
                "expected": json.loads(row[2]) if row[2] else {},
                "actual": json.loads(row[3]) if row[3] else {},
                "passed": bool(row[4]),
                "confidence": row[5],
                "timestamp": row[6]
            })
        
        # Calculate stats
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        accuracy = (passed / total * 100) if total > 0 else 0
        
        conn.close()
        
        return {
            "results": results,
            "stats": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "accuracy": round(accuracy, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation results: {str(e)}")

@app.post("/api/evaluation/run")
async def run_evaluation_tests():
    """Run evaluation tests"""
    try:
        test_cases = [
            {
                "input": "I spoke with customer Amit Verma today. His phone number is nine nine eight eight seven seven six six five five. He stays at 45 Park Street, Salt Lake, Kolkata. We discussed the demo and next steps.",
                "expected": {
                    "customer": {
                        "full_name": "Amit Verma",
                        "phone": "9988776655",
                        "address": "45 Park Street",
                        "city": "Kolkata",
                        "locality": "Salt Lake"
                    },
                    "interaction": {
                        "summary": "Discussed demo and next steps",
                        "created_at": "2026-01-18T11:30:00Z"
                    }
                }
            },
            {
                "input": "Customer Sarah Johnson called from 9876543210. She lives at 123 Main Road, Bandra, Mumbai. We talked about pricing options.",
                "expected": {
                    "customer": {
                        "full_name": "Sarah Johnson",
                        "phone": "9876543210",
                        "address": "123 Main Road",
                        "city": "Mumbai",
                        "locality": "Bandra"
                    },
                    "interaction": {
                        "summary": "Talked about pricing options",
                        "created_at": "2026-01-20T11:00:00Z"
                    }
                }
            }
        ]
        
        conn = sqlite3.connect('crm_data.db')
        cursor = conn.cursor()
        
        for test_case in test_cases:
            # Extract data
            actual = extract_structured_data(test_case["input"])
            
            # Compare with expected (simple comparison)
            expected_customer = test_case["expected"]["customer"]
            actual_customer = actual.customer.dict()
            
            passed = (
                actual_customer["full_name"].lower() == expected_customer["full_name"].lower() and
                actual_customer["phone"] == expected_customer["phone"] and
                expected_customer["city"].lower() in actual_customer["city"].lower()
            )
            
            # Save result
            cursor.execute(
                """INSERT INTO evaluation_results 
                   (input_text, expected_output, actual_output, passed, confidence_score) 
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    test_case["input"],
                    json.dumps(test_case["expected"]),
                    json.dumps(actual.dict()),
                    passed,
                    0.85
                )
            )
        
        conn.commit()
        conn.close()
        
        return {"message": "Evaluation tests completed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
