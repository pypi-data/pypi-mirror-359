"""
Configuration module for the Content Service App.

This module handles configuration settings and retrieves secrets from AWS Secrets Manager.
"""

import json
from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dramcash_lib.logger import logger
from typing import Dict


def get_secret(secret_name: str, aws_region: str):
    """
    Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name (str): The name of the secret to retrieve.
        aws_region (str): The AWS region where the secret is stored.

    Returns:
        dict: The secret value as a dictionary.

    Raises:
        NoCredentialsError: If AWS credentials are missing or invalid.
        ClientError: If there is an issue retrieving the secret.
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=aws_region)
    try:
        logger.info("Fetching secret '%s' from AWS Secrets Manager...", secret_name)
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            secret = response["SecretString"]
            logger.info("Secret retrieved successfully.")
            return json.loads(secret) if secret.startswith("{") else {"dbpassword": secret}
        else:
            raise ValueError("Binary secrets are not supported.")
    except NoCredentialsError:
        logger.error(
            "AWS credentials are missing or invalid. Please configure your AWS credentials."
            )
        raise
    except ClientError as e:
        logger.error("Failed to retrieve secret: %s", e)
        raise


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    # Environment config
    environment: str = "development"
    aws_region: str = "ap-south-1"
    secret_name: str = "DramcashURL"

    # Secret values (will be populated from AWS Secrets Manager)
    database_uri: str = ""
    database_name: str = ""
    secret_key: str = ""
    algorithm: str = ""
    aws_cognito_user_pool_id: str = ""
    aws_cognito_app_client_id: str = ""
    aws_cognito_app_client_secret: str = ""
    queue_url: str = ""

    # Internal
    _secrets: Dict = {}  # Marked with `_` to indicate internal use

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._secrets = get_secret(self.secret_name, self.aws_region)

        # Populate settings from secrets
        self.database_uri = self._secrets.get("DATABASE_URI", "")
        self.database_name = self._secrets.get("DATABASE_NAME", "")
        self.secret_key = self._secrets.get("SECRET_KEY", "")
        self.algorithm = self._secrets.get("ALGORITHM", "")
        self.aws_cognito_user_pool_id = self._secrets.get("COGNITO_POOL_ID", "")
        self.aws_cognito_app_client_id = self._secrets.get("COGNITO_CLIENT_ID", "")
        self.aws_cognito_app_client_secret = self._secrets.get("COGNITO_SECRET", "")
        self.queue_url = self._secrets.get("QUEUE_URL", "")

# Instantiate settings
settings = Settings()