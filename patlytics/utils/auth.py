from functools import wraps
from flask import request, jsonify
from patlytics.services.auth_service import AuthService
from config import SECRET_KEY

auth_service = AuthService(SECRET_KEY)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format'
                }), 401

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401

        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Token is invalid or expired'
            }), 401

        # Add user_id to kwargs
        kwargs['user_id'] = payload['user_id']
        return f(*args, **kwargs)

    return decorated
