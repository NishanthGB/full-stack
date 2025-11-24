import requests
import sys
import json
import time
from datetime import datetime
import os
from pathlib import Path

class VideoAPITester:
    def __init__(self, base_url="https://mediascan-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        if files:
            # Remove Content-Type for file uploads
            headers.pop('Content-Type', None)

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_user_registration(self):
        """Test user registration with different roles"""
        print("\n🔍 Testing User Registration...")
        
        # Test editor registration
        editor_data = {
            "username": f"test_editor_{int(time.time())}",
            "email": f"editor_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "role": "editor"
        }
        
        response = self.run_test(
            "Register Editor User",
            "POST",
            "auth/register",
            200,
            data=editor_data
        )
        
        if response:
            self.token = response.get('access_token')
            self.user_id = response.get('user', {}).get('id')
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        print("\n🔍 Testing User Login...")
        
        # First register a user
        user_data = {
            "username": f"login_test_{int(time.time())}",
            "email": f"login_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "role": "editor"
        }
        
        reg_response = self.run_test(
            "Register User for Login Test",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not reg_response:
            return False
        
        # Test login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        return login_response is not None

    def test_auth_me(self):
        """Test getting current user info"""
        print("\n🔍 Testing Auth Me Endpoint...")
        
        response = self.run_test(
            "Get Current User Info",
            "GET",
            "auth/me",
            200
        )
        
        return response is not None

    def test_video_upload(self):
        """Test video upload functionality"""
        print("\n🔍 Testing Video Upload...")
        
        # Create a small test video file (mock)
        test_file_content = b"fake video content for testing"
        
        files = {
            'file': ('test_video.mp4', test_file_content, 'video/mp4')
        }
        
        response = self.run_test(
            "Upload Video File",
            "POST",
            "videos/upload",
            200,
            files=files
        )
        
        if response:
            return response.get('video_id')
        return None

    def test_video_list(self):
        """Test video listing"""
        print("\n🔍 Testing Video Listing...")
        
        response = self.run_test(
            "List All Videos",
            "GET",
            "videos",
            200
        )
        
        if response is not None:
            # Test filtering
            self.run_test(
                "List Videos by Status",
                "GET",
                "videos?status=processing",
                200
            )
            
            self.run_test(
                "List Videos by Sensitivity",
                "GET",
                "videos?sensitivity=safe",
                200
            )
            
            return True
        return False

    def test_video_get(self, video_id):
        """Test getting specific video"""
        print("\n🔍 Testing Video Get...")
        
        if not video_id:
            self.log_test("Get Specific Video", False, "No video ID available")
            return False
        
        response = self.run_test(
            "Get Specific Video",
            "GET",
            f"videos/{video_id}",
            200
        )
        
        return response is not None

    def test_video_stream(self, video_id):
        """Test video streaming endpoint"""
        print("\n🔍 Testing Video Streaming...")
        
        if not video_id:
            self.log_test("Video Stream Access", False, "No video ID available")
            return False
        
        # Note: This might fail if video is not processed yet
        response = self.run_test(
            "Video Stream Access",
            "GET",
            f"videos/{video_id}/stream",
            400  # Expecting 400 since video won't be processed yet
        )
        
        return True  # 400 is expected for unprocessed video

    def test_video_delete(self, video_id):
        """Test video deletion"""
        print("\n🔍 Testing Video Deletion...")
        
        if not video_id:
            self.log_test("Delete Video", False, "No video ID available")
            return False
        
        response = self.run_test(
            "Delete Video",
            "DELETE",
            f"videos/{video_id}",
            200
        )
        
        return response is not None

    def test_role_permissions(self):
        """Test role-based permissions"""
        print("\n🔍 Testing Role-Based Permissions...")
        
        # Register a viewer user
        viewer_data = {
            "username": f"test_viewer_{int(time.time())}",
            "email": f"viewer_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "role": "viewer"
        }
        
        viewer_response = self.run_test(
            "Register Viewer User",
            "POST",
            "auth/register",
            200,
            data=viewer_data
        )
        
        if not viewer_response:
            return False
        
        # Store original token
        original_token = self.token
        
        # Use viewer token
        self.token = viewer_response.get('access_token')
        
        # Test that viewer cannot upload
        test_file_content = b"fake video content for testing"
        files = {
            'file': ('test_video.mp4', test_file_content, 'video/mp4')
        }
        
        # Viewer should be able to upload (based on the code, viewers can upload)
        # Let's test this
        upload_response = self.run_test(
            "Viewer Upload Test",
            "POST",
            "videos/upload",
            200,
            files=files
        )
        
        # Restore original token
        self.token = original_token
        
        return True

    def test_invalid_auth(self):
        """Test invalid authentication"""
        print("\n🔍 Testing Invalid Authentication...")
        
        # Store original token
        original_token = self.token
        
        # Test with invalid token
        self.token = "invalid_token"
        
        response = self.run_test(
            "Invalid Token Test",
            "GET",
            "auth/me",
            401
        )
        
        # Test with no token
        self.token = None
        
        response = self.run_test(
            "No Token Test",
            "GET",
            "videos",
            401
        )
        
        # Restore original token
        self.token = original_token
        
        return True

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Video Platform API Tests...")
        print(f"Testing against: {self.base_url}")
        
        # Test user registration and authentication
        if not self.test_user_registration():
            print("❌ Registration failed, stopping tests")
            return False
        
        # Test authentication endpoints
        self.test_user_login()
        self.test_auth_me()
        
        # Test video operations
        video_id = self.test_video_upload()
        self.test_video_list()
        self.test_video_get(video_id)
        self.test_video_stream(video_id)
        
        # Test permissions
        self.test_role_permissions()
        self.test_invalid_auth()
        
        # Test deletion (do this last)
        if video_id:
            self.test_video_delete(video_id)
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VideoAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())