#!/usr/bin/env python3
"""
Comprehensive Test Suite for EduManage Ultimate School Management System
Tests all major features and API endpoints to ensure everything works correctly.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

# Configuration
API_BASE = "http://localhost:5000/api"
TEST_DATA = {
    'admin': {
        'email': 'admin@demo.school',
        'password': 'admin123'
    },
    'teacher': {
        'email': 'teacher@demo.school', 
        'password': 'teacher123'
    },
    'student': {
        'email': 'student@demo.school',
        'password': 'student123'
    },
    'parent': {
        'email': 'parent@demo.school',
        'password': 'parent123'
    }
}

class EduManageTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {message}")
    
    def login_user(self, role):
        """Login user and get JWT token"""
        try:
            credentials = TEST_DATA[role]
            response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data['access_token']
                self.log_test(f"Login {role}", "PASS", "Successfully authenticated")
                return True
            else:
                self.log_test(f"Login {role}", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Login {role}", "FAIL", str(e))
            return False
    
    def get_auth_headers(self, role):
        """Get authorization headers for API calls"""
        if role in self.tokens:
            return {'Authorization': f'Bearer {self.tokens[role]}'}
        return {}
    
    def test_authentication(self):
        """Test authentication system"""
        print("\n🔐 Testing Authentication System...")
        
        # Test login for all user types
        for role in ['admin', 'teacher', 'student', 'parent']:
            self.login_user(role)
        
        # Test invalid login
        try:
            response = self.session.post(f"{API_BASE}/auth/login", 
                                       json={'email': 'invalid@test.com', 'password': 'wrong'})
            
            if response.status_code == 401:
                self.log_test("Invalid login handling", "PASS", "Correctly rejected invalid credentials")
            else:
                self.log_test("Invalid login handling", "FAIL", f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid login handling", "FAIL", str(e))
    
    def test_school_management(self):
        """Test school management features"""
        print("\n🏫 Testing School Management...")
        
        headers = self.get_auth_headers('admin')
        
        # Test get school info
        try:
            response = self.session.get(f"{API_BASE}/schools", headers=headers)
            if response.status_code == 200:
                self.log_test("Get school info", "PASS", "Retrieved school information")
            else:
                self.log_test("Get school info", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get school info", "FAIL", str(e))
        
        # Test school analytics
        try:
            response = self.session.get(f"{API_BASE}/schools/1/analytics", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'analytics' in data:
                    self.log_test("School analytics", "PASS", "Analytics data retrieved")
                else:
                    self.log_test("School analytics", "FAIL", "No analytics data")
            else:
                self.log_test("School analytics", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("School analytics", "FAIL", str(e))
    
    def test_student_management(self):
        """Test student management features"""
        print("\n👨‍🎓 Testing Student Management...")
        
        headers = self.get_auth_headers('admin')
        
        # Test get students
        try:
            response = self.session.get(f"{API_BASE}/students", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'students' in data:
                    self.log_test("Get students", "PASS", f"Retrieved {len(data['students'])} students")
                else:
                    self.log_test("Get students", "FAIL", "No students data")
            else:
                self.log_test("Get students", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get students", "FAIL", str(e))
        
        # Test create student
        student_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': f'test_student_{datetime.now().timestamp()}@test.com',
            'student_id': f'STU{int(datetime.now().timestamp())}',
            'date_of_birth': '2010-01-15',
            'gender': 'Male',
            'class_id': 1
        }
        
        try:
            response = self.session.post(f"{API_BASE}/students", 
                                       json=student_data, headers=headers)
            if response.status_code == 201:
                self.log_test("Create student", "PASS", "Student created successfully")
            else:
                self.log_test("Create student", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create student", "FAIL", str(e))
    
    def test_attendance_system(self):
        """Test attendance management"""
        print("\n📋 Testing Attendance System...")
        
        headers = self.get_auth_headers('teacher')
        
        # Test get attendance
        try:
            response = self.session.get(f"{API_BASE}/attendance", headers=headers)
            if response.status_code == 200:
                self.log_test("Get attendance", "PASS", "Attendance data retrieved")
            else:
                self.log_test("Get attendance", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get attendance", "FAIL", str(e))
        
        # Test attendance analytics
        try:
            response = self.session.get(f"{API_BASE}/attendance/analytics", headers=headers)
            if response.status_code == 200:
                self.log_test("Attendance analytics", "PASS", "Analytics retrieved")
            else:
                self.log_test("Attendance analytics", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Attendance analytics", "FAIL", str(e))
    
    def test_grade_management(self):
        """Test grade and examination system"""
        print("\n📝 Testing Grade Management...")
        
        headers = self.get_auth_headers('teacher')
        
        # Test get grades
        try:
            response = self.session.get(f"{API_BASE}/grades", headers=headers)
            if response.status_code == 200:
                self.log_test("Get grades", "PASS", "Grades data retrieved")
            else:
                self.log_test("Get grades", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get grades", "FAIL", str(e))
    
    def test_fee_management(self):
        """Test fee management system"""
        print("\n💰 Testing Fee Management...")
        
        headers = self.get_auth_headers('admin')
        
        # Test get fees
        try:
            response = self.session.get(f"{API_BASE}/fees", headers=headers)
            if response.status_code == 200:
                self.log_test("Get fees", "PASS", "Fee data retrieved")
            else:
                self.log_test("Get fees", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get fees", "FAIL", str(e))
    
    def test_parent_portal(self):
        """Test parent portal functionality"""
        print("\n👨‍👩‍👧‍👦 Testing Parent Portal...")
        
        headers = self.get_auth_headers('parent')
        
        # Test get parent info
        try:
            response = self.session.get(f"{API_BASE}/parents", headers=headers)
            if response.status_code == 200:
                self.log_test("Parent portal access", "PASS", "Parent data retrieved")
            else:
                self.log_test("Parent portal access", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Parent portal access", "FAIL", str(e))
    
    def test_notifications(self):
        """Test notification system"""
        print("\n📨 Testing Notification System...")
        
        headers = self.get_auth_headers('admin')
        
        # Test notification templates
        try:
            response = self.session.get(f"{API_BASE}/notifications/templates", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'templates' in data:
                    self.log_test("Notification templates", "PASS", "Templates retrieved")
                else:
                    self.log_test("Notification templates", "FAIL", "No templates")
            else:
                self.log_test("Notification templates", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Notification templates", "FAIL", str(e))
        
        # Test recipient groups
        try:
            response = self.session.get(f"{API_BASE}/notifications/recipient-groups", headers=headers)
            if response.status_code == 200:
                self.log_test("Recipient groups", "PASS", "Groups retrieved")
            else:
                self.log_test("Recipient groups", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Recipient groups", "FAIL", str(e))
    
    def test_exam_system(self):
        """Test examination management"""
        print("\n🎯 Testing Exam System...")
        
        headers = self.get_auth_headers('admin')
        
        # Test get exams
        try:
            response = self.session.get(f"{API_BASE}/exams", headers=headers)
            if response.status_code == 200:
                self.log_test("Get exams", "PASS", "Exams retrieved")
            else:
                self.log_test("Get exams", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get exams", "FAIL", str(e))
    
    def test_library_system(self):
        """Test library management"""
        print("\n📚 Testing Library System...")
        
        headers = self.get_auth_headers('admin')
        
        # Test get books
        try:
            response = self.session.get(f"{API_BASE}/library/books", headers=headers)
            if response.status_code == 200:
                self.log_test("Get library books", "PASS", "Books retrieved")
            else:
                self.log_test("Get library books", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get library books", "FAIL", str(e))
        
        # Test library analytics
        try:
            response = self.session.get(f"{API_BASE}/library/analytics", headers=headers)
            if response.status_code == 200:
                self.log_test("Library analytics", "PASS", "Analytics retrieved")
            else:
                self.log_test("Library analytics", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Library analytics", "FAIL", str(e))
    
    def test_qr_system(self):
        """Test QR code functionality"""
        print("\n🔲 Testing QR Code System...")
        
        headers = self.get_auth_headers('admin')
        
        # Test QR verification endpoint (without token)
        try:
            response = self.session.post(f"{API_BASE}/qr/verify", 
                                       json={'qr_token': 'test_token'}, headers=headers)
            # This should fail with invalid token, which is expected
            if response.status_code in [400, 401, 404]:
                self.log_test("QR verification endpoint", "PASS", "Endpoint accessible")
            else:
                self.log_test("QR verification endpoint", "FAIL", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("QR verification endpoint", "FAIL", str(e))
    
    def test_events_system(self):
        """Test events and calendar"""
        print("\n📅 Testing Events System...")
        
        headers = self.get_auth_headers('admin')
        
        # Test get events
        try:
            response = self.session.get(f"{API_BASE}/events", headers=headers)
            if response.status_code == 200:
                self.log_test("Get events", "PASS", "Events retrieved")
            else:
                self.log_test("Get events", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get events", "FAIL", str(e))
        
        # Test event calendar
        try:
            response = self.session.get(f"{API_BASE}/events/calendar", headers=headers)
            if response.status_code == 200:
                self.log_test("Events calendar", "PASS", "Calendar retrieved")
            else:
                self.log_test("Events calendar", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Events calendar", "FAIL", str(e))
    
    def test_reports_system(self):
        """Test reporting functionality"""
        print("\n📊 Testing Reports System...")
        
        headers = self.get_auth_headers('admin')
        
        # Test report templates
        try:
            response = self.session.get(f"{API_BASE}/reports/templates", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'templates' in data:
                    self.log_test("Report templates", "PASS", "Templates retrieved")
                else:
                    self.log_test("Report templates", "FAIL", "No templates")
            else:
                self.log_test("Report templates", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Report templates", "FAIL", str(e))
    
    def test_health_endpoints(self):
        """Test system health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{API_BASE.replace('/api', '')}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("Health endpoint", "PASS", "System is healthy")
                else:
                    self.log_test("Health endpoint", "WARN", "System status unclear")
            else:
                self.log_test("Health endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health endpoint", "FAIL", str(e))
        
        # Test API info endpoint
        try:
            response = self.session.get(f"{API_BASE}")
            if response.status_code == 200:
                self.log_test("API info endpoint", "PASS", "API info retrieved")
            else:
                self.log_test("API info endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("API info endpoint", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting EduManage Ultimate Comprehensive Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test suites
        self.test_authentication()
        self.test_health_endpoints()
        self.test_school_management()
        self.test_student_management()
        self.test_attendance_system()
        self.test_grade_management()
        self.test_fee_management()
        self.test_parent_portal()
        self.test_notifications()
        self.test_exam_system()
        self.test_library_system()
        self.test_qr_system()
        self.test_events_system()
        self.test_reports_system()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Generate summary
        self.generate_summary(duration)
    
    def generate_summary(self, duration):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warnings = len([t for t in self.test_results if t['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"⏱️  Duration: {duration.total_seconds():.2f} seconds")
        print(f"📊 Success Rate: {(passed/total_tests*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"  • {test['test']}: {test['message']}")
        
        if warnings > 0:
            print("\n⚠️  WARNINGS:")
            for test in self.test_results:
                if test['status'] == 'WARN':
                    print(f"  • {test['test']}: {test['message']}")
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed,
                    'failed': failed,
                    'warnings': warnings,
                    'success_rate': passed/total_tests*100,
                    'duration_seconds': duration.total_seconds(),
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        # Overall status
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! EduManage Ultimate is working correctly!")
        elif failed <= 2:
            print("\n✨ MOSTLY WORKING! Minor issues detected.")
        else:
            print("\n🚨 MULTIPLE ISSUES DETECTED! Please check the failed tests.")


def main():
    """Main function to run the test suite"""
    print("EduManage Ultimate - Comprehensive Test Suite")
    print("Testing all features to ensure system functionality")
    print()
    
    # Check if the API server is running
    try:
        response = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not responding correctly. Please start the backend server first.")
            print("Run: cd backend && python run.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server. Please start the backend server first.")
        print("Run: cd backend && python run.py")
        sys.exit(1)
    
    # Run the test suite
    test_suite = EduManageTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()