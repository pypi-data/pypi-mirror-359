`````instructions
<SYSTEM>
You are an AI programming assistant that is specialized in applying code changes to an existing document.
Follow Microsoft content policies.
Avoid content that violates copyrights.
If you are asked to generate content that is harmful, hateful, racist, sexist, lewd, violent, or completely irrelevant to software engineering, only respond with "Sorry, I can't assist with that."
Keep your answers short and impersonal.
The user has a code block that represents a suggestion for a code change and a instructions file opened in a code editor.
Rewrite the existing document to fully incorporate the code changes in the provided code block.
For the response, always follow these instructions:
1. Analyse the code block and the existing document to decide if the code block should replace existing code or should be inserted.
2. If necessary, break up the code block in multiple parts and insert each part at the appropriate location.
3. Preserve whitespace and newlines right after the parts of the file that you modify.
4. The final result must be syntactically valid, properly formatted, and correctly indented. It should not contain any ...existing code... comments.
5. Finally, provide the fully rewritten file. You must output the complete file.
</SYSTEM>

# 🤖 LINE API Integration Library - AI Agent Context

## Project Overview

**LINE API Integration Library** is a comprehensive, type-safe Python library for integrating with LINE's APIs. It provides modern async/await patterns, full Pydantic type safety, and covers all major LINE platform features including Messaging API, Flex Messages, Rich Menus, LINE Login, LIFF, and Mini Apps.

## 🎯 Core Purpose

- **Comprehensive LINE Integration**: One library for all LINE platform APIs
- **Type Safety**: Full Pydantic integration with comprehensive type hints
- **Modern Async**: Built for high-performance async/await operations
- **Developer Experience**: Rich IDE support, auto-completion, and detailed documentation
- **Production Ready**: Comprehensive testing, error handling, and best practices
- **Extensible Architecture**: Modular design for easy feature additions

## 🏗️ Architecture & Tech Stack

### Core Framework

- **Python 3.11+**: Modern Python with enhanced type hints and performance
- **Async-First Design**: All I/O operations use async/await patterns
- **Pydantic 2.x**: Data validation, settings management, and type safety
- **Official LINE SDK**: Built on top of `line-bot-sdk` for reliability
- **HTTPX**: Modern async HTTP client for external API calls

### Dependencies & Package Management

- **Core**: `line-bot-sdk>=3.17.0`, `pydantic>=2.8.0`, `httpx>=0.27.0`
- **Web Framework**: `fastapi>=0.111.0`, `uvicorn>=0.30.0`
- **Development**: `pytest>=8.3.0`, `mypy>=1.11.0`, `ruff>=0.5.0`
- **Package Management**:
  - Using `uv` for fast, reliable Python package management
  - All dependencies managed via `uv sync`
  - Development setup with `uv sync --dev`
  - Virtual environments handled by `uv venv`

### Design Principles

- **Single Responsibility**: Each module has a clear, focused purpose
- **Type Safety**: Full type hints throughout with Pydantic validation
- **Error Handling**: Comprehensive error handling with typed exceptions
- **Async-First**: All I/O operations use async/await patterns
- **Modular Architecture**: Clean separation between different LINE API services

## 📁 Project Structure

```
line-api/
├── .github/copilot-instructions.md # This file - AI agent context
├── README.md                       # User documentation and usage examples
├── pyproject.toml                  # Dependencies and tool configurations
├── line-api.code-workspace         # VS Code workspace configuration
├── line_api/                       # Main package directory
│   ├── core/                       # Core configuration and utilities
│   ├── messaging/                  # LINE Messaging API implementation
│   ├── webhook/                    # Webhook handling and event processing
│   ├── flex_messages/              # Flex Message components and utilities
│   ├── rich_menu/                  # Rich Menu management
│   ├── login/                      # LINE Login OAuth2 integration
│   └── liff/                       # LIFF app lifecycle management
├── tests/                          # 🧪 Comprehensive Test Suite
│   ├── __init__.py
│   ├── test_messaging.py           # Messaging API tests
│   ├── test_webhook.py             # Webhook processing tests
│   ├── test_flex_messages.py       # Flex Messages tests
│   └── ...                         # Additional test modules
├── examples/                       # 📚 Usage Examples
│   ├── webhook_example.py          # FastAPI webhook handler
│   ├── flex_message_example.py     # Flex Message creation
│   └── push_message_example.py     # Basic message sending
├── docs/                           # 📖 Documentation
│   ├── WEBHOOK_SETUP.md            # Webhook setup guide
│   ├── api/                        # API reference documentation
│   ├── guides/                     # Usage guides and tutorials
│   └── examples/                   # Detailed examples
├── scripts/                        # 🔧 Development Scripts
│   └── ...                         # API testing script
└── debug/                          # 🐛 Debug Scripts (gitignored)
    └── ...                         # Temporary debug and investigation scripts
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# LINE Bot Configuration (for Messaging API)
LINE_CHANNEL_ACCESS_TOKEN=your_line_bot_token
LINE_CHANNEL_SECRET=your_line_bot_secret

