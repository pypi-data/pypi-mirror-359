"""Essencia - A modern Python application framework."""

from essencia.core import Config, EssenciaException
from essencia.models import (
    # Async models
    User, UserCreate, UserUpdate, Session,
    # Sync models and base classes
    MongoModel, MongoId, ObjectReferenceId, StrEnum
)
from essencia.database import MongoDB, RedisClient, Database
from essencia.services import (
    UserService, AuthService, SessionService,
    BaseService, EnhancedBaseService
)
from essencia.ui import EssenciaApp
from essencia.security import (
    # Sanitization
    HTMLSanitizer,
    MarkdownSanitizer,
    sanitize_input,
    sanitize_name,
    sanitize_email,
    sanitize_phone,
    sanitize_cpf,
    # Session Management
    SessionManager,
    get_session_manager,
    create_secure_session,
    validate_current_session,
    destroy_current_session,
    # Authorization
    Role,
    Permission,
    PermissionManager,
    get_permission_manager,
    require_admin,
    require_medical_role,
    require_financial_access,
    # Rate Limiting
    RateLimiter,
    get_rate_limiter,
    rate_limit_login,
    rate_limit_api,
    # Encryption
    encrypt_cpf,
    decrypt_cpf,
    encrypt_medical_data,
    decrypt_medical_data,
)
from essencia.cache import IntelligentCache, AsyncCache
from essencia.utils import (
    CPFValidator,
    CNPJValidator,
    PhoneValidator,
    EmailValidator,
    DateValidator,
    MoneyValidator,
    PasswordValidator,
)
from essencia.fields import (
    EncryptedStr,
    EncryptedCPF,
    EncryptedRG,
    EncryptedMedicalData,
    DefaultDate,
    DefaultDateTime,
)

__version__ = "1.1.0"

__all__ = [
    # Core
    "Config",
    "EssenciaException",
    # Models - Async
    "User",
    "UserCreate",
    "UserUpdate",
    "Session",
    # Models - Sync and Base
    "MongoModel",
    "MongoId",
    "ObjectReferenceId",
    "StrEnum",
    # Database
    "MongoDB",
    "RedisClient",
    "Database",
    # Services
    "UserService",
    "AuthService",
    "SessionService",
    "BaseService",
    "EnhancedBaseService",
    # UI
    "EssenciaApp",
    # Cache
    "IntelligentCache",
    "AsyncCache",
    # Security - Sanitization
    "HTMLSanitizer",
    "MarkdownSanitizer",
    "sanitize_input",
    "sanitize_name",
    "sanitize_email",
    "sanitize_phone",
    "sanitize_cpf",
    # Security - Session Management
    "SessionManager",
    "get_session_manager",
    "create_secure_session",
    "validate_current_session",
    "destroy_current_session",
    # Security - Authorization
    "Role",
    "Permission",
    "PermissionManager",
    "get_permission_manager",
    "require_admin",
    "require_medical_role",
    "require_financial_access",
    # Security - Rate Limiting
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit_login",
    "rate_limit_api",
    # Security - Encryption
    "encrypt_cpf",
    "decrypt_cpf",
    "encrypt_medical_data",
    "decrypt_medical_data",
    # Utils - Validators
    "CPFValidator",
    "CNPJValidator",
    "PhoneValidator",
    "EmailValidator",
    "DateValidator",
    "MoneyValidator",
    "PasswordValidator",
    # Fields
    "EncryptedStr",
    "EncryptedCPF",
    "EncryptedRG",
    "EncryptedMedicalData",
    "DefaultDate",
    "DefaultDateTime",
]
