# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-07-02

### Fixed

- **🚨 CRITICAL: FlexMessage Serialization Bug Fix**
  - **Fixed LINE API 400 Errors**: Resolved issue where snake_case field names were being sent to LINE API instead of required camelCase
  - **Root Cause**: `FlexMessage.model_dump()` method was not consistently using `by_alias=True` parameter
  - **Impact**: Eliminated 400 "unknown field" errors for properties like `aspect_ratio`, `background_color`, `line_spacing`, etc.
  - **Solution**: Updated `FlexMessage.model_dump()` to always use `by_alias=True` for both main model and nested models
  - **Verification**: All 27 snake_case properties now properly serialize to camelCase format

- **🔧 Technical Improvements**
  - **Enhanced Serialization**: Added safe kwargs handling to prevent duplicate parameter errors
  - **Nested Model Support**: Ensured FlexBubble and FlexCarousel also use proper field name conversion
  - **Comprehensive Testing**: Verified all field mappings with automated serialization tests
  - **API Compliance**: 100% compliance with LINE API field naming requirements

### Verified Field Mappings

The following snake_case properties are now guaranteed to serialize correctly:

- `display_text` → `displayText`
- `alt_uri_desktop` → `altUriDesktop`
- `line_spacing` → `lineSpacing`
- `max_lines` → `maxLines`
- `adjust_mode` → `adjustMode`
- `offset_top/bottom/start/end` → `offsetTop/Bottom/Start/End`
- `aspect_ratio` → `aspectRatio`
- `aspect_mode` → `aspectMode`
- `background_color` → `backgroundColor`
- `preview_url` → `previewUrl`
- `alt_content` → `altContent`
- `start_color/end_color/center_color` → `startColor/endColor/centerColor`
- `center_position` → `centerPosition`
- `max_width/max_height` → `maxWidth/maxHeight`
- `padding_all/top/bottom/start/end` → `paddingAll/Top/Bottom/Start/End`
- `border_color/border_width` → `borderColor/borderWidth`

### Impact

- **Before**: FlexMessages failed with LINE API 400 errors like "unknown field: aspect_ratio"
- **After**: All FlexMessages serialize correctly with proper camelCase field names
- **Result**: Production LINE bots can now send complex FlexMessages without serialization errors

## [2.0.0] - 2025-07-02

### Added

- **🎯 MAJOR: FlexMessage Unification - Simplified Developer Experience**
  - **Unified FlexMessage Class**: Combined `line_api.flex_messages.FlexMessage` and `line_api.messaging.FlexMessage` into a single, powerful class
  - **Zero Confusion**: Users now work with only ONE FlexMessage class instead of two confusing ones
  - **Seamless API Integration**: Unified class works perfectly for both building Flex content AND sending via messaging API
  - **Automatic Serialization**: Built-in `model_dump()` method properly handles field name conversion for LINE API compatibility
  - **Enhanced Type Safety**: Supports both Pydantic models and dictionaries with proper type hints
  - **Better Developer Experience**: Eliminates the need to understand which FlexMessage to use when

- **🔧 Technical Improvements**
  - **Field Name Standardization**: Changed `alt_text` to `altText` in FlexMessage for LINE API consistency
  - **Enhanced model_dump()**: Automatically converts nested Pydantic models to proper JSON format
  - **Removed Duplicate Code**: Eliminated redundant FlexMessage implementation from messaging module
  - **Updated Imports**: Messaging module now re-exports the unified FlexMessage from flex_messages
  - **Maintained Type Safety**: Full mypy strict mode compliance across all modules

- **📚 Documentation and Examples**
  - **New Documentation**: Added comprehensive `docs/FLEXMESSAGE_UNIFICATION.md` explaining the changes and benefits
  - **Updated Examples**: All examples now use the unified FlexMessage approach
  - **New Unified Example**: Created `examples/unified_flex_message_example.py` demonstrating the simplified API
  - **Migration Guide**: Clear guidance for existing users (most changes are backward compatible)

### Changed

- **BREAKING**: Removed duplicate `FlexMessage` class from `line_api.messaging.models`
- **BREAKING**: Changed `FlexMessage.alt_text` field to `FlexMessage.altText` for API consistency
- **Enhanced**: All messaging operations now use the unified FlexMessage class
- **Updated**: Import paths simplified - all FlexMessage usage from single source

