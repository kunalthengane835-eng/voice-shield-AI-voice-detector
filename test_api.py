"""
Simple test script for VoiceShield API
Run this after starting the server to test the endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_signup():
    """Test user signup"""
    print("Testing signup...")
    response = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": "test@example.com",
        "password": "test123"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json() if response.status_code in [200, 201] else None

def test_login():
    """Test user login"""
    print("\nTesting login...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return result.get('token') if response.status_code == 200 else None

def test_upload(token, audio_file_path):
    """Test file upload"""
    print("\nTesting file upload...")
    headers = {"Authorization": f"Bearer {token}"}
    with open(audio_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/voice/upload", headers=headers, files=files)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return result.get('file_id') if response.status_code == 201 else None

def test_analyze(token, file_id):
    """Test voice analysis"""
    print("\nTesting voice analysis...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/voice/analyze/{file_id}", headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return result

def test_history(token):
    """Test getting analysis history"""
    print("\nTesting history...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/voice/history", headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return result

if __name__ == "__main__":
    print("VoiceShield API Test Script")
    print("=" * 50)
    
    # Test signup
    signup_result = test_signup()
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login failed. Cannot continue tests.")
        exit(1)
    
    print(f"\n✅ Login successful. Token received.")
    
    # Test file upload (you need to provide an audio file)
    # Uncomment and provide a file path to test:
    # file_id = test_upload(token, "path/to/your/audio/file.mp3")
    # if file_id:
    #     test_analyze(token, file_id)
    
    # Test history
    test_history(token)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