# LINE Login Configuration (optional)
LINE_API_LOGIN_CHANNEL_ID=your_login_channel_id
LINE_API_LOGIN_CHANNEL_SECRET=your_login_channel_secret

# LIFF Configuration (optional)
LINE_API_LIFF_CHANNEL_ID=your_liff_channel_id

# Development Configuration
LINE_API_DEBUG=true
LINE_API_TIMEOUT=30
LINE_API_MAX_RETRIES=3
```

### Configuration Loading

- **Automatic Discovery**: Searches for `.env` file in current directory and parent directories
- **Environment Override**: Environment variables override `.env` file values
- **Pydantic Validation**: All configuration validated with Pydantic models
- **Type Safety**: Full type hints and validation for all settings

## 🚀 Core Modules

### 1. Core Configuration (`core/`)

**Purpose**: Centralized configuration management using Pydantic Settings

**Key Features**:

- Automatic `.env` file discovery and loading
- Environment variable validation with Pydantic
- Type-safe configuration across all services
- Secure credential management

**Usage**:

```python
from line_api.core import LineAPIConfig

# Automatic .env loading and validation
config = LineAPIConfig()

# Access configuration with type safety
print(f"Channel ID: {config.line_channel_access_token}")
print(f"Timeout: {config.line_api_timeout}")
```


### 2. Messaging API (`messaging/`)

**Purpose**: Complete LINE Messaging API implementation with webhook support

**Key Features**:

- Full Messaging API coverage (reply, push, multicast, broadcast)
- Webhook parser with signature verification
- User profile management
- Message validation and error handling
- Rate limiting and retry mechanisms

**Usage**:

```python
from line_api import LineMessagingClient, LineAPIConfig, TextMessage

async with LineMessagingClient(LineAPIConfig()) as client:
    await client.push_message("USER_ID", [TextMessage(text="Hello!")])
```

### 3. Webhook Processing (`webhook/`)

**Purpose**: Complete webhook handling for LINE Platform events

**Key Features**:

- Type-safe webhook event models with Pydantic validation
- Signature verification utilities for security
- Flexible event handler system with decorators
- Comprehensive error handling and logging
- Support for all LINE webhook event types

**Usage**:

```python
from line_api.webhook import LineWebhookHandler
from fastapi import FastAPI, Request

handler = LineWebhookHandler(config)

@handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    # Process message events
    pass

@app.post("/webhook")
async def webhook(request: Request):
    return await handler.handle_webhook(
        await request.body(),
        request.headers.get("X-Line-Signature"),
        await request.json()
    )
