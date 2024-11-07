from patlytics.utils.aws_utils import get_ssm_parameter


PATENTS_ALIAS = "patents_v1"
COMPANY_PRODUCTS_ALIAS = "company_products_v1"
OS_HOST = get_ssm_parameter('/patlytics/os/host')
OS_USER = get_ssm_parameter('/patlytics/os/user')
OS_PASSWORD = get_ssm_parameter('/patlytics/os/password')
OPENAI_API_KEY = get_ssm_parameter('/patlytics/openai/api_key')
GEMINI_API_KEY = get_ssm_parameter('/patlytics/gemini/api_key')

DB_USER = get_ssm_parameter('/patlytics/db/user')
DB_PWD = get_ssm_parameter('/patlytics/db/password')
DB_HOST = get_ssm_parameter('/patlytics/db/host')
DB_PORT = get_ssm_parameter('/patlytics/db/port')
DB_NAME = get_ssm_parameter('/patlytics/db/name')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_CHARSET_SYNTAX = "charset=utf8mb4"
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?"
    f"{SQLALCHEMY_CHARSET_SYNTAX}"
)
SECRET_KEY = get_ssm_parameter('/patlytics/secret_key')

# for test
TEST_DB_NAME = get_ssm_parameter('/patlytics/db/test_name')
TEST_SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}?"
    f"{SQLALCHEMY_CHARSET_SYNTAX}"
)
