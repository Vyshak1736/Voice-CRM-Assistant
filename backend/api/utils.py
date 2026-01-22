import pandas as pd
import json
from datetime import datetime
import re
from .models import TestResult, Customer, Interaction
import openai
import os
from fuzzywuzzy import fuzz, process

class DataExtractor:
    """Enhanced data extraction using multiple NLP approaches and LLM"""
    
    def __init__(self):
        self.indian_cities = [
            'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune', 
            'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur', 'nagpur', 'indore', 
            'thane', 'bhopal', 'visakhapatnam', 'pimpri', 'patna', 'vadodara', 'ghaziabad',
            'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan',
            'vasai', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar',
            'navi mumbai', 'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur',
            'gwalior', 'vijayawada', 'jodhpur', 'madurai', 'raipur', 'kota', 'chandigarh',
            'guwahati', 'solapur', 'hubli', 'tiruchirappalli', 'bareilly', 'mysore',
            'tirupur', 'gurgaon', 'aligarh', 'jalandhar', 'bhubaneswar', 'salem',
            'mira', 'thane', 'mathura', 'bhiwandi', 'saharanpur', 'gorakhpur',
            'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack',
            'firozabad', 'kochi', 'nellore', 'bhavnagar', 'tirupati', 'kurnool',
            'rajahmundry', 'tumkur', 'kishanganj', 'erode', 'bokaro', 'south dumdum',
            'bellary', 'patiala', 'gurgaon', 'noida', 'faridabad', 'ghaziabad'
        ]
        
        self.locality_patterns = [
            r'([A-Za-z]+\s+(?:Layout|Colony|Nagar|Enclave|Park|Garden|Hills|Lake|Circle|Square))',
            r'([A-Za-z]+\s+(?:Sector|Block|Phase|Zone))',
            r'([A-Za-z]+\s+(?:Street|Road|Lane|Avenue))',
            r'in\s+([A-Za-z]+\s+(?:Layout|Colony|Nagar))'
        ]
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None

    def extract_customer_data(self, text):
        """Enhanced extraction with multiple approaches including LLM"""
        
        # First try regex-based extraction
        result = self._extract_with_regex(text)
        
        # If OpenAI is available, enhance with LLM
        if self.openai_client:
            try:
                llm_result = self._extract_with_llm(text)
                # Merge results, preferring LLM for complex cases
                result = self._merge_extraction_results(result, llm_result)
            except Exception as e:
                print(f"LLM extraction failed, using regex only: {e}")
        
        return result
    
    def _extract_with_regex(self, text):
        """Regex-based extraction with confidence scoring"""
        
        result = {
            "customer": {
                "full_name": "",
                "phone": "",
                "address": "",
                "city": "",
                "locality": ""
            },
            "interaction": {
                "summary": "",
                "created_at": datetime.now().isoformat()
            },
            "confidence_scores": {
                "name": 0.0,
                "phone": 0.0,
                "address": 0.0,
                "city": 0.0,
                "locality": 0.0,
                "summary": 0.0
            }
        }
        
        # Convert spoken numbers to digits first
        text = self._convert_spoken_numbers(text)
        
        # Extract name with confidence scoring
        name_patterns = [
            r'customer\s+([A-Za-z]+\s+[A-Za-z]+)',
            r'([A-Za-z]+\s+[A-Za-z]+)\s+called',
            r'spoke\s+with\s+([A-Za-z]+\s+[A-Za-z]+)',
            r'met\s+with\s+([A-Za-z]+\s+[A-Za-z]+)',
            r'called\s+([A-Za-z]+\s+[A-Za-z]+)'
        ]
        
        name_confidence = 0.0
        for i, pattern in enumerate(name_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["customer"]["full_name"] = match.group(1).strip()
                name_confidence = 0.8 + (i * 0.04)  # Higher confidence for earlier patterns
                break
        
        result["confidence_scores"]["name"] = name_confidence
        
        # Extract phone number with validation
        phone_patterns = [
            r'phone\s+(?:number\s+)?([0-9\s]{10,15})',
            r'number\s+is\s+([0-9\s]{10,15})',
            r'contact\s+([0-9\s]{10,15})',
            r'([0-9]{10})',
            r'([0-9\s]{10})'
        ]
        
        phone_confidence = 0.0
        for i, pattern in enumerate(phone_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = re.sub(r'\s', '', match.group(1))
                if len(phone) >= 10:
                    result["customer"]["phone"] = phone[-10:]  # Take last 10 digits
                    phone_confidence = 0.9 + (i * 0.02)
                    break
        
        result["confidence_scores"]["phone"] = phone_confidence
        
        # Extract address
        address_patterns = [
            r'at\s+([0-9]+\s+[^,]+)',
            r'address\s+is\s+([^,]+)',
            r'located\s+at\s+([^,]+)',
            r'([^,]+\s+(?:Street|Road|Lane|Avenue|Sector|Block))'
        ]
        
        address_confidence = 0.0
        for i, pattern in enumerate(address_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["customer"]["address"] = match.group(1).strip()
                address_confidence = 0.7 + (i * 0.05)
                break
        
        result["confidence_scores"]["address"] = address_confidence
        
        # Extract city with fuzzy matching
        city_confidence = 0.0
        text_lower = text.lower()
        
        # Try exact match first
        for city in self.indian_cities:
            if city in text_lower:
                result["customer"]["city"] = city.title()
                city_confidence = 0.85
                break
        
        # If no exact match, try fuzzy matching
        if not result["customer"]["city"]:
            cities_in_text = [word for word in text_lower.split() if len(word) > 3]
            if cities_in_text:
                best_match, score = process.extractOne(text_lower, self.indian_cities)
                if score > 80:  # High confidence threshold
                    result["customer"]["city"] = best_match.title()
                    city_confidence = score / 100
        
        result["confidence_scores"]["city"] = city_confidence
        
        # Extract locality
        locality_confidence = 0.0
        for i, pattern in enumerate(self.locality_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["customer"]["locality"] = match.group(1).strip()
                locality_confidence = 0.75 + (i * 0.05)
                break
        
        result["confidence_scores"]["locality"] = locality_confidence
        
        # Extract interaction summary
        summary_patterns = [
            r'(?:discussed|talked about|we|they)\s+(.+)',
            r'(?:next steps|follow up|meeting|demo|pricing|contract|agreement)\s*(.+)',
            r'(?:interested in|wants to|needs to|will)\s+(.+)'
        ]
        
        summary_confidence = 0.0
        for i, pattern in enumerate(summary_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                summary = match.group(1).strip()
                summary = re.sub(r'\.+$', '', summary)  # Remove trailing periods
                result["interaction"]["summary"] = summary
                summary_confidence = 0.8 + (i * 0.05)
                break
        
        result["confidence_scores"]["summary"] = summary_confidence
        
        return result
    
    def _extract_with_llm(self, text):
        """Use OpenAI GPT for enhanced data extraction"""
        
        prompt = f"""
Extract customer and interaction information from the following text. Return a JSON object with this exact structure:

{{
  "customer": {{
    "full_name": "",
    "phone": "",
    "address": "",
    "city": "",
    "locality": ""
  }},
  "interaction": {{
    "summary": ""
  }}
}}

Rules:
- Extract phone numbers as 10-digit numbers without spaces or dashes
- Convert spoken numbers (like "nine nine eight eight") to digits
- Use title case for names and cities
- If information is not found, leave the field empty
- Focus on customer details and what was discussed

Text: "{text}"

Return only the JSON object, no other text:
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Extract structured information from text and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            llm_result = json.loads(response.choices[0].message.content.strip())
            
            # Add confidence scores for LLM extraction
            llm_result["confidence_scores"] = {
                "name": 0.95,
                "phone": 0.95,
                "address": 0.85,
                "city": 0.90,
                "locality": 0.85,
                "summary": 0.90
            }
            
            return llm_result
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return None
    
    def _merge_extraction_results(self, regex_result, llm_result):
        """Merge regex and LLM results, preferring LLM for complex cases"""
        
        if not llm_result:
            return regex_result
        
        merged = {
            "customer": {
                "full_name": "",
                "phone": "",
                "address": "",
                "city": "",
                "locality": ""
            },
            "interaction": {
                "summary": "",
                "created_at": datetime.now().isoformat()
            },
            "confidence_scores": {}
        }
        
        # For each field, prefer LLM if it has high confidence and non-empty value
        for field in ["full_name", "phone", "address", "city", "locality"]:
            llm_value = llm_result.get("customer", {}).get(field, "").strip()
            regex_value = regex_result.get("customer", {}).get(field, "").strip()
            
            if llm_value and llm_result.get("confidence_scores", {}).get(field, 0) > 0.8:
                merged["customer"][field] = llm_value
                merged["confidence_scores"][field] = llm_result["confidence_scores"][field]
            else:
                merged["customer"][field] = regex_value
                merged["confidence_scores"][field] = regex_result["confidence_scores"][field]
        
        # For summary, prefer LLM as it's better at understanding context
        llm_summary = llm_result.get("interaction", {}).get("summary", "").strip()
        regex_summary = regex_result.get("interaction", {}).get("summary", "").strip()
        
        if llm_summary and len(llm_summary) > len(regex_summary):
            merged["interaction"]["summary"] = llm_summary
            merged["confidence_scores"]["summary"] = llm_result["confidence_scores"]["summary"]
        else:
            merged["interaction"]["summary"] = regex_summary
            merged["confidence_scores"]["summary"] = regex_result["confidence_scores"]["summary"]
        
        return merged

    def _convert_spoken_numbers(self, text):
        """Convert spoken numbers to digits"""
        number_map = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20'
        }
        
        # First pass: Convert individual spoken numbers
        words = text.lower().split()
        converted_words = []
        
        for word in words:
            if word in number_map:
                converted_words.append(number_map[word])
            else:
                converted_words.append(word)
        
        converted_text = ' '.join(converted_words)
        
        # Second pass: Look for any remaining spoken numbers and convert them
        import re
        
        # Find any remaining spoken numbers
        remaining_spoken = re.findall(r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b', converted_text)
        for spoken in remaining_spoken:
            converted_text = converted_text.replace(spoken, number_map[spoken])
        
        # Finally, look for sequences of 5+ digits separated by spaces and compact them
        digit_sequences = re.findall(r'(?:\d\s+){4,}\d', converted_text)
        for sequence in digit_sequences:
            compact_sequence = re.sub(r'\s+', '', sequence)
            converted_text = converted_text.replace(sequence, compact_sequence)
        
        return converted_text

class EvaluationManager:
    """Manage evaluation tests and results"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        self.test_cases = [
            {
                "id": 1,
                "input": "I spoke with customer Amit Verma today. His phone number is nine nine eight eight seven seven six six five five. He stays at 45 Park Street, Salt Lake, Kolkata. We discussed demo and next steps.",
                "expected": {
                    "customer": {
                        "full_name": "Amit Verma",
                        "phone": "9988776655",
                        "city": "Kolkata",
                        "locality": "Salt Lake"
                    },
                    "interaction": {
                        "summary": "discussed demo and next steps"
                    }
                }
            },
            {
                "id": 2,
                "input": "Customer Sarah Johnson called from 9876543210. She lives at 123 Main Road, Bandra, Mumbai. We talked about pricing options for the premium package.",
                "expected": {
                    "customer": {
                        "full_name": "Sarah Johnson",
                        "phone": "9876543210",
                        "city": "Mumbai",
                        "locality": "Bandra"
                    },
                    "interaction": {
                        "summary": "talked about pricing options for the premium package"
                    }
                }
            },
            {
                "id": 3,
                "input": "Met with Rajesh Kumar at his office in HSR Layout, Bangalore. His contact number is nine eight seven six five four three two one zero. They want to schedule a product demonstration.",
                "expected": {
                    "customer": {
                        "full_name": "Rajesh Kumar",
                        "phone": "9876543210",
                        "city": "Bangalore",
                        "locality": "HSR Layout"
                    },
                    "interaction": {
                        "summary": "want to schedule a product demonstration"
                    }
                }
            },
            {
                "id": 4,
                "input": "Priya Sharma from Sector 15, Noida called. Her phone is eight eight seven seven six six five five four four. She is interested in the enterprise plan and needs technical specifications.",
                "expected": {
                    "customer": {
                        "full_name": "Priya Sharma",
                        "phone": "8877665544",
                        "city": "Noida",
                        "locality": "Sector 15"
                    },
                    "interaction": {
                        "summary": "interested in the enterprise plan and needs technical specifications"
                    }
                }
            },
            {
                "id": 5,
                "input": "Customer Michael Thomas stays at 789 MG Road, Indiranagar, Bangalore. Contact number is nine nine nine eight eight eight seven seven seven six. We finalized the contract terms.",
                "expected": {
                    "customer": {
                        "full_name": "Michael Thomas",
                        "phone": "9998887776",
                        "city": "Bangalore",
                        "locality": "Indiranagar"
                    },
                    "interaction": {
                        "summary": "finalized the contract terms"
                    }
                }
            }
        ]
    
    def run_evaluation(self):
        """Run comprehensive evaluation"""
        results = []
        passed_count = 0
        
        for test_case in self.test_cases:
            # Extract data
            extracted = self.extractor.extract_customer_data(test_case["input"])
            
            # Compare with expected
            passed = self.compare_results(extracted, test_case["expected"])
            confidence = self.calculate_confidence(extracted, test_case["expected"])
            
            if passed:
                passed_count += 1
            
            # Save to database
            test_result = TestResult.objects.create(
                test_id=test_case["id"],
                input_text=test_case["input"],
                expected_output=test_case["expected"],
                actual_output=extracted,
                passed=passed,
                confidence=confidence
            )
            
            results.append({
                "id": test_case["id"],
                "input": test_case["input"][:100] + "...",
                "passed": passed,
                "confidence": confidence,
                "timestamp": test_result.timestamp.isoformat(),
                "extracted": extracted,
                "expected": test_case["expected"]
            })
        
        accuracy = (passed_count / len(self.test_cases)) * 100
        
        return {
            "results": results,
            "accuracy": accuracy,
            "total_tests": len(self.test_cases),
            "passed_tests": passed_count,
            "failed_tests": len(self.test_cases) - passed_count
        }
    
    def compare_results(self, actual, expected):
        """Compare actual and expected results"""
        try:
            # Compare customer data
            customer_match = True
            for key in ["full_name", "phone", "city", "locality"]:
                actual_val = actual.get("customer", {}).get(key, "").lower().strip()
                expected_val = expected.get("customer", {}).get(key, "").lower().strip()
                if actual_val != expected_val and expected_val:
                    customer_match = False
                    break
            
            # Compare interaction summary
            actual_summary = actual.get("interaction", {}).get("summary", "").lower().strip()
            expected_summary = expected.get("interaction", {}).get("summary", "").lower().strip()
            summary_match = actual_summary == expected_summary or expected_summary in actual_summary
            
            return customer_match and summary_match
            
        except Exception:
            return False
    
    def calculate_confidence(self, actual, expected):
        """Calculate confidence score"""
        try:
            if "confidence_scores" not in actual:
                return 0.0
            
            confidence_scores = actual["confidence_scores"]
            total_confidence = sum(confidence_scores.values())
            avg_confidence = total_confidence / len(confidence_scores)
            
            return round(avg_confidence, 2)
            
        except Exception:
            return 0.0
    
    def export_to_excel(self):
        """Export evaluation results to Excel"""
        try:
            # Get all test results
            results = TestResult.objects.all().order_by('-timestamp')
            
            data = []
            for result in results:
                data.append({
                    'Test ID': result.test_id,
                    'Input Text': result.input_text,
                    'Expected Output': json.dumps(result.expected_output, indent=2),
                    'Actual Output': json.dumps(result.actual_output, indent=2),
                    'Passed': 'Yes' if result.passed else 'No',
                    'Confidence': result.confidence,
                    'Timestamp': result.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'evaluation_results_{timestamp}.xlsx'
            
            # Save to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            return filename
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return None
