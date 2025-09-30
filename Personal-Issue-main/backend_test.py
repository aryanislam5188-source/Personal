#!/usr/bin/env python3
"""
Comprehensive backend API testing for Personal Issue App
Tests all API endpoints with realistic data and error scenarios
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://personal-issue.preview.emergentagent.com/api"

class PersonalIssueAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
        if not success:
            print(f"   Details: {response_data}")
    
    def test_health_check(self):
        """Test GET /api/ - Health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Health Check", True, "Health check endpoint working")
                return True
            else:
                self.log_test("Health Check", False, f"Health check failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Health check endpoint not implemented or server error: {str(e)}")
            return False
    
    def test_get_mock_apps(self):
        """Test GET /api/mock-apps - Get mock popular apps"""
        try:
            response = requests.get(f"{self.base_url}/mock-apps")
            if response.status_code == 200:
                apps = response.json()
                if isinstance(apps, list) and len(apps) > 0:
                    # Check if apps have required fields
                    first_app = apps[0]
                    required_fields = ["name", "package_name", "icon"]
                    if all(field in first_app for field in required_fields):
                        self.log_test("Get Mock Apps", True, f"Retrieved {len(apps)} mock apps successfully")
                        return True
                    else:
                        self.log_test("Get Mock Apps", False, "Mock apps missing required fields", first_app)
                        return False
                else:
                    self.log_test("Get Mock Apps", False, "No mock apps returned", apps)
                    return False
            else:
                self.log_test("Get Mock Apps", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Mock Apps", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_create_user(self):
        """Test POST /api/users - Create new user"""
        try:
            user_data = {
                "email": "sarah.johnson@example.com",
                "name": "Sarah Johnson"
            }
            
            response = requests.post(f"{self.base_url}/users", json=user_data)
            if response.status_code == 200:
                user = response.json()
                if "id" in user and "email" in user and "name" in user:
                    self.test_user_id = user["id"]  # Store for other tests
                    self.log_test("Create User", True, f"User created successfully with ID: {user['id']}")
                    return True
                else:
                    self.log_test("Create User", False, "User response missing required fields", user)
                    return False
            else:
                self.log_test("Create User", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create User", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_get_user(self):
        """Test GET /api/users/{user_id} - Get user details"""
        if not self.test_user_id:
            self.log_test("Get User", False, "No test user ID available")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/users/{self.test_user_id}")
            if response.status_code == 200:
                user = response.json()
                if user["id"] == self.test_user_id and "email" in user and "name" in user:
                    self.log_test("Get User", True, f"Retrieved user details successfully")
                    return True
                else:
                    self.log_test("Get User", False, "User data inconsistent", user)
                    return False
            else:
                self.log_test("Get User", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get User", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_get_user_profile(self):
        """Test GET /api/profiles/{user_id} - Get user profile"""
        if not self.test_user_id:
            self.log_test("Get User Profile", False, "No test user ID available")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/profiles/{self.test_user_id}")
            if response.status_code == 200:
                profile = response.json()
                required_fields = ["user_id", "protected_apps", "protection_state", "theme"]
                if all(field in profile for field in required_fields):
                    if profile["user_id"] == self.test_user_id:
                        self.log_test("Get User Profile", True, "Retrieved user profile successfully")
                        return True
                    else:
                        self.log_test("Get User Profile", False, "Profile user_id mismatch", profile)
                        return False
                else:
                    self.log_test("Get User Profile", False, "Profile missing required fields", profile)
                    return False
            else:
                self.log_test("Get User Profile", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get User Profile", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_add_protected_app(self):
        """Test POST /api/profiles/{user_id}/apps - Add protected app"""
        if not self.test_user_id:
            self.log_test("Add Protected App", False, "No test user ID available")
            return False
            
        try:
            app_data = {
                "name": "Instagram",
                "icon": "📷",
                "package_name": "com.instagram.android"
            }
            
            response = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/apps", json=app_data)
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "successfully" in result["message"].lower():
                    self.log_test("Add Protected App", True, "App added to protection list successfully")
                    return True
                else:
                    self.log_test("Add Protected App", False, "Unexpected response format", result)
                    return False
            else:
                self.log_test("Add Protected App", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Add Protected App", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_add_duplicate_app(self):
        """Test adding duplicate app (should fail)"""
        if not self.test_user_id:
            self.log_test("Add Duplicate App", False, "No test user ID available")
            return False
            
        try:
            app_data = {
                "name": "Instagram",
                "icon": "📷",
                "package_name": "com.instagram.android"
            }
            
            response = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/apps", json=app_data)
            if response.status_code == 400:
                self.log_test("Add Duplicate App", True, "Correctly rejected duplicate app")
                return True
            else:
                self.log_test("Add Duplicate App", False, f"Should have failed with 400, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Add Duplicate App", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_remove_protected_app(self):
        """Test DELETE /api/profiles/{user_id}/apps - Remove protected app"""
        if not self.test_user_id:
            self.log_test("Remove Protected App", False, "No test user ID available")
            return False
            
        try:
            app_data = {
                "package_name": "com.instagram.android"
            }
            
            response = requests.delete(f"{self.base_url}/profiles/{self.test_user_id}/apps", json=app_data)
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "removed" in result["message"].lower():
                    self.log_test("Remove Protected App", True, "App removed from protection list successfully")
                    return True
                else:
                    self.log_test("Remove Protected App", False, "Unexpected response format", result)
                    return False
            else:
                self.log_test("Remove Protected App", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Remove Protected App", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_set_password(self):
        """Test POST /api/profiles/{user_id}/password - Set user password"""
        if not self.test_user_id:
            self.log_test("Set Password", False, "No test user ID available")
            return False
            
        try:
            password_data = {
                "password": "secure12"
            }
            
            response = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/password", json=password_data)
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "successfully" in result["message"].lower():
                    self.log_test("Set Password", True, "Password set successfully")
                    return True
                else:
                    self.log_test("Set Password", False, "Unexpected response format", result)
                    return False
            else:
                self.log_test("Set Password", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Set Password", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_password_length_validation(self):
        """Test password length validation (max 8 chars)"""
        if not self.test_user_id:
            self.log_test("Password Length Validation", False, "No test user ID available")
            return False
            
        try:
            password_data = {
                "password": "toolongpassword123"  # More than 8 chars
            }
            
            response = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/password", json=password_data)
            if response.status_code == 400:
                self.log_test("Password Length Validation", True, "Correctly rejected password longer than 8 characters")
                return True
            else:
                self.log_test("Password Length Validation", False, f"Should have failed with 400, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Password Length Validation", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_verify_password(self):
        """Test POST /api/profiles/{user_id}/verify-password - Verify password"""
        if not self.test_user_id:
            self.log_test("Verify Password", False, "No test user ID available")
            return False
            
        try:
            # Test correct password
            password_data = {
                "password": "secure12"
            }
            
            response = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/verify-password", json=password_data)
            if response.status_code == 200:
                result = response.json()
                if "valid" in result and result["valid"] == True:
                    self.log_test("Verify Password (Correct)", True, "Password verification successful")
                    
                    # Test incorrect password
                    wrong_password_data = {
                        "password": "wrong123"
                    }
                    
                    response2 = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/verify-password", json=wrong_password_data)
                    if response2.status_code == 200:
                        result2 = response2.json()
                        if "valid" in result2 and result2["valid"] == False:
                            self.log_test("Verify Password (Incorrect)", True, "Password verification correctly rejected wrong password")
                            return True
                        else:
                            self.log_test("Verify Password (Incorrect)", False, "Should have returned valid: false", result2)
                            return False
                    else:
                        self.log_test("Verify Password (Incorrect)", False, f"Failed with status {response2.status_code}", response2.text)
                        return False
                else:
                    self.log_test("Verify Password (Correct)", False, "Should have returned valid: true", result)
                    return False
            else:
                self.log_test("Verify Password", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Verify Password", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_update_state(self):
        """Test PUT /api/profiles/{user_id}/state - Update protection state"""
        if not self.test_user_id:
            self.log_test("Update State", False, "No test user ID available")
            return False
            
        try:
            # Test state transitions: OFF -> BACKGROUND -> ACTIVE
            states_to_test = [
                {"protection_state": "BACKGROUND", "theme": "purple", "click_count": 1},
                {"protection_state": "ACTIVE", "theme": "red", "click_count": 3}
            ]
            
            for i, state_data in enumerate(states_to_test):
                response = requests.put(f"{self.base_url}/profiles/{self.test_user_id}/state", json=state_data)
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result and "successfully" in result["message"].lower():
                        self.log_test(f"Update State ({state_data['protection_state']})", True, f"State updated to {state_data['protection_state']} successfully")
                    else:
                        self.log_test(f"Update State ({state_data['protection_state']})", False, "Unexpected response format", result)
                        return False
                else:
                    self.log_test(f"Update State ({state_data['protection_state']})", False, f"Failed with status {response.status_code}", response.text)
                    return False
            
            return True
        except Exception as e:
            self.log_test("Update State", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_app_limit(self):
        """Test adding apps up to the 20 app limit"""
        if not self.test_user_id:
            self.log_test("App Limit Test", False, "No test user ID available")
            return False
            
        try:
            # Add multiple apps to test the limit
            apps_to_add = [
                {"name": "Facebook", "icon": "📘", "package_name": "com.facebook.katana"},
                {"name": "WhatsApp", "icon": "💬", "package_name": "com.whatsapp"},
                {"name": "TikTok", "icon": "🎵", "package_name": "com.zhiliaoapp.musically"},
                {"name": "YouTube", "icon": "▶️", "package_name": "com.google.android.youtube"},
                {"name": "Twitter", "icon": "🐦", "package_name": "com.twitter.android"}
            ]
            
            success_count = 0
            for app in apps_to_add:
                response = requests.post(f"{self.base_url}/profiles/{self.test_user_id}/apps", json=app)
                if response.status_code == 200:
                    success_count += 1
            
            if success_count == len(apps_to_add):
                self.log_test("App Limit Test", True, f"Successfully added {success_count} apps to protection list")
                return True
            else:
                self.log_test("App Limit Test", False, f"Only added {success_count} out of {len(apps_to_add)} apps")
                return False
                
        except Exception as e:
            self.log_test("App Limit Test", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_data_persistence(self):
        """Test that data persists correctly in MongoDB"""
        if not self.test_user_id:
            self.log_test("Data Persistence", False, "No test user ID available")
            return False
            
        try:
            # Get profile to check if all data persisted
            response = requests.get(f"{self.base_url}/profiles/{self.test_user_id}")
            if response.status_code == 200:
                profile = response.json()
                
                # Check if we have protected apps
                if len(profile.get("protected_apps", [])) > 0:
                    # Check if state is ACTIVE (from previous test)
                    if profile.get("protection_state") == "ACTIVE":
                        # Check if theme is red (from previous test)
                        if profile.get("theme") == "red":
                            # Check if click_count is 3 (from previous test)
                            if profile.get("click_count") == 3:
                                self.log_test("Data Persistence", True, "All data persisted correctly in database")
                                return True
                            else:
                                self.log_test("Data Persistence", False, f"Click count not persisted correctly: {profile.get('click_count')}")
                                return False
                        else:
                            self.log_test("Data Persistence", False, f"Theme not persisted correctly: {profile.get('theme')}")
                            return False
                    else:
                        self.log_test("Data Persistence", False, f"Protection state not persisted correctly: {profile.get('protection_state')}")
                        return False
                else:
                    self.log_test("Data Persistence", False, "Protected apps not persisted correctly")
                    return False
            else:
                self.log_test("Data Persistence", False, f"Failed to retrieve profile with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Data Persistence", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🚀 Starting Personal Issue App Backend API Tests")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in logical order
        tests = [
            self.test_health_check,
            self.test_get_mock_apps,
            self.test_create_user,
            self.test_get_user,
            self.test_get_user_profile,
            self.test_add_protected_app,
            self.test_add_duplicate_app,
            self.test_app_limit,
            self.test_remove_protected_app,
            self.test_set_password,
            self.test_password_length_validation,
            self.test_verify_password,
            self.test_update_state,
            self.test_data_persistence
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            failed_tests = [result for result in self.test_results if not result["success"]]
            print("\n❌ Failed tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = PersonalIssueAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)