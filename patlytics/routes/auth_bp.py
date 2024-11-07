from flask import Blueprint, request, jsonify
from patlytics.services.auth_service import AuthService
from patlytics.utils.auth import token_required
from config import SECRET_KEY
from patlytics.database.models import User

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService(SECRET_KEY)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Missing email or password'
        }), 400

    result = auth_service.register_user(email, password)

    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Missing email or password'
        }), 400

    result = auth_service.login_user(email, password)

    if result['success']:
        return jsonify(result)
    return jsonify(result), 401


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_user_info(user_id: int):
    """Get current user info"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404

    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user.id,
                'email': user.email,
                'reports': [report.to_dict() for report in user.reports]
            }
        }
    })


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    refresh_token = None
    auth_header = request.headers.get('Authorization')

    if auth_header:
        try:
            refresh_token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({
                'success': False,
                'message': 'Invalid token format'
            }), 401

    if not refresh_token:
        return jsonify({
            'success': False,
            'message': 'Refresh token is missing'
        }), 401

    result = auth_service.refresh_access_token(refresh_token)

    if result['success']:
        return jsonify(result)
    return jsonify(result), 401
