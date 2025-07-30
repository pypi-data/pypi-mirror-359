# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Essencia is a comprehensive Python application framework built with Flet (Flutter for Python) that provides a foundation for building medical and business applications. It includes support for both sync and async MongoDB operations, Redis caching, advanced security features, and field-level encryption.

## Development Setup

This project uses Python 3.12+ and manages dependencies through pyproject.toml with uv as the package manager.

### Installing Dependencies

```bash
uv pip install -e .
```

### Running the Application

Since this is a Flet application, you'll typically run it as a Python module:

```bash
python -m essencia
```

## Project Structure

- `src/essencia/` - Main package directory
  - `cache/` - Intelligent caching system with Redis support
  - `core/` - Core functionality including configuration and exceptions
  - `database/` - Database connectivity (async Motor and sync PyMongo)
  - `fields/` - Custom Pydantic fields including encrypted fields
  - `models/` - Data models for both async and sync operations
  - `security/` - Comprehensive security features
  - `services/` - Service layer with base classes and mixins
  - `ui/` - Flet-based UI components
  - `utils/` - Utility functions and validators

## Key Components

### Models
- **MongoModel**: Base model for sync MongoDB operations
- **BaseModel**: Base model for async MongoDB operations
- Support for MongoId, ObjectReferenceId, and StrEnum types

### Database
- **MongoDB**: Async database operations using Motor
- **Database**: Sync database operations using PyMongo
- **RedisClient**: Redis integration for caching and sessions

### Security
- **Sanitization**: HTML/Markdown sanitizers for XSS prevention
- **Session Management**: Secure session handling with CSRF protection
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Multiple strategies for API protection
- **Encryption**: Field-level encryption for sensitive data

### Cache
- **IntelligentCache**: Smart caching with TTL management
- **AsyncCache**: Async caching operations
- Specialized caches for medical, financial, and session data

### Validators
- Brazilian data format validators (CPF, CNPJ, Phone)
- Email, Date, Money, and Password validators
- All validators provide helpful error messages in Portuguese

### Fields
- Encrypted fields for sensitive data (CPF, RG, Medical Data)
- Default date/datetime fields with timezone support
- Medical-specific encrypted fields for healthcare applications

## Key Dependencies

- **Flet**: Cross-platform UI framework (Flutter for Python)
- **Motor**: Async MongoDB driver for Python
- **PyMongo**: Sync MongoDB driver
- **Pydantic**: Data validation using Python type annotations
- **Redis/aioredis**: In-memory data structure store
- **Cryptography**: Field-level encryption support
- **Unidecode**: Text normalization for search

## Architecture Notes

The framework supports both sync and async patterns:

1. **Async Operations**: Use Motor, AsyncCache, and async services for high-performance applications
2. **Sync Operations**: Use PyMongo and sync models for simpler applications or gradual migration
3. **Security-First**: Built-in XSS protection, CSRF tokens, rate limiting, and field encryption
4. **Brazilian Market Focus**: Includes validators and formatters for Brazilian data formats

## Usage Examples

### Using Encrypted Fields
```python
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedMedicalData

class Patient(MongoModel):
    name: str
    cpf: EncryptedCPF
    medical_history: EncryptedMedicalData
```

### Using Validators
```python
from essencia.utils import CPFValidator, EmailValidator

# Validate CPF
CPFValidator.validate("123.456.789-00")  # Raises ValidationError if invalid

# Format phone number
PhoneValidator.format("11999998888")  # Returns: "(11) 99999-8888"
```

### Using Base Services
```python
from essencia.services import EnhancedBaseService
from essencia.models import MongoModel

class PatientService(EnhancedBaseService):
    model_class = Patient
    collection_name = "patients"
```

## Environment Variables

- `ESSENCIA_ENCRYPTION_KEY`: Base64-encoded encryption key for field encryption
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string

## Project Insights

- This is the core essencia package, designed to be used as a foundation for other applications
- Provides both sync and async patterns to support different use cases
- Includes comprehensive security features suitable for healthcare applications
- Supports Brazilian data formats and LGPD compliance requirements

## Memories

- Keep the local CLAUDE.MD using only English
- The package now includes components transferred from the flet-app project
- Focus on making components generic and reusable across different applications