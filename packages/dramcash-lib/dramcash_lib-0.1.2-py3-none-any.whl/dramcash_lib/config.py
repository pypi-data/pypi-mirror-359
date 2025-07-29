"""
Configuration module for the Content Service App.

This module handles configuration settings and retrieves secrets from AWS Secrets Manager.
"""

import json
from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dramcash_lib.logger import logger


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
    """
    Configuration settings for the Content Service App.

    This class defines default values for various configuration parameters and validates them.
    """

    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    # Default values
    environment: str = "development"
    aws_region: str = "ap-south-1"
    secret_name: str = "DramcashURL"
    logger.info("Fetching secrets for production environment...")
    secrets = get_secret(secret_name, aws_region)
    database_uri = secrets.get("DATABASE_URI")
    database_name = secrets.get("DATABASE_NAME")
    secret_key = secrets.get("SECRET_KEY")
    aws_region = secrets.get("REGION")
    algorithm = secrets.get("ALGORITHM")
    aws_cognito_user_pool_id = secrets.get("COGNITO_POOL_ID")
    aws_cognito_app_client_id = secrets.get("COGNITO_CLIENT_ID")
    aws_cognito_app_client_secret = secrets.get("COGNITO_SECRET")
    queue_url = secrets.get("QUEUE_URL")
    logger.info("Secrets loaded successfully.")
            

    def _validate_configuration(self):
        """
        Perform pre-flight checks to validate configuration.
        """
        logger.info("Performing pre-flight checks...")
        if not self.environment:
            logger.error("ENVIRONMENT is not set.")
            raise ValueError("ENVIRONMENT is not set.")
        logger.info("[OK] ENVIRONMENT: %s", self.environment)
        if self.environment == "production" and not self.secret_name:
            logger.error("SECRET_NAME must be set for production environment.")
            raise ValueError("SECRET_NAME must be set for production environment.")
        if not self.aws_region:
            logger.error("AWS_REGION is not set.")
            raise ValueError("AWS_REGION is not set.")
        logger.info("[OK] AWS_REGION: %s", self.aws_region)
        if not self.database_name:
            logger.error("DATABASE_NAME is not set.")
            raise ValueError("DATABASE_NAME is not set.")
        logger.info("[OK] DATABASE_NAME: %s", self.database_name)
        if not self.secret_key:
            logger.error("SECRET_KEY is not set.")
            raise ValueError("SECRET_KEY is not set.")
        logger.info("[OK] SECRET_KEY: Configured.")
        if not self.algorithm:
            logger.error("ALGORITHM is not set.")
            raise ValueError("ALGORITHM is not set.")
        logger.info("[OK] ALGORITHM: %s", self.algorithm)
        logger.info("[SUCCESS] All pre-flight checks passed successfully!")


# Initialize settings
settings = Settings(environment="production")
logger.info("Configuration loaded successfully.")
logger.info("App Name: %s, App Version: %s", settings.app_name, settings.version)
logger.info("Environment: %s", settings.environment)
