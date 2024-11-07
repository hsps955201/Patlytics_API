import json
from datetime import datetime

from config import PATENTS_ALIAS, COMPANY_PRODUCTS_ALIAS
from patlytics.services.gemini_service import GeminiService
from patlytics.utils.opensearch import default_client
from thefuzz import fuzz


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
                    (p for p in patents if p['id'] == patent_id), None)

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
                    "title": patent.get('title', 'Unknown Patent')
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get patent data: {str(e)}",
                "patent_id": patent_id
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
                    "explanation": "Detailed explanation of potential infringement"
                }},
                // ... one entry for each product
            ]
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

            # 6. Return formatted result
            return {
                "patent_id": patent_id,
                "patent_title": patent_data['title'],
                "company_name": company_name,
                "top_infringing_products": matches[:2],
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "patent_id": patent_id,
                "company_name": company_name
            }