### Migration Guide

#### For New Users
- Import everything from main package: `from line_api import FlexMessage, FlexBubble, ...`
- Create messages directly: `FlexMessage.create(alt_text="Hello", contents=bubble)`
- Send via messaging API: `await client.push_message(user_id, [message])`

#### For Existing Users
- **If using `line_api.flex_messages.FlexMessage`**: ✅ No changes needed (backward compatible)
- **If using `line_api.messaging.FlexMessage`**: 🔄 Change import to `from line_api import FlexMessage`
- **Field name update**: Change `alt_text` to `altText` in FlexMessage.create() calls

### Benefits

- **🧠 Reduced Cognitive Load**: Only one FlexMessage class to remember
- **📝 Cleaner Code**: No confusion about which FlexMessage to import/use
- **🔄 No Manual Conversion**: Auto-handled serialization for API calls
- **🎯 Better IDE Support**: Clear autocomplete without duplicate classes
- **⚡ Faster Development**: Streamlined workflow for Flex message creation

## [1.3.0] - 2025-07-02

### Added

- **🎉 FlexMessage Auto-Conversion Feature**
  - **Automatic Pydantic Model Conversion**: `FlexMessage.create()` now automatically converts Pydantic models to dictionaries
  - **Enhanced Developer Experience**: No more manual `.model_dump()` calls required when creating Flex messages
  - **Backward Compatible**: Still supports dictionary inputs for advanced use cases
  - **Type Safety**: Enhanced type signature `contents: dict[str, Any] | BaseModel` with full mypy support
  - **Smart Detection**: Uses `isinstance(contents, BaseModel)` to detect and convert Pydantic models automatically
  - **Proper Serialization**: Automatically applies `exclude_none=True, mode="json"` for LINE API compatibility

- **📚 Enhanced Examples and Documentation**
  - **New Auto-Conversion Example**: `flex_message_auto_conversion_example.py` demonstrating the new feature
  - **Comprehensive Documentation**: Added `FLEXMESSAGE_AUTO_CONVERSION.md` with detailed usage guide
  - **Before/After Comparisons**: Clear examples showing the improvement in code clarity
  - **Migration Guide**: Instructions for updating existing code (optional - no breaking changes)

### Enhanced

- **FlexMessage.create() Method**: Now accepts both `dict[str, Any]` and `BaseModel` for contents parameter
- **Multicast Message Examples**: Updated to showcase cleaner auto-conversion syntax
- **Type Annotations**: Modern `|` union syntax instead of deprecated `Union[]`
- **API Consistency**: All Flex message creation now uses the same intuitive pattern

### Technical Improvements

- **Zero Breaking Changes**: All existing code continues to work without modification
- **Performance Optimized**: Minimal overhead with single `isinstance()` check
- **Full Test Coverage**: All functionality tested and validated
- **Production Ready**: Successfully tested with real LINE API endpoints

### Code Examples

#### Before (v1.2.1 and earlier)
```python
# Manual serialization required
bubble = FlexBubble.create(body=body)
flex_message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble.model_dump(exclude_none=True, mode="json")  # Manual!
)
```

#### After (v1.3.0+)
```python
# Auto-conversion - much cleaner!
bubble = FlexBubble.create(body=body)
flex_message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble  # Auto-converted! 🎉
)
```

### Benefits

- **✨ Cleaner Code**: Eliminates boilerplate `.model_dump()` calls
- **🚫 Fewer Errors**: No more serialization parameter mistakes
- **🛡️ Type Safety**: Full type hints with union types
- **📱 Better UX**: More intuitive and consistent API
- **🔧 Less Boilerplate**: Reduced code complexity for developers

## [1.2.1] - 2025-07-02

### Fixed

- **🔧 URI Actions Documentation Fix**
  - **Fixed import statements**: Corrected all documentation to use `from line_api.flex_messages import FlexUriAction`
  - **Removed incorrect imports**: Eliminated non-existent `from line_api.actions import URIAction` references
  - **Added convenience aliases**: Added `URIAction`, `PostbackAction`, `MessageAction` aliases for better ergonomics
  - **Enhanced factory methods**: Added `.create()` class methods for all action types for consistency
  - **Updated examples**: Fixed all documentation examples to use correct import patterns

