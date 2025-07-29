"""
Helpr package initialization.
"""
__version__ = "0.2.9"

from .common_utils import validate_mobile
from .exceptions import AppException
from .format_response import jsonify_success, jsonify_failure
from .secret_manager import SecretManager
from .cache import (
    RedisHelper,
    CacheDatabase,
    BulkRedisAction,
    BulkRedisActionType
)
from .token_service import JWTHelper, TokenError, TokenMissingError, TokenExpiredError, TokenInvalidError
from .cdn import Cdn
from .logger import logger

__all__ = [
    'validate_mobile',
    'AppException',
    'jsonify_success',
    'jsonify_failure',
    'SecretManager',
    'RedisHelper',
    'CacheDatabase',
    'BulkRedisAction',
    'BulkRedisActionType',
    'JWTHelper',
    'TokenError',
    'TokenMissingError',
    'TokenExpiredError',
    'TokenInvalidError',
    'Cdn',
    'logger'
]

import logging

def get_logger(name="app"):
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

# Create default logger instance for direct import
logger = get_logger()