```



### 4. Flex Messages (`flex_messages/`)

**Purpose**: Type-safe Flex Message creation with Pydantic models

**Key Features**:

- Complete Flex Message component support (FlexBox, FlexBubble, FlexText, etc.)
- Type-safe creation with Pydantic validation
- JSON export for LINE simulator testing
- Automatic clipboard copy functionality
- No deprecated components (FlexSpacer removed)
- Custom component creation with factory methods

**Usage**:

```python
from line_api.flex_messages import (
    FlexBox, FlexBubble, FlexLayout, FlexMessage, FlexText,
    print_flex_json, export_flex_json
)

# Create components
title = FlexText.create("Welcome!", weight="bold", size="xl")
body = FlexBox.create(layout=FlexLayout.VERTICAL, contents=[title])
bubble = FlexBubble.create(body=body)
message = FlexMessage.create(alt_text="Welcome", contents=bubble)

# Export for testing
print_flex_json(message, "My Message")  # Auto-copies to clipboard
export_flex_json(message, "welcome.json")  # Save to file
```
### 5. Rich Menu Management (`rich_menu/`)

**Purpose**: Complete Rich Menu lifecycle management

**Key Features**:

- Rich Menu creation and management
- Image upload and validation
- User-specific rich menu assignment
- Template system for common layouts
- Bulk operations for multiple users

**Usage**:

```python
from line_api.rich_menu import RichMenuClient

async with RichMenuClient(config) as client:
    # Create and upload rich menu
    rich_menu_id = await client.create_rich_menu(
        name="Main Menu",
        areas=[...],  # Define menu areas
        chat_bar_text="Open Menu"
    )
    
    # Set as default for all users
    await client.set_default_rich_menu(rich_menu_id)
```



### 6. LINE Login (`login/`)

**Purpose**: OAuth2 authentication and user management

**Key Features**:

- Complete OAuth2 flow implementation
- User profile management
- Token validation and refresh
- Scope management
- Secure token storage patterns

**Usage**:

```python
from line_api.login import LineLoginClient

async with LineLoginClient(config) as client:
    # Generate OAuth2 authorization URL
    auth_url = await client.get_authorization_url(
        redirect_uri="https://your-app.com/callback",
        scope=["profile", "openid"]
    )
    
    # Exchange authorization code for tokens
    tokens = await client.exchange_code(
        code="auth_code_from_callback",
        redirect_uri="https://your-app.com/callback"
    )
    
    # Get user profile
    profile = await client.get_profile(tokens.access_token)
```



### 7. LIFF Management (`liff/`)

**Purpose**: LIFF (LINE Front-end Framework) app management

**Key Features**:

- LIFF app creation and management
- View configuration and updates
- App lifecycle management
- Integration with web applications

**Usage**:

```python
from line_api.liff import LIFFClient

async with LIFFClient(config) as client:
    # Create a new LIFF app
    liff_id = await client.create_liff_app(
        view_type="full",
        view_url="https://your-app.com/liff"
    )
    
    # Update LIFF app configuration
    await client.update_liff_app(
        liff_id=liff_id,
        view_url="https://your-app.com/liff/updated"
    )
```



## 🧪 Testing Strategy

### Test Infrastructure

**Testing Framework**: pytest with pytest-asyncio for async support

**Test Categories**:
- **Unit Tests**: Individual function and method testing with mocking
- **Integration Tests**: End-to-end testing with real LINE API responses
- **Mock Tests**: Complete API interaction testing with controlled responses
- **Edge Case Tests**: Error conditions, rate limits, and boundary conditions

**Test Structure**:
```python
# tests/test_messaging.py example
@pytest.mark.asyncio
async def test_multicast_message_success():
    """Test successful multicast message sending."""
    # Arrange: Setup mock client and data
    # Act: Call the function
    # Assert: Verify expected behavior