- **📚 Documentation Consistency**
  - **properties-reference.md**: Fixed URI action import and usage examples
  - **size-spacing.md**: Corrected button action examples
  - **video.md**: Fixed all video action examples (5 instances)
  - **components-reference.md**: Updated component examples with correct imports
  - **best-practices.md**: Fixed all action usage examples (4 instances) and added missing imports

- **🧪 Enhanced Testing**
  - **Comprehensive test suite**: Added `test_uri_actions.py` with 11 test cases
  - **Import verification**: Tests for both `FlexUriAction` and `URIAction` alias imports
  - **Factory method testing**: Validates both direct constructor and `.create()` method usage
  - **Serialization testing**: Ensures proper JSON output for LINE API compliance

### Technical Improvements

- **Better Developer Experience**: Users can now use either `FlexUriAction` or `URIAction` alias
- **Consistent API**: All action types now have `.create()` factory methods
- **Type Safety**: Maintained full type safety across all changes
- **Backward Compatibility**: No breaking changes, only additions and fixes

## [1.2.0] - 2025-07-01

### Added

- **🎉 Comprehensive FlexMessage Model Updates**
  - **NEW FlexSpan Component**: Styled text within text components with decoration, weight, and color options
  - **NEW FlexVideo Component**: Video content in hero blocks with preview images and alt content support
  - **Enhanced Enums**: Complete FlexTextDecoration, FlexAdjustMode, and FlexPosition enums
  - **Advanced Layout Properties**: Enhanced spacing, alignment, and positioning options
  - **Linear Gradient Backgrounds**: Full support for gradient backgrounds in FlexBox components

- **🛡️ Type Safety & API Compliance**
  - **Full mypy strict mode compliance** (0 errors across 15 source files)
  - **Required action labels**: All FlexAction types now properly require `label` parameter for LINE API compliance
  - **Removed deprecated properties**: Eliminated unsupported `corner_radius` from FlexBox
  - **Modern type annotations**: Updated to use `dict`/`list` instead of deprecated `Dict`/`List`
  - **Enhanced Union type handling**: Proper type casts for FlexBox contents

- **📚 Enhanced Documentation & Examples**
  - **Comprehensive documentation suite** in `/docs/flex-messages/` directory
  - **LINE Flex Message Simulator integration** with automatic clipboard copy functionality
  - **Updated examples** demonstrating FlexSpan, FlexVideo, and gradient backgrounds
  - **Migration guides** for breaking changes and new features
  - **Usage guides** for all new components with practical examples

- **🔧 Developer Experience Improvements**
  - **Enhanced factory methods**: Improved `.create()` methods for all components
  - **Better IDE support**: Enhanced auto-completion and type hints
  - **Automatic JSON export**: Direct export to LINE Flex Message Simulator format
  - **Clipboard integration**: Auto-copy generated JSON for easy testing

### Enhanced

- **FlexMessage Models**: Complete overhaul with latest LINE API specification compliance
- **FlexBox Component**: Enhanced with justify-content, align-items, and gradient background support
- **FlexText Component**: Added support for FlexSpan contents and advanced text properties
- **FlexButton Component**: Enhanced with better positioning and styling options
- **FlexImage Component**: Improved aspect ratio and positioning controls
- **All Components**: Added comprehensive offset positioning (top, bottom, start, end)

### Fixed

- **BREAKING**: Removed unsupported `corner_radius` property from FlexBox (use border properties instead)
- **BREAKING**: Made `label` required for all FlexAction types (FlexPostbackAction, FlexMessageAction, FlexUriAction)
- **Type annotations**: Fixed all mypy strict mode type errors
- **Import organization**: Cleaned up imports and fixed deprecated type usage
- **Linting compliance**: Full ruff linting compliance with proper formatting
- **Test coverage**: Enhanced test suite with comprehensive component validation

### Migration Guide

#### Required Changes for v1.2.0

1. **Action Labels Now Required**:

   ```python
   # ❌ Old (will fail)
   FlexUriAction(uri="https://example.com")

   # ✅ New (required)
   FlexUriAction(label="Visit Site", uri="https://example.com")
   ```

2. **Removed corner_radius Property**:

   ```python
   # ❌ Old (not supported)
   FlexBox(layout="vertical", contents=[], corner_radius="10px")

   # ✅ New (use border properties)
   FlexBox(layout="vertical", contents=[], border_width="1px")
   ```

#### New Features Available

