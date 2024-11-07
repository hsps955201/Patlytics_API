from unittest.mock import patch, mock_open
from patlytics.tests.test_base import TestBase
from patlytics.services.patent_service import PatentService
import json


class TestPatentService(TestBase):
    def setUp(self):
        super().setUp()
        self.patent_service = PatentService()
        self.test_patent_data = [
            {
                "id": "12345",
                "title": "Test Patent",
                "claims": "Test Claims"
            }
        ]

        self.test_company_data = {
            "companies": [
                {
                    "name": "Test Company",
                    "products": [
                        {
                            "name": "Test Product",
                            "description": "Test Description"
                        }
                    ]
                }
            ]
        }

    def test_get_patent_data(self):
        """Test getting patent data"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.test_patent_data))):
            result = self.patent_service.get_patent_data("12345")

            self.assertTrue(result['success'])
            self.assertEqual(result['data']['title'], 'Test Patent')
            self.assertEqual(result['data']['claims'], 'Test Claims')

    def test_get_patent_data_not_found(self):
        """Test getting non-existent patent"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.test_patent_data))):
            result = self.patent_service.get_patent_data("99999")

            self.assertFalse(result['success'])
            self.assertIn('not found', result['error'])

    def test_get_company_data(self):
        """Test getting company data"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.test_company_data))):
            result = self.patent_service.get_company_data("Test Company")

            self.assertTrue(result['success'])
            self.assertEqual(result['data']['name'], 'Test Company')
            self.assertEqual(len(result['data']['products']), 1)
            self.assertEqual(result['data']['products']
                             [0]['name'], 'Test Product')

    def test_get_company_data_not_found(self):
        """Test getting non-existent company"""
        with patch("builtins.open", mock_open(read_data=json.dumps(self.test_company_data))):
            result = self.patent_service.get_company_data(
                "Non Existent Company")

            self.assertFalse(result['success'])
            self.assertIn('not found', result['error'])

    @patch('patlytics.services.gemini_service.GeminiService')
    def test_check_infringement(self, mock_gemini):
        """Test infringement check"""
        mock_analysis = {
            "analyses": [
                {
                    "product_name": "Test Product",
                    "infringement_likelihood": "High",
                    "claims_at_issue": [1, 2],
                    "explanation": "Test explanation"
                }
            ]
        }
        mock_gemini.return_value.analyze_patent.return_value = mock_analysis

        patent_mock = mock_open(read_data=json.dumps(self.test_patent_data))
        company_mock = mock_open(read_data=json.dumps(self.test_company_data))

        def mock_open_factory(*args, **kwargs):
            if 'patents.json' in args[0]:
                return patent_mock()
            return company_mock()

        with patch("builtins.open", mock_open_factory):
            result = self.patent_service.check_infringement(
                "12345", "Test Company")

            self.assertIn('patent_id', result)
            self.assertIn('company_name', result)
            self.assertIn('top_infringing_products', result)
            self.assertEqual(len(result['top_infringing_products']), 1)
            self.assertEqual(result['top_infringing_products']
                             [0]['product_name'], 'Test Product')
