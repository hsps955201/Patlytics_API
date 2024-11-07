import json
import os

from patlytics import create_app
from patlytics.database import db
from patlytics.database.models import Company, Product, Patent


def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def import_all_data():
    data_dir = os.path.join('data')

    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found at {data_dir}")
        return

    app = create_app()
    with app.app_context():
        try:
            company_data = load_json_data(
                os.path.join(data_dir, 'company_products.json'))
            if company_data and 'companies' in company_data:
                for company_data in company_data['companies']:
                    company = Company.query.filter_by(
                        name=company_data['name']).first()
                    if not company:
                        company = Company(name=company_data['name'])
                        db.session.add(company)
                        print(f"Added new company: {company_data['name']}")

                    if 'products' in company_data:
                        for product_data in company_data['products']:
                            product = Product.query.filter_by(
                                name=product_data['name']
                            ).first()

                            if not product:
                                product = Product(
                                    name=product_data['name'],
                                    description=product_data.get(
                                        'description', '')
                                )
                                db.session.add(product)
                                print(
                                    f"Added new product: {product_data['name']}")

                            if product not in company.product:
                                company.product.append(product)
                                print(
                                    f"Linked {product_data['name']} to {company_data['name']}")

            patent_data = load_json_data(
                os.path.join(data_dir, 'patents.json'))

            if patent_data:
                for patent_info in patent_data:
                    patent = Patent.query.filter_by(
                        patent_id=patent_info['id']).first()

                    if not patent:
                        patent = Patent(
                            patent_id=int(patent_info['id']),
                            title=patent_info['title']
                        )
                        db.session.add(patent)
                        print(
                            f"Added new patent: {patent_info['id']} - {patent_info['title']}")
                    else:
                        patent.title = patent_info['title']
                        print(f"Updated patent: {patent_info['id']}")

            db.session.commit()
            print("All data imported successfully!")

            print("\nImport Statistics:")
            print(f"Companies: {Company.query.count()}")
            print(f"Products: {Product.query.count()}")
            print(f"Patents: {Patent.query.count()}")

        except Exception as e:
            db.session.rollback()
            print(f"Error importing data: {e}")
            raise


def main():
    import_all_data()


if __name__ == "__main__":
    main()
