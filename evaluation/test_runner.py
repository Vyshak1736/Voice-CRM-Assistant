#!/usr/bin/env python3
"""
Voice CRM Evaluation Test Runner
Runs automated tests on the voice-to-CRM data extraction system
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import sqlite3
from typing import List, Dict, Any
import os

class VoiceCRMEvaluator:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.test_results = []
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'crm_data.db')
    
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from file or use default test cases"""
        test_cases = [
            {
                "id": 1,
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
                },
                "category": "basic_extraction"
            },
            {
                "id": 2,
                "input": "Customer Sarah Johnson called from 9876543210. She lives at 123 Main Road, Bandra, Mumbai. We talked about pricing options for the enterprise plan.",
                "expected": {
                    "customer": {
                        "full_name": "Sarah Johnson",
                        "phone": "9876543210",
                        "address": "123 Main Road",
                        "city": "Mumbai",
                        "locality": "Bandra"
                    },
                    "interaction": {
                        "summary": "Talked about pricing options for the enterprise plan",
                        "created_at": "2026-01-20T11:00:00Z"
                    }
                },
                "category": "pricing_discussion"
            },
            {
                "id": 3,
                "input": "Met with Rajesh Kumar at his office in HSR Layout, Bangalore. His contact number is eight nine seven six five four three two one zero. We finalized the contract terms.",
                "expected": {
                    "customer": {
                        "full_name": "Rajesh Kumar",
                        "phone": "8976543210",
                        "address": "",
                        "city": "Bangalore",
                        "locality": "HSR Layout"
                    },
                    "interaction": {
                        "summary": "Finalized the contract terms",
                        "created_at": "2026-01-20T14:30:00Z"
                    }
                },
                "category": "contract_finalization"
            },
            {
                "id": 4,
                "input": "Priya Sharma from Connaught Place, Delhi contacted us. Her phone is seven six five four three two one zero nine eight. She wants a product demonstration next week.",
                "expected": {
                    "customer": {
                        "full_name": "Priya Sharma",
                        "phone": "7654321098",
                        "address": "",
                        "city": "Delhi",
                        "locality": "Connaught Place"
                    },
                    "interaction": {
                        "summary": "Wants a product demonstration next week",
                        "created_at": "2026-01-20T16:00:00Z"
                    }
                },
                "category": "demo_request"
            },
            {
                "id": 5,
                "input": "Follow-up call with Michael Chen from Sector 15, Noida. Contact: double two three four five six seven eight nine zero. Discussed implementation timeline and training requirements.",
                "expected": {
                    "customer": {
                        "full_name": "Michael Chen",
                        "phone": "2234567890",
                        "address": "",
                        "city": "Noida",
                        "locality": "Sector 15"
                    },
                    "interaction": {
                        "summary": "Discussed implementation timeline and training requirements",
                        "created_at": "2026-01-20T17:15:00Z"
                    }
                },
                "category": "follow_up_call"
            }
        ]
        
        return test_cases
    
    def compare_results(self, expected: Dict, actual: Dict) -> Dict[str, Any]:
        """Compare expected and actual results"""
        comparison = {
            "name_match": False,
            "phone_match": False,
            "city_match": False,
            "locality_match": False,
            "summary_similarity": 0.0,
            "overall_score": 0.0
        }
        
        # Compare customer name
        exp_name = expected.get("customer", {}).get("full_name", "").lower()
        act_name = actual.get("customer", {}).get("full_name", "").lower()
        comparison["name_match"] = exp_name == act_name
        
        # Compare phone number
        exp_phone = expected.get("customer", {}).get("phone", "")
        act_phone = actual.get("customer", {}).get("phone", "")
        comparison["phone_match"] = exp_phone == act_phone
        
        # Compare city
        exp_city = expected.get("customer", {}).get("city", "").lower()
        act_city = actual.get("customer", {}).get("city", "").lower()
        comparison["city_match"] = exp_city == act_city
        
        # Compare locality
        exp_locality = expected.get("customer", {}).get("locality", "").lower()
        act_locality = actual.get("customer", {}).get("locality", "").lower()
        comparison["locality_match"] = exp_locality == act_locality
        
        # Compare summary (simple similarity check)
        exp_summary = expected.get("interaction", {}).get("summary", "").lower()
        act_summary = actual.get("interaction", {}).get("summary", "").lower()
        
        if exp_summary and act_summary:
            common_words = set(exp_summary.split()) & set(act_summary.split())
            total_words = set(exp_summary.split()) | set(act_summary.split())
            comparison["summary_similarity"] = len(common_words) / len(total_words) if total_words else 0.0
        
        # Calculate overall score
        matches = sum([
            comparison["name_match"],
            comparison["phone_match"],
            comparison["city_match"],
            comparison["locality_match"]
        ])
        comparison["overall_score"] = (matches + comparison["summary_similarity"]) / 5.0
        
        return comparison
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        print(f"Running test case {test_case['id']}: {test_case['category']}")
        
        try:
            # Send request to backend
            response = requests.post(
                f"{self.backend_url}/api/extract",
                json={"text": test_case["input"]},
                timeout=30
            )
            
            if response.status_code == 200:
                actual = response.json()
                comparison = self.compare_results(test_case["expected"], actual)
                
                result = {
                    "test_id": test_case["id"],
                    "category": test_case["category"],
                    "input": test_case["input"],
                    "expected": test_case["expected"],
                    "actual": actual,
                    "comparison": comparison,
                    "passed": comparison["overall_score"] >= 0.7,  # 70% threshold
                    "confidence": comparison["overall_score"],
                    "timestamp": datetime.now().isoformat(),
                    "error": None
                }
            else:
                result = {
                    "test_id": test_case["id"],
                    "category": test_case["category"],
                    "input": test_case["input"],
                    "expected": test_case["expected"],
                    "actual": None,
                    "comparison": None,
                    "passed": False,
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            result = {
                "test_id": test_case["id"],
                "category": test_case["category"],
                "input": test_case["input"],
                "expected": test_case["expected"],
                "actual": None,
                "comparison": None,
                "passed": False,
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        
        return result
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all test cases"""
        print("🚀 Starting Voice CRM evaluation tests...")
        
        test_cases = self.load_test_cases()
        results = []
        
        for test_case in test_cases:
            result = self.run_single_test(test_case)
            results.append(result)
            time.sleep(1)  # Small delay between requests
        
        self.test_results = results
        return results
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate test statistics"""
        if not self.test_results:
            return {}
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Category-wise statistics
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0}
            categories[category]["total"] += 1
            if result["passed"]:
                categories[category]["passed"] += 1
        
        # Calculate category accuracies
        for cat in categories:
            total = categories[cat]["total"]
            passed = categories[cat]["passed"]
            categories[cat]["accuracy"] = (passed / total * 100) if total > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "accuracy": round(accuracy, 2),
            "categories": categories,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_results_to_database(self):
        """Save test results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for result in self.test_results:
                cursor.execute(
                    """INSERT INTO evaluation_results 
                       (input_text, expected_output, actual_output, passed, confidence_score) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        result["input"],
                        json.dumps(result["expected"]),
                        json.dumps(result["actual"]) if result["actual"] else None,
                        result["passed"],
                        result["confidence"]
                    )
                )
            
            conn.commit()
            conn.close()
            print("✅ Results saved to database")
            
        except Exception as e:
            print(f"❌ Failed to save to database: {e}")
    
    def export_to_excel(self, filename: str = None) -> str:
        """Export results to Excel file"""
        if filename is None:
            filename = f"voice_crm_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Prepare data for DataFrame
        data = []
        for result in self.test_results:
            row = {
                "Test ID": result["test_id"],
                "Category": result["category"],
                "Input Text": result["input"],
                "Expected Name": result["expected"]["customer"]["full_name"],
                "Actual Name": result["actual"]["customer"]["full_name"] if result["actual"] else "",
                "Expected Phone": result["expected"]["customer"]["phone"],
                "Actual Phone": result["actual"]["customer"]["phone"] if result["actual"] else "",
                "Expected City": result["expected"]["customer"]["city"],
                "Actual City": result["actual"]["customer"]["city"] if result["actual"] else "",
                "Expected Locality": result["expected"]["customer"]["locality"],
                "Actual Locality": result["actual"]["customer"]["locality"] if result["actual"] else "",
                "Expected Summary": result["expected"]["interaction"]["summary"],
                "Actual Summary": result["actual"]["interaction"]["summary"] if result["actual"] else "",
                "Passed": "PASS" if result["passed"] else "FAIL",
                "Confidence Score": round(result["confidence"], 3),
                "Timestamp": result["timestamp"],
                "Error": result["error"] or ""
            }
            data.append(row)
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test Results', index=False)
            
            # Add statistics sheet
            stats = self.generate_statistics()
            stats_data = {
                "Metric": ["Total Tests", "Passed Tests", "Failed Tests", "Accuracy (%)"],
                "Value": [stats["total_tests"], stats["passed_tests"], stats["failed_tests"], stats["accuracy"]]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Add category-wise statistics
            if stats["categories"]:
                cat_data = []
                for cat, cat_stats in stats["categories"].items():
                    cat_data.append({
                        "Category": cat,
                        "Total Tests": cat_stats["total"],
                        "Passed Tests": cat_stats["passed"],
                        "Accuracy (%)": cat_stats["accuracy"]
                    })
                cat_df = pd.DataFrame(cat_data)
                cat_df.to_excel(writer, sheet_name='Category Statistics', index=False)
        
        print(f"✅ Results exported to {filepath}")
        return filepath
    
    def print_summary(self):
        """Print test summary to console"""
        stats = self.generate_statistics()
        
        print("\n" + "="*60)
        print("🎯 VOICE CRM EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {stats['total_tests']}")
        print(f"Passed: {stats['passed_tests']}")
        print(f"Failed: {stats['failed_tests']}")
        print(f"Overall Accuracy: {stats['accuracy']}%")
        print(f"Timestamp: {stats['timestamp']}")
        
        print("\n📊 Category-wise Results:")
        for category, cat_stats in stats["categories"].items():
            print(f"  {category}: {cat_stats['passed']}/{cat_stats['total']} ({cat_stats['accuracy']}%)")
        
        print("\n❌ Failed Tests:")
        failed_tests = [r for r in self.test_results if not r["passed"]]
        for test in failed_tests:
            print(f"  Test {test['test_id']} ({test['category']}): {test.get('error', 'Low confidence score')}")
        
        print("="*60)

def main():
    """Main function to run evaluation"""
    evaluator = VoiceCRMEvaluator()
    
    # Run tests
    results = evaluator.run_all_tests()
    
    # Save to database
    evaluator.save_results_to_database()
    
    # Export to Excel
    excel_file = evaluator.export_to_excel()
    
    # Print summary
    evaluator.print_summary()
    
    return results

if __name__ == "__main__":
    main()
