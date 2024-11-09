import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from patlytics.database import db
from patlytics.database.models import User


class AuthService:
    def __init__(self, secret_key: str, access_token_expire_minutes: int = 30, refresh_token_expire_days: int = 7):
        self.secret_key = secret_key
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def register_user(self, email: str, password: str) -> dict:
        """Register a new user"""
        try:
            # Check if user exists
            if User.query.filter_by(email=email).first():
                return {
                    'success': False,
                    'message': 'Email already registered'
                }

            # Create new user
            hashed_password = self.hash_password(password)
            user = User(
                email=email,
                hashed_password=hashed_password
            )

            db.session.add(user)
            db.session.commit()

            access_token, refresh_token = self.generate_tokens(user.id)
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }

    def generate_tokens(self, user_id: int) -> Tuple[str, str]:
        """Generate both access and refresh tokens"""
        # Generate access token
        access_token_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'type': 'access'
        }
        access_token = jwt.encode(
            access_token_payload, self.secret_key, algorithm='HS256')

        # Generate refresh token
        refresh_token_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            refresh_token_payload, self.secret_key, algorithm='HS256')

        return access_token, refresh_token

    def verify_token(self, token: str, token_type: str = 'access') -> Optional[dict]:
        """Verify token and check its type"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload['type'] != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def login_user(self, email: str, password: str) -> dict:
        """Login user and return both tokens"""
        try:
            user = User.query.filter_by(email=email).first()

            if not user or not self.verify_password(password, user.hashed_password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }

            # Generate both tokens
            access_token, refresh_token = self.generate_tokens(user.id)

            return {
                'success': True,
                'message': 'Login successful',
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user.id,
                        'email': user.email
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Generate new access token using refresh token"""
        payload = self.verify_token(refresh_token, token_type='refresh')
        if not payload:
            return {
                'success': False,
                'message': 'Invalid or expired refresh token'
            }

        # Generate new access token
        access_token_payload = {
            'user_id': payload['user_id'],
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'type': 'access'
        }
        new_access_token = jwt.encode(
            access_token_payload, self.secret_key, algorithm='HS256')

        return {
            'success': True,
            'data': {
                'access_token': new_access_token
            }
        }
