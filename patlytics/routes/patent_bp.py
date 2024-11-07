from flask import Blueprint, request, jsonify
from patlytics.services.patent_service import PatentService
patent_bp = Blueprint('patent', __name__)


@patent_bp.route('/infringements', methods=['POST'])
def check_infringement():
    data = request.get_json()
    patent_id = data.get('patent_id')
    company_name = data.get('company_name')

    if not patent_id or not company_name:
        return jsonify({
            'error': 'Missing required parameters'
        }), 400

    service = PatentService()
    company_result = service.get_company_data_fuzzy(company_name)

    if not company_result['success']:
        return jsonify(company_result), 404

    matched_company_name = company_result['data']['name']
    infringement_result = service.check_infringement(
        patent_id, matched_company_name)

    result = {
        **infringement_result,
        'input_company': company_name,
        'matched_company': matched_company_name,
        'alternatives': company_result.get('alternatives', [])
    }

    return jsonify(result)