```

**Coverage Requirements**:
- Minimum 90% overall code coverage
- 100% coverage for public APIs
- All error conditions must be tested
- All LINE API edge cases covered



## ⚠️ AI Agent File Deletion Limitation

When using AI models such as GPT-4.1, GPT-4o, or any model that cannot directly delete files, be aware of the following workflow limitation:

- **File Deletion Restriction**: The AI model cannot perform destructive actions like deleting files from the filesystem. Its capabilities are limited to editing file contents only.
- **User Action Required**: If you need to remove a file, the AI will provide the appropriate terminal command (e.g., `rm /path/to/file.py`) for you to run manually.
- **Safety Rationale**: This restriction is in place to prevent accidental or unauthorized file deletion and to ensure user control over destructive actions.
- **Workflow Guidance**: Always confirm file removal by running the suggested command in your terminal or file manager.

## 🤖 AI Agent Instructions - STRICT COMPLIANCE REQUIRED

**CRITICAL**: All AI agents working on this project MUST follow these instructions precisely. Deviation from these guidelines is not permitted.

### 🚨 MANDATORY PRE-WORK VALIDATION

Before making ANY changes:

1. **ALWAYS** read the current file contents completely before editing
2. **ALWAYS** run existing tests to ensure no regressions: `python -m pytest tests/ -v`
3. **ALWAYS** check git status and current branch before making changes
4. **ALWAYS** validate that your changes align with the project architecture

### 🎯 CORE ARCHITECTURAL PRINCIPLES - NON-NEGOTIABLE

1. **Type Safety is MANDATORY**:
   - ALL functions MUST have complete type annotations
   - ALL data structures MUST use Pydantic models
   - ALL inputs and outputs MUST be validated
   - NO `Any` types without explicit justification
   - NO missing type hints on public APIs

2. **Async-First Architecture is REQUIRED**:
   - ALL I/O operations MUST use async/await patterns
   - ALL HTTP clients MUST be async (httpx, not requests)
   - ALL database operations MUST be async
   - Context managers MUST be used for resource management

3. **Pydantic Integration is MANDATORY**:
   - ALL configuration MUST use Pydantic Settings
   - ALL API request/response models MUST use Pydantic
   - ALL validation MUST use Pydantic validators
   - Field descriptions and constraints are REQUIRED

4. **Error Handling Must Be Comprehensive**:
   - ALL exceptions MUST be typed and specific
   - ALL external API calls MUST have retry mechanisms
   - ALL errors MUST be logged with structured data
   - User-facing error messages MUST be helpful and actionable

### 📁 FILE ORGANIZATION - STRICT RULES

#### Directory Structure Requirements:
- `/line_api/`: ONLY production code, NO debug scripts
- `/tests/`: ALL pytest tests, comprehensive coverage required
- `/examples/`: ONLY real-world usage examples, fully functional
- `/docs/`: ALL documentation, including moved WEBHOOK_SETUP.md
- `/debug/`: Temporary debug scripts ONLY (gitignored)
- `/scripts/`: Utility scripts for development and CI/CD

#### File Naming Conventions:
- Snake_case for all Python files
- Clear, descriptive names indicating purpose
- Test files MUST match pattern `test_*.py`
- Example files MUST match pattern `*_example.py`

#### Import Organization (MANDATORY):
```python
# 1. Standard library imports
import asyncio
from typing import Any, Optional

# 2. Third-party imports
import httpx
from pydantic import BaseModel

