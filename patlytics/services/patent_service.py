import json
from datetime import datetime
from thefuzz import fuzz

from config import PATENTS_ALIAS, COMPANY_PRODUCTS_ALIAS
from patlytics.services.gemini_service import GeminiService
from patlytics.utils.opensearch import default_client
from patlytics.database.models import Report, Company
from patlytics.database import db


class PatentService:
    def __init__(self):
        self.opensearch_client = default_client
        self.llm_service = GeminiService()  # or OpenAIService()

    def get_patent_data(self, patent_id: str) -> dict:
        """
        Get patent data from OpenSearch or fallback to JSON file.

        Args:
            patent_id (str): ID of the patent to retrieve

        Returns:
            dict: Patent data or error message
        """
        try:
            # First try OpenSearch
            # patent = self.opensearch_client.get_document_by_id(
            #     PATENTS_ALIAS, patent_id)
            # if patent:
            #     return {
            #         "success": True,
            #         "data": {
            #             "claims": patent['claims'],
            #             "title": patent.get('title', 'Unknown Patent')
            #         }
            #     }

            # Fallback to JSON file
            with open('./data/patents.json') as f:
                patents = json.load(f)
                patent = next(
                    (p for p in patents if p['id'] == int(patent_id)), None)

            if not patent:
                return {
                    "success": False,
                    "error": "Patent ID not found.",
                    "patent_id": patent_id

                }

            return {
                "success": True,
                "data": {
                    "claims": patent['claims'],
                    "title": patent.get('title', 'Unknown Patent'),
                    "publication_number": patent.get('publication_number', '')
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get patent data: {str(e)}",
                "patent_id": patent_id
            }

    def forward_company_name(self) -> dict:
        """
        Forward company names to FE

        """
        with open('./data/company_products.json') as f:
            company_data = json.load(f)

        company_names = [company['name']
                         for company in company_data['companies']]

        return {
            "success": True,
            "data": company_names
        }

    def get_company_data(self, company_name: str, threshold: int = 80) -> dict:
        """
        Get company data with fuzzy matching.

        Args:
            company_name (str): Name of the company
            threshold (int): Minimum similarity score (0-100) for matching
        """
        try:
            with open('./data/company_products.json') as f:
                company_data = json.load(f)

            matches = []
            for company in company_data['companies']:
                ratio = fuzz.ratio(
                    company['name'].lower(), company_name.lower())
                if ratio >= threshold:
                    matches.append((company, ratio))

            matches.sort(key=lambda x: x[1], reverse=True)

            if not matches:
                return {
                    "success": False,
                    "error": "Company not found.",
                    "company_name": company_name
                }

            best_match = matches[0][0]
            return {
                "success": True,
                "data": {
                    "name": best_match['name'],
                    "products": best_match['products']
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get company data: {str(e)}",
                "company_name": company_name
            }

    def get_company_data_fuzzy(self, company_name: str) -> dict:
        """
        Get company data with fuzzy matching support.

        Args:
            company_name (str): Name of the company to search for

        Returns:
            dict: Company data or error message with fuzzy matches
        """
        try:
            # Try fuzzy search first

            matches = self.opensearch_client.fuzzy_search_company(company_name)

            if matches:
                # Return best match and alternatives
                return {
                    "success": True,
                    "data": matches[0]['data'],
                    "alternatives": [
                        {
                            "name": match['company_name'],
                            "score": match['score']
                        } for match in matches[1:3]  # Return up to 2 alternatives
                    ]
                }

            # Fallback to exact match if no fuzzy matches found
            return self.get_company_data(company_name)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get company data: {str(e)}",
                "company_name": company_name
            }

    def format_analysis_prompt(self, patent_data: dict, company_data: dict, company_name: str) -> str:
        """
        Format the prompt for LLM analysis.
        """
        products_text = "\n\n".join([
            f"Product {i+1}:\nName: {product['name']}\nDescription: {product['description']}"
            for i, product in enumerate(company_data['products'])
        ])

        return f"""
        Patent Title: {patent_data['title']}
        
        Patent Claims:
        {patent_data['claims']}
        
        Company: {company_name}
        Products to Analyze:
        {products_text}
        
        Task: Analyze each product for potential patent infringement.
        Consider:
        1. How each product might implement the patent claims
        2. The technical overlap between products and patent claims
        3. The likelihood of infringement based on available information
        
        Return a JSON array with the following structure:
        {{
            "analyses": [
                {{
                    "product_name": "name of product",
                    "infringement_likelihood": "High/Medium/Low",
                    "claims_at_issue": [list of specific claim numbers that might be infringed],
                    "explanation": "Detailed explanation of potential infringement",
                    "specific_features": "specific features of the product that might infringe the patent"
                }},
                // ... one entry for each product
            ]
            "overall_risk_assessment": "general assessment of the risk of infringement"
        }}
        """

    def check_infringement(self, patent_id: str, company_name: str) -> dict:
        """
        Check patent infringement for a company's products.
        """
        # 1. Get patent data
        patent_result = self.get_patent_data(patent_id)
        if not patent_result['success']:
            return patent_result

        patent_data = patent_result['data']

        # 2. Get company data
        company_result = self.get_company_data(company_name)
        if not company_result['success']:
            return company_result

        company_data = company_result['data']

        try:
            # 3. Create analysis prompt
            prompt = self.format_analysis_prompt(
                patent_data, company_data, company_name)

            # 4. Get analysis from LLM
            analysis_result = self.llm_service.analyze_patent(prompt)

            # 5. Process and sort results
            matches = analysis_result.get('analyses', [])
            matches.sort(key=lambda x: {
                "High": 3,
                "Medium": 2,
                "Low": 1
            }[x['infringement_likelihood']], reverse=True)
            overall_risk_assessment = analysis_result.get(
                'overall_risk_assessment', '')

            # 6. Return formatted result
            return {
                "analysis_date": datetime.now().isoformat(),
                "analysis_id": patent_id,
                "patent_id": patent_data.get('publication_number'),
                "patent_title": patent_data['title'],
                "company_name": company_name,
                "top_infringing_products": matches[:2],
                "overall_risk_assessment": overall_risk_assessment
            }

        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "patent_id": patent_id,
                "company_name": company_name
            }

    def save_analysis(self, uid: int, patent_id: int, matched_company_name: str, input_company: str, analysis: dict) -> dict:
        """
        Save analysis to Report database
        """
        company_id = None
        company = Company.query.filter_by(
            name=matched_company_name).first()
        if company:
            company_id = company.id

        new_report = Report(
            uid=uid,
            patent_id=patent_id,
            company_id=company_id,
            input_company=input_company,
            analysis_results=analysis
        )

        db.session.add(new_report)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": f"Failed to save analysis: {str(e)}"
            }

        return {
            "id": new_report.id,
            "uid": new_report.uid,
            "patent_id": new_report.patent_id,
            "company_id": new_report.company_id,
            "input_company": new_report.input_company,
            "analysis_results": new_report.analysis_results,
            "created_at": new_report.ctime,
            "updated_at": new_report.utime
        }
