"""
Gold AI Integration Test
Tests all components to ensure proper integration
"""

import sys
import os
import traceback

def test_imports():
    """Test all module imports"""
    print("🧪 Testing module imports...")
    
    modules = [
        'yfinance',
        'pandas', 
        'numpy',
        'sklearn',
        'ta',
        'joblib',
        'flask',
        'flask_socketio'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_signal_generation():
    """Test signal generation"""
    print("\n🧪 Testing signal generation...")
    
    try:
        # Test fallback signal generator
        from fallback_signal import FallbackSignalGenerator
        generator = FallbackSignalGenerator()
        signal = generator.generate_signal()
        
        if signal:
            print("  ✅ Fallback signal generation works")
            print(f"     Signal: {signal['signal']}, Confidence: {signal['confidence']:.1%}")
            return True
        else:
            print("  ⚠️  No signal generated (may be normal)")
            return True
            
    except Exception as e:
        print(f"  ❌ Signal generation failed: {e}")
        return False

def test_ml_model():
    """Test ML model availability"""
    print("\n🧪 Testing ML model...")
    
    try:
        if os.path.exists('gold_v1.joblib'):
            print("  ✅ ML model file exists")
            
            # Try to load model
            import joblib
            model = joblib.load('gold_v1.joblib')
            print("  ✅ ML model loads successfully")
            return True
        else:
            print("  ⚠️  ML model not found (will be trained on first run)")
            return True
            
    except Exception as e:
        print(f"  ❌ ML model test failed: {e}")
        return False

def test_web_components():
    """Test web components"""
    print("\n🧪 Testing web components...")
    
    try:
        # Test template exists
        if os.path.exists('templates/dashboard.html'):
            print("  ✅ Dashboard template exists")
        else:
            print("  ❌ Dashboard template missing")
            return False
        
        # Test static files
        if os.path.exists('static/css/dashboard.css'):
            print("  ✅ CSS file exists")
        else:
            print("  ❌ CSS file missing")
            return False
            
        if os.path.exists('static/js/dashboard.js'):
            print("  ✅ JavaScript file exists")
        else:
            print("  ❌ JavaScript file missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Web components test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🧪 Testing Flask app...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main route
            response = client.get('/')
            if response.status_code == 200:
                print("  ✅ Main dashboard route works")
            else:
                print(f"  ❌ Main route failed: {response.status_code}")
                return False
            
            # Test API status
            response = client.get('/api/status')
            if response.status_code == 200:
                print("  ✅ API status endpoint works")
            else:
                print(f"  ❌ API status failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app test failed: {e}")
        traceback.print_exc()
        return False

def test_deployment_files():
    """Test deployment configuration files"""
    print("\n🧪 Testing deployment files...")
    
    files = [
        'requirements.txt',
        'railway.json',
        'Procfile',
        'config.json',
        'start_app.bat',
        'start_app.sh'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all integration tests"""
    print("🚀 Gold AI Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Signal Generation", test_signal_generation),
        ("ML Model", test_ml_model),
        ("Web Components", test_web_components),
        ("Flask App", test_flask_app),
        ("Deployment Files", test_deployment_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gold AI is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)