1. **FlexSpan for Rich Text**:

   ```python
   FlexText.create(
       text="Rich text with spans",
       contents=[
           FlexSpan.create("Bold", weight=FlexTextWeight.BOLD),
           FlexSpan.create(" and colored text", color="#FF0000")
       ]
   )
   ```

2. **FlexVideo in Hero Blocks**:

   ```python
   FlexVideo.create(
       url="https://example.com/video.mp4",
       preview_url="https://example.com/thumb.jpg",
       alt_content=FlexImage.create("https://example.com/fallback.jpg"),
       aspect_ratio="16:9"
   )
   ```

3. **Linear Gradient Backgrounds**:

   ```python
   FlexBox.create(
       layout=FlexLayout.VERTICAL,
       contents=[...],
       background=FlexLinearGradient.create(
           angle="135deg",
           start_color="#00C300",
           end_color="#00A000"
       )
   )
   ```

### Quality Assurance

- ✅ All 34 tests pass
- ✅ Full mypy strict mode compliance (0 type errors)
- ✅ Complete ruff linting compliance
- ✅ LINE Flex Message Simulator compatibility verified
- ✅ Production-ready code quality

## [1.1.0] - 2025-07-01

### Added

- **Enhanced Multicast Messaging**
  - Full LINE API support with all optional parameters
  - `notification_disabled` parameter for silent message sending
  - `custom_aggregation_units` for analytics tracking and campaign management
  - `retry_key` parameter for idempotent message sending
  - Comprehensive error handling and validation
  - Interactive examples with user input for testing

- **Strict Development Guidelines**
  - Comprehensive AI agent instructions with non-negotiable requirements
  - Mandatory type safety, async patterns, and testing standards
  - Quality gates that must pass before code completion
  - Security requirements for credential management
  - Performance standards for async operations

- **Improved Project Structure**
  - Moved documentation to proper `docs/` directory organization
  - Enhanced project structure with clear separation of concerns
  - Better examples with real-world usage scenarios
  - Comprehensive testing patterns and coverage requirements

### Enhanced

- **LineMessagingClient**: Added support for all multicast API parameters
- **Request Models**: Enhanced with notification and analytics options
- **Examples**: Added comprehensive multicast examples with interactive input
- **Documentation**: Updated with new features and usage patterns

### Fixed

- **Project Organization**: Proper documentation structure in `docs/` directory
- **Type Safety**: Enhanced type coverage for all new features
- **Error Handling**: Better error messages and user guidance

## [1.0.0] - 2025-06-30

### Added

- **Complete LINE Messaging API Integration**
  - Push messages, reply messages, multicast, and broadcast functionality
  - Support for text, image, location, sticker, and Flex messages
  - Async-first design with proper error handling and retry logic
  - Rate limiting and connection management

- **Type-Safe Flex Messages**
  - Complete Pydantic models for all Flex Message components
  - FlexBox, FlexBubble, FlexText, FlexImage, FlexButton support
  - FlexCarousel and FlexSeparator components
  - JSON export and clipboard integration for LINE simulator testing
  - Factory methods for easy component creation

- **Comprehensive Webhook Handling**
  - Secure signature verification for webhook authenticity
  - Type-safe event models for all LINE webhook events
  - Decorator-based event handlers for clean code organization
  - Support for message, postback, follow, and unfollow events
  - FastAPI integration examples

- **Production-Ready Features**
  - Full Pydantic integration with comprehensive type hints
  - Automatic environment variable discovery and validation
  - Comprehensive error handling with typed exceptions
  - Built-in retry mechanisms with exponential backoff
  - Structured logging throughout the library

- **Developer Experience**
  - Rich IDE support with full type hints
  - Auto-completion for all API methods
  - Comprehensive test suite with pytest
  - Example code and documentation
  - UV package manager integration

- **Configuration Management**
  - Automatic .env file discovery
  - Environment variable validation
  - Type-safe configuration across all services
  - Secure credential management

### Technical Implementation

- Modern Python 3.9+ with enhanced type hints
- Async/await patterns throughout
- HTTPX for high-performance HTTP operations
- Pydantic 2.x for data validation and settings
- Comprehensive test coverage
- Code quality tools (ruff, mypy)

## [Unreleased]

### To Be Added

- N/A

### To Be Changed

- N/A

### To Be Fixed

- N/A

### To Be Removed

- N/A

### Security Updates

- N/A