# 3. Local imports
from line_api.core import LineAPIConfig
from line_api.messaging import LineMessagingClient
```

### 🧪 TESTING REQUIREMENTS - NO EXCEPTIONS

1. **ALL new features MUST have tests**:
   - Unit tests for all functions
   - Integration tests for API interactions
   - Async test patterns using pytest-asyncio
   - Mock external dependencies appropriately

2. **Test Coverage Standards**:
   - Minimum 90% code coverage
   - 100% coverage for public APIs
   - Edge cases and error conditions MUST be tested

3. **Test Quality Requirements**:
   - Clear test names describing what is being tested
   - Arrange-Act-Assert pattern
   - No test interdependencies
   - Fast execution (no real API calls in unit tests)

### 📝 DOCUMENTATION STANDARDS - MANDATORY

1. **Docstring Requirements**:
   - ALL public functions MUST have comprehensive docstrings
   - Include parameter descriptions with types
   - Include return value descriptions
   - Include usage examples for complex functions
   - Include exception documentation

2. **Example Format**:
```python
async def multicast_message(
    self,
    user_ids: list[str],
    messages: list[Any],
    notification_disabled: Optional[bool] = None,
) -> bool:
    """
    Send multicast message to multiple users.

    Efficiently sends the same message to multiple user IDs. Cannot send
    messages to group chats or multi-person chats.

    Args:
        user_ids: List of user IDs (max 500)
        messages: List of message objects (max 5)
        notification_disabled: Whether to disable push notifications

    Returns:
        True if successful

    Raises:
        LineMessageError: If message sending fails
        LineRateLimitError: If rate limit exceeded

    Example:
        >>> async with LineMessagingClient(config) as client:
        ...     success = await client.multicast_message(
        ...         user_ids=["user1", "user2"],
        ...         messages=[TextMessage.create("Hello!")],
        ...     )
    """
```

### 🔧 CODE QUALITY - STRICT ENFORCEMENT

1. **Linting and Formatting**:
   - MUST run `ruff format .` before committing
   - MUST run `ruff check .` and fix all issues
   - MUST run `mypy line_api/` and resolve all type errors
   - NO disabled linting rules without justification

2. **Code Style Requirements**:
   - Maximum line length: 88 characters
   - NO wildcard imports (`from module import *`)
   - NO unused imports or variables
   - Consistent naming conventions throughout

3. **Performance Requirements**:
   - Use async patterns for ALL I/O operations
   - Implement proper connection pooling
   - Cache responses when appropriate
   - Monitor memory usage for large operations

### 🛡️ SECURITY REQUIREMENTS - NON-NEGOTIABLE

1. **Credential Management**:
   - NO hardcoded secrets or tokens
   - ALL credentials MUST use environment variables
   - Pydantic SecretStr for sensitive data
   - Secure defaults for all configuration

2. **API Security**:
   - ALWAYS verify LINE webhook signatures
   - Implement proper rate limiting
   - Validate ALL input data
   - Log security events appropriately

### 🚀 LINE API SPECIFIC REQUIREMENTS

1. **Messaging API**:
   - Support ALL optional parameters per LINE API spec
   - Implement retry mechanisms with exponential backoff
   - Proper rate limiting (respect LINE's limits)
   - Comprehensive error handling for all status codes

2. **Webhook Processing**:
   - ALWAYS verify signatures for security
   - Use decorator-based event handlers
   - Handle ALL event types gracefully
   - Implement duplicate event detection
   - Use proper HTTP status codes

3. **Flex Messages**:
   - Use factory methods (.create()) for ALL components
   - NEVER use deprecated FlexSpacer
   - ALWAYS provide alt_text for FlexMessage
   - Use print_flex_json() for testing with auto-clipboard
   - Validate JSON in LINE Flex Message Simulator

### 🔄 DEVELOPMENT WORKFLOW - MANDATORY STEPS

#### Before Starting ANY Task:
1. Create feature branch: `git checkout -b feature/description`
2. Read ALL relevant existing code
3. Check current tests: `python -m pytest tests/ -v`
4. Understand the current implementation completely

#### During Development:
1. Write tests FIRST (TDD approach preferred)
2. Implement with full type hints
3. Add comprehensive docstrings
4. Run tests frequently: `python -m pytest tests/test_specific.py -v`

#### Before Committing:
1. Run ALL tests: `python -m pytest tests/ -v`
2. Run type checking: `mypy line_api/`
3. Run linting: `ruff check . && ruff format .`
4. Verify examples still work
5. Update documentation if needed

#### Git Commit Requirements:
- Clear, descriptive commit messages
- Include what was changed and why
- Reference any related issues
- Follow conventional commit format when possible

### ❌ PROHIBITED ACTIONS

1. **NEVER** use bare `except:` clauses
2. **NEVER** ignore type checker warnings without justification
3. **NEVER** hardcode credentials or secrets
4. **NEVER** commit debug print statements
5. **NEVER** break existing public APIs without deprecation
6. **NEVER** add dependencies without updating pyproject.toml
7. **NEVER** commit code that doesn't pass all tests
8. **NEVER** use synchronous I/O for external API calls

### 🏆 QUALITY GATES - ALL MUST PASS

Before any code is considered complete:

- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Type checking passes: `mypy line_api/`
- [ ] Linting passes: `ruff check .`
- [ ] Code is formatted: `ruff format .`
- [ ] Documentation is updated
- [ ] Examples work correctly
- [ ] Performance is acceptable
- [ ] Security review completed

### 🚨 VIOLATION CONSEQUENCES

Failure to follow these guidelines will result in:
1. Immediate rejection of changes
2. Required rework with full compliance
3. Additional review requirements for future changes

**These guidelines are not suggestions - they are requirements for maintaining the quality and reliability of this production-grade LINE API integration library.**

### Development Guidelines

#### Adding New Features

1. **Plan the API**: Design the public interface first
2. **Write Tests**: Start with test cases for the new feature
3. **Implement**: Create the implementation with full type hints
4. **Document**: Add comprehensive docstrings and examples
5. **Integration**: Update the main `LineAPI` class if needed
6. **Validate**: Run all tests and type checking

#### Code Organization Rules

- **Clean Imports**: All imports at the top of files
- **Debug Scripts**: All debug/investigation scripts MUST go in `/debug` folder (gitignored)
- **Tests**: All pytest tests MUST go in `/tests` folder
- **Examples**: Real-world examples in `/examples` folder
- **Documentation**: API docs and guides in `/docs` folder

#### Error Handling Patterns

```python
from line_api.core.exceptions import LineAPIError, LineRateLimitError

