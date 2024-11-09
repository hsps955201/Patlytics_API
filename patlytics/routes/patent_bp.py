from flask import Blueprint, request, jsonify
from patlytics.services.patent_service import PatentService
patent_bp = Blueprint('patent', __name__)


@patent_bp.route('/fuzzy_find_company', methods=['GET'])
def fuzzy_find_company():
    service = PatentService()
    result = service.forward_company_name()

    return jsonify(result)


@patent_bp.route('/infringements', methods=['POST'])
def check_infringement():
    data = request.get_json()
    patent_id = data.get('patent_id')
    input_company_name = data.get('company_name')

    if not patent_id or not input_company_name:
        return jsonify({
            'error': 'Missing required parameters'
        }), 400

    service = PatentService()
    company_result = service.get_company_data_fuzzy(input_company_name)

    if not company_result['success']:
        return jsonify(company_result), 404

    matched_company_name = company_result['data']['name']

    infringement_result = service.check_infringement(
        patent_id, matched_company_name)

    result = {
        'input_company': input_company_name,
        'matched_company': matched_company_name,
        **infringement_result
    }

    # if get uid
    uid = data.get('uid')
    if uid:
        service.save_analysis(
            uid, patent_id, matched_company_name, input_company_name, result)

    return jsonify(result)
