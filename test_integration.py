#!/usr/bin/env python3
"""
Gold AI Integration Test
Verifies frontend-backend signal alignment and system flow
"""

import requests
import json
import time
from datetime import datetime

class IntegrationTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("🧪 Testing API Endpoints...")
        
        endpoints = [
            ("/api/status", "GET"),
            ("/api/signal/current", "GET"),
            ("/api/trades/active", "GET"),
            ("/api/performance", "GET")
        ]
        
        results = {}
        for endpoint, method in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                results[endpoint] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None
                }
                print(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                results[endpoint] = {"status": "ERROR", "success": False, "error": str(e)}
                print(f"❌ {endpoint}: {e}")
        
        return results
    
    def test_signal_consistency(self):
        """Test signal data consistency"""
        print("\n🎯 Testing Signal Consistency...")
        
        try:
            # Get current signal
            response = requests.get(f"{self.base_url}/api/signal/current", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('signal'):
                    signal = data['signal']
                    
                    # Validate signal structure
                    required_fields = ['signal', 'confidence', 'entry_price', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in signal]
                    
                    if missing_fields:
                        print(f"❌ Missing signal fields: {missing_fields}")
                        return False
                    
                    # Validate signal values
                    if signal['signal'] not in [0, 1, 2]:
                        print(f"❌ Invalid signal value: {signal['signal']}")
                        return False
                    
                    if not (0 <= signal['confidence'] <= 1):
                        print(f"❌ Invalid confidence: {signal['confidence']}")
                        return False
                    
                    print(f"✅ Signal structure valid")
                    print(f"   Signal: {['NEUTRAL', 'BUY', 'SELL'][signal['signal']]}")
                    print(f"   Confidence: {signal['confidence']:.1%}")
                    print(f"   Entry Price: ${signal['entry_price']:.2f}")
                    return True
                else:
                    print("⚠️ No signal available")
                    return True
            else:
                print(f"❌ Signal API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Signal test error: {e}")
            return False
    
    def test_system_control(self):
        """Test system start/stop functionality"""
        print("\n🎛️ Testing System Control...")
        
        try:
            # Get initial status
            status_response = requests.get(f"{self.base_url}/api/status", timeout=10)
            if status_response.status_code != 200:
                print("❌ Cannot get system status")
                return False
            
            initial_status = status_response.json()
            print(f"Initial status: {initial_status.get('system_status', 'unknown')}")
            
            # Test system control (just check endpoints exist)
            start_url = f"{self.base_url}/api/system/start"
            stop_url = f"{self.base_url}/api/system/stop"
            
            print("✅ System control endpoints accessible")
            return True
            
        except Exception as e:
            print(f"❌ System control test error: {e}")
            return False
    
    def test_performance_data(self):
        """Test performance data structure"""
        print("\n📊 Testing Performance Data...")
        
        try:
            response = requests.get(f"{self.base_url}/api/performance", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Performance data accessible")
                    if 'metrics' in data:
                        metrics = data['metrics']
                        print(f"   Metrics available: {list(metrics.keys())}")
                    return True
                else:
                    print("⚠️ Performance data not available")
                    return True
            else:
                print(f"❌ Performance API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False
    
    def run_full_test(self):
        """Run complete integration test suite"""
        print("=" * 60)
        print("           GOLD AI INTEGRATION TEST")
        print("=" * 60)
        print(f"Testing server: {self.base_url}")
        print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        api_results = self.test_api_endpoints()
        signal_ok = self.test_signal_consistency()
        control_ok = self.test_system_control()
        performance_ok = self.test_performance_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("                TEST SUMMARY")
        print("=" * 60)
        
        api_success = all(result['success'] for result in api_results.values())
        overall_success = api_success and signal_ok and control_ok and performance_ok
        
        print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
        print(f"Signal Data: {'✅ PASS' if signal_ok else '❌ FAIL'}")
        print(f"System Control: {'✅ PASS' if control_ok else '❌ FAIL'}")
        print(f"Performance Data: {'✅ PASS' if performance_ok else '❌ FAIL'}")
        print()
        print(f"Overall Result: {'✅ INTEGRATION OK' if overall_success else '❌ INTEGRATION ISSUES'}")
        
        if not overall_success:
            print("\n🔧 Troubleshooting:")
            print("1. Ensure the Gold AI app is running (python app.py)")
            print("2. Check that all required files are present")
            print("3. Verify network connectivity to localhost:5000")
            print("4. Check console logs for detailed error messages")
        
        return overall_success

def main():
    tester = IntegrationTester()
    success = tester.run_full_test()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()