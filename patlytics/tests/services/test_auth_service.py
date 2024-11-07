from patlytics.database.models import User
from patlytics.database import db
from patlytics.tests.test_base import TestBase


class TestAuthService(TestBase):
    def setUp(self):
        super().setUp()
        self.test_user = User(email="test@example.com")
        self.test_user.hashed_password = self.auth_service.hash_password(
            "password123")
        db.session.add(self.test_user)
        db.session.commit()

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password"
        hashed = self.auth_service.hash_password(password)

        self.assertNotEqual(hashed, password)
        self.assertTrue(self.auth_service.verify_password(password, hashed))
        self.assertFalse(self.auth_service.verify_password(
            "wrong_password", hashed))

    def test_register_user_success(self):
        """Test successful user registration"""
        result = self.auth_service.register_user(
            "new@example.com", "password123")

        self.assertTrue(result['success'])
        self.assertIn('message', result)
        self.assertEqual(result['message'], 'User registered successfully')

    def test_register_user_duplicate_email(self):
        """Test registration with existing email"""
        result = self.auth_service.register_user(
            "test@example.com", "password123")

        self.assertFalse(result['success'])
        self.assertIn("already registered", result['message'].lower())

    def test_login_user_success(self):
        """Test successful login"""
        result = self.auth_service.login_user(
            "test@example.com", "password123")
        self.assertTrue(result['success'])
        self.assertIn('access_token', result['data'])

    def test_login_user_invalid_credentials(self):
        """Test login with wrong password"""
        result = self.auth_service.login_user(
            "test@example.com", "wrong_password")

        self.assertFalse(result['success'])
        self.assertIn("invalid", result['message'].lower())

    def test_refresh_token(self):
        """Test refresh token functionality"""
        login_result = self.auth_service.login_user(
            "test@example.com", "password123")
        self.assertTrue(login_result['success'])

        refresh_result = self.auth_service.refresh_access_token(
            login_result.get('data').get('refresh_token'))

        self.assertTrue(refresh_result['success'])
        self.assertIn('access_token', refresh_result['data'])

    def test_verify_token(self):
        """Test token verification"""
        login_result = self.auth_service.login_user(
            "test@example.com", "password123")
        self.assertTrue(login_result['success'])

        payload = self.auth_service.verify_token(
            login_result['data']['access_token'])
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get('user_id'), self.test_user.id)
