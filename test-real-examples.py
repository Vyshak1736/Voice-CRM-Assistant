#!/usr/bin/env python3
"""
Real-World Test Examples for Voice CRM API
Tests the system with actual sales scenarios
"""

import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8000"

# Real-world test cases
REAL_WORLD_EXAMPLES = [
    {
        "name": "Enterprise Deal Closing",
        "text": "Met with Anil Gupta at his corporate office in Cyber City, Hyderabad. His direct line is nine one two three four five six seven eight nine zero. We signed the annual contract worth fifty lakhs and agreed on Q1 implementation start date.",
        "expected_customer": {
            "full_name": "Anil Gupta",
            "phone": "91234567890",
            "address": "corporate office in Cyber City",
            "city": "Hyderabad",
            "locality": ""
        },
        "expected_summary": "signed the annual contract worth fifty lakhs and agreed on Q1 implementation start date"
    },
    {
        "name": "SMB Lead Qualification", 
        "text": "Received inquiry from Suresh Kumar from Andheri, Mumbai. Phone nine eight seven six five four three two one zero. He runs a 20-person manufacturing business and needs inventory management solution urgently.",
        "expected_customer": {
            "full_name": "Suresh Kumar",
            "phone": "9876543210", 
            "address": "",
            "city": "Mumbai",
            "locality": "Andheri"
        },
        "expected_summary": "runs a 20-person manufacturing business and needs inventory management solution urgently"
    },
    {
        "name": "Follow-up Call",
        "text": "Followed up with Meera Reddy from Banjara Hills, Hyderabad after last week's demo. Contact double two three four five six seven eight nine zero. She confirmed budget approval and wants to proceed with proof of concept next week.",
        "expected_customer": {
            "full_name": "Meera Reddy",
            "phone": "234567890",
            "address": "",
            "city": "Hyderabad", 
            "locality": "Banjara Hills"
        },
        "expected_summary": "confirmed budget approval and wants to proceed with proof of concept next week"
    },
    {
        "name": "Cross-sell Opportunity",
        "text": "Spoke with existing client Vikram Singh from Gurgaon about our new analytics module. Phone nine nine eight eight seven seven six six five five. He's interested in adding it to his current CRM subscription for additional ten users.",
        "expected_customer": {
            "full_name": "Vikram Singh",
            "phone": "9988776655",
            "address": "",
            "city": "Gurgaon",
            "locality": ""
        },
        "expected_summary": "interested in adding it to his current CRM subscription for additional ten users"
    },
    {
        "name": "Technical Support to Sale",
        "text": "Converted support call with Ramesh Iyer from Indiranagar, Bangalore. Phone eight nine seven six five four three two one zero. Resolved his data sync issue and upsold him to premium support plan.",
        "expected_customer": {
            "full_name": "Ramesh Iyer",
            "phone": "8976543210",
            "address": "",
            "city": "Bangalore",
            "locality": "Indiranagar"
        },
        "expected_summary": "resolved his data sync issue and upsold him to premium support plan"
    }
]

def test_extraction_api(test_case):
    """Test the data extraction API with real-world examples"""
    print(f"\n🧪 Testing: {test_case['name']}")
    print(f"📝 Input: {test_case['text'][:100]}...")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/extract",
            json={"text": test_case["text"]},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract actual values
            actual_name = result.get("customer", {}).get("full_name", "")
            actual_phone = result.get("customer", {}).get("phone", "")
            actual_city = result.get("customer", {}).get("city", "")
            actual_summary = result.get("interaction", {}).get("summary", "")
            
            # Compare with expected
            expected = test_case["expected_customer"]
            
            print(f"✅ Name: {actual_name} (Expected: {expected['full_name']})")
            print(f"✅ Phone: {actual_phone} (Expected: {expected['phone']})")
            print(f"✅ City: {actual_city} (Expected: {expected['city']})")
            print(f"✅ Summary: {actual_summary[:50]}...")
            
            # Calculate accuracy
            name_match = actual_name.lower() == expected['full_name'].lower()
            phone_match = actual_phone == expected['phone']
            city_match = expected['city'].lower() in actual_city.lower()
            
            accuracy = (name_match + phone_match + city_match) / 3 * 100
            print(f"📊 Accuracy: {accuracy:.1f}%")
            
            return {
                "test_name": test_case["name"],
                "success": response.status_code == 200,
                "accuracy": accuracy,
                "result": result
            }
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return {"test_name": test_case["name"], "success": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"test_name": test_case["name"], "success": False, "error": str(e)}

def run_all_tests():
    """Run all real-world test examples"""
    print("🚀 Starting Real-World Voice CRM API Tests")
    print("=" * 60)
    
    results = []
    
    for test_case in REAL_WORLD_EXAMPLES:
        result = test_extraction_api(test_case)
        results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ Successful Tests: {len(successful_tests)}")
    print(f"❌ Failed Tests: {len(failed_tests)}")
    
    if successful_tests:
        avg_accuracy = sum(r.get("accuracy", 0) for r in successful_tests) / len(successful_tests)
        print(f"📈 Average Accuracy: {avg_accuracy:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        accuracy = result.get("accuracy", 0)
        print(f"  {status} {result['test_name']}: {accuracy:.1f}%")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Save results to file
    with open("real-world-test-results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: real-world-test-results.json")