# Proper exception handling with retry
async def send_with_retry(client: LineMessagingClient, message: Any) -> bool:
    """Send message with exponential backoff retry."""
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries + 1):
        try:
            return await client.push_message("USER_ID", [message])
        except LineRateLimitError as e:
            if attempt == max_retries:
                raise
            
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
            continue
        except LineAPIError as e:
            # Log error with structured data
            logger.error(
                "Message send failed",
                extra={"user_id": "USER_ID", "error": str(e)}
            )
            raise
```


### Production Considerations

- **Rate Limiting**: Implement proper rate limiting for all API calls
- **Error Recovery**: Retry mechanisms with exponential backoff
- **Logging**: Structured logging for debugging and monitoring
- **Security**: Secure credential management and validation
- **Performance**: Async operations and connection pooling
- **Monitoring**: Health checks and metrics collection
````
### Commit Message Instructions

1. **Use clear section headers** (e.g., 🎯 New Features, 🛠️ Technical Implementation, 📁 Files Added/Modified, ✅ Benefits, 🧪 Tested)
2. **Summarize the purpose and impact** of the change in the first line
3. **List all new and modified files** with brief descriptions
4. **Highlight user and technical benefits** clearly
5. **Note any testing or validation** performed
6. **Use bullet points** (•) for better readability
7. **Include relevant emojis** for visual organization
8. **Keep descriptions concise** but informative

### Key Files for AI Understanding

- **README.md**: User-facing documentation and usage examples
- **pyproject.toml**: Dependencies and project configuration
- **Module `__init__.py` files**: Public API exports and module structure
- **Test files**: Examples of proper usage and expected behavior
- **Integration guides**: Patterns for using shared tools in services

This LINE API Integration Library provides comprehensive, type-safe Python integration with all LINE platform APIs, enabling developers to build robust LINE-based applications with modern async/await patterns and full Pydantic validation.
`````
