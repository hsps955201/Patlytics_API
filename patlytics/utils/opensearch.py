import json
import ast

from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, helpers

from patlytics.opensearch_settings.patents_v1 import INDEX_SETTINGS as PATENTS_INDEX_SETTINGS
from patlytics.opensearch_settings.company_products_v1 import INDEX_SETTINGS as COMPANY_PRODUCTS_INDEX_SETTINGS
from config import OS_HOST, OS_USER, OS_PASSWORD, PATENTS_ALIAS, COMPANY_PRODUCTS_ALIAS


class OpenSearchClient:
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.client = self._create_client()

    def _create_client(self) -> OpenSearch:
        return OpenSearch(
            hosts=self.host,
            http_compress=True,
            http_auth=(self.user, self.password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )

    def put_alias_to_index(self, alias_name: str, index_name: str) -> bool:
        try:
            res = self.client.indices.put_alias(
                name=alias_name, index=index_name)
            print(f"Put alias '{alias_name}' to index '{index_name}' success")
        except Exception as e:
            print(
                f"Put alias '{alias_name}' to index '{index_name}' failed: {e}")
            return False

        return True

    def read_file(self, json_file_path: str) -> list[dict]:
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                if json_file_path == "./data/company_products.json":
                    data = data.get('companies', [])

            for post in data:
                if json_file_path == "./data/company_products.json":
                    break

                # Check if 'inventors' is a string and convert it if necessary and claims and classifications and citations
                if isinstance(post.get('inventors'), str) or \
                        isinstance(post.get('claims'), str) or \
                        isinstance(post.get('classifications'), str) or \
                        isinstance(post.get('citations'), str):
                    try:
                        # Safely evaluate the string representation to convert it to a list
                        post['inventors'] = ast.literal_eval(post['inventors'])
                        post['claims'] = ast.literal_eval(post['claims'])
                        post['classifications'] = ast.literal_eval(
                            post['classifications'])
                        post['citations'] = ast.literal_eval(post['citations'])
                    except (ValueError, SyntaxError) as e:
                        print(
                            f"Error parsing inventors for post {post.get('id')}: {e}")

                # Ensure the 'inventors' field is a list or an empty list if not
                if not isinstance(post['inventors'], list):
                    post['inventors'] = []
                if not isinstance(post['claims'], list):
                    post['claims'] = []
                if not isinstance(post['classifications'], list):
                    post['classifications'] = []
                if not isinstance(post['citations'], list):
                    post['citations'] = []

        except FileNotFoundError:
            print(f"JSON file '{json_file_path}' not found.")
            return []

        return data

    def check_alias_and_index(self, target_index: str, alias: str) -> None:
        try:
            if self.client.indices.exists_alias(name=alias):
                self.client.indices.delete_alias(
                    name=alias, index=target_index)
            else:
                print(f"Alias '{alias}' not found")

            if self.client.indices.exists(index=target_index):
                self.client.indices.delete(index=target_index)
            else:
                print(f"Index '{target_index}' not found")

        except Exception as e:
            print(e)

    def process(self, target_index: str, alias: str, index_setting: str, json_file_path: str, chunk_size: int = 100) -> int:
        try:
            self.check_alias_and_index(target_index, alias)
            self.reindex(target_index, index_setting)
            data = self.read_file(json_file_path)
            chunks = [data[i: i + chunk_size]
                      for i in range(0, len(data), chunk_size)]
            count = 0
            for chunk in chunks:
                docs = []
                for post_json in chunk:
                    doc = {
                        "_index": target_index,
                        # if json_file_path is company_products.json, then use company_name as _id
                        "_id": int(post_json["id"]) if json_file_path != "./data/company_products.json" else post_json["name"],
                    }
                    doc.update(post_json)
                    docs.append(doc)

                success, _ = helpers.bulk(self.client, docs)
                count += success
                print(f"Bulk indexed {success} documents")

            self.client.indices.refresh(index=target_index)
            self.put_alias_to_index(alias, target_index)
            return count
        except Exception as e:
            print(e)
            return 0

    def reindex(self, target_index: str, index_setting: str) -> None:
        """
        Reindex all documents from a JSON file to the target OpenSearch index.
        """
        try:
            _ = self.client.indices.get_mapping(index=target_index)
            print(f"Index '{target_index}' exists")
        except Exception as e:
            self.client.indices.create(
                index=target_index, body=index_setting)
            print(f"Index '{target_index}' created")

    def get_document_by_id(self, alias: str, doc_id: str | int, id_field: str = "_id") -> dict:
        """
        Get a document by its ID from any OpenSearch index/alias.

        Args:
            alias (str): The index alias to search in (e.g., 'patents', 'company_products')
            doc_id (str|int): The document ID to retrieve
            id_field (str, optional): The field name used as ID. Defaults to "id"

        Returns:
            dict: Document if found, empty dict if not found

        Examples:
            # Get patent
            doc = client.get_document_by_id(PATENTS_ALIAS, 72)

            # Get company product
            doc = client.get_document_by_id(COMPANY_PRODUCTS_ALIAS, "Company Name", id_field="name")
        """
        try:
            # Convert ID to int if the alias is patents (assuming patents use numeric IDs)
            if alias == PATENTS_ALIAS and isinstance(doc_id, str):
                doc_id = int(doc_id)

            response = self.client.search(
                index=alias,
                body={
                    "query": {
                        "term": {
                            id_field: doc_id
                        }
                    }
                }
            )

            hits = response['hits']['hits']
            if hits:
                return hits[0]['_source']
            return {}

        except Exception as e:
            print(
                f"Error retrieving document from {alias} with {id_field}={doc_id}: {e}")
            return {}

    def fuzzy_search_company(self, company_name: str, fuzziness: int = 2, min_score: float = 5.0) -> list[dict]:
        """
        Perform fuzzy search for company names in OpenSearch.

        Args:
            company_name (str): Company name to search for
            fuzziness (int): Maximum edit distance for fuzzy matching (default: 2)
            min_score (float): Minimum relevance score to include in results (default: 5.0)

        Returns:
            list[dict]: List of matching companies with their scores
        """
        try:
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "fuzzy": {
                                    "name": {
                                        "value": company_name,
                                        "fuzziness": fuzziness,
                                        "prefix_length": 2
                                    }
                                }
                            },
                            {
                                "match": {
                                    "name": {
                                        "query": company_name,
                                        "boost": 2.0
                                    }
                                }
                            }
                        ]
                    }
                },
                "min_score": min_score
            }

            response = self.client.search(
                index=COMPANY_PRODUCTS_ALIAS,
                body=query
            )

            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'company_name': hit['_source']['name'],
                    'score': hit['_score'],
                    'data': hit['_source']
                })

            return sorted(results, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            print(f"Error performing fuzzy search: {e}")
            return []


# Create a default instance
default_client = OpenSearchClient(OS_HOST, OS_USER, OS_PASSWORD)

if __name__ == "__main__":
    """
    Initial Data Indexing Script

    This script is used for the first-time setup of OpenSearch indices and data loading.
    It performs the following operations:
    1. Creates new indices with timestamps (e.g., patents-20240320, company_products-20240320)
    2. Loads data from JSON files into these indices
    3. Sets up aliases (PATENTS_ALIAS, COMPANY_PRODUCTS_ALIAS) to point to the new indices

    Usage:
    - Uncomment the code below when you need to:
        * Set up indices for the first time
        * Reload all data into new indices
        * Update indices with new data structure

    Example indices created:
    - patents-20240320 -> patents (alias)
    - company_products-20240320 -> company_products (alias)
    """
    # tw_datetime = datetime.utcnow().strftime("%Y%m%d")

    # Index patents data
    # patents_index = f"{PATENTS_ALIAS}-{tw_datetime}"
    # r = default_client.process(
    #     patents_index,
    #     PATENTS_ALIAS,
    #     PATENTS_INDEX_SETTINGS,
    #     "./data/patents.json"
    # )
    # print(r)

    # Index company products data
    # company_products_index = f"{COMPANY_PRODUCTS_ALIAS}-{tw_datetime}"
    # r = default_client.process(
    #     company_products_index,
    #     COMPANY_PRODUCTS_ALIAS,
    #     COMPANY_PRODUCTS_INDEX_SETTINGS,
    #     "./data/company_products.json"
    # )
    # print(r)

    # print(default_client.get_document_by_id(PATENTS_ALIAS, 4))
    # print(default_client.get_document_by_id(COMPANY_PRODUCTS_ALIAS, "iRobot"))
