import unittest
from unittest.mock import patch, MagicMock
from patlytics import create_app, db
import config
from sqlalchemy import create_engine, text
from patlytics.services.auth_service import AuthService


class TestBase(unittest.TestCase):
    """Base test class"""

    @classmethod
    def setUpClass(cls):
        engine = create_engine(
            f"mysql+pymysql://{config.DB_USER}:{config.DB_PWD}@"
            f"{config.DB_HOST}:{config.DB_PORT}"
        )
        with engine.connect() as conn:
            conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS {config.TEST_DB_NAME}"))

    @classmethod
    def tearDownClass(cls):
        engine = create_engine(
            f"mysql+pymysql://{config.DB_USER}:{config.DB_PWD}@"
            f"{config.DB_HOST}:{config.DB_PORT}"
        )
        with engine.connect() as conn:
            conn.execute(
                text(f"DROP DATABASE IF EXISTS {config.TEST_DB_NAME}"))

    def setUp(self):
        self.opensearch_patcher = patch(
            'patlytics.utils.opensearch.OpenSearch')
        self.mock_opensearch = self.opensearch_patcher.start()
        self.mock_os_client = MagicMock()
        self.mock_opensearch.return_value = self.mock_os_client

        self.app = create_app(testing=True)

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        current_db = db.session.get_bind().url.database

        if current_db != config.TEST_DB_NAME:
            raise Exception(
                f"Database connection error! Connected to {current_db} "
                f"instead of {config.TEST_DB_NAME}"
            )
        self.auth_service = AuthService(secret_key=config.SECRET_KEY)
        db.create_all()

    def tearDown(self):
        try:
            if db.engine.url.database == config.TEST_DB_NAME:
                for table in reversed(db.metadata.sorted_tables):
                    db.session.execute(table.delete())
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error during tearDown: {str(e)}")
            raise
        finally:
            if hasattr(self, 'opensearch_patcher'):
                self.opensearch_patcher.stop()

            db.session.remove()
            if hasattr(self, 'app_context'):
                self.app_context.pop()

    def create_test_user(self, email="test@example.com", password="password123"):
        """Helper method to create test user"""
        from patlytics.database.models import User
        user = User(email=email)
        user.hashed_password = self.auth_service.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user
