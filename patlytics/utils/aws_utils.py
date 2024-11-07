import boto3


def get_ssm_parameter(param_name: str, decrypt: bool = True) -> str:
    """Get parameter from AWS SSM Parameter Store"""
    ssm = boto3.client('ssm', region_name='ap-northeast-1')
    response = ssm.get_parameter(
        Name=param_name,
        WithDecryption=decrypt
    )
    return response['Parameter']['Value']
