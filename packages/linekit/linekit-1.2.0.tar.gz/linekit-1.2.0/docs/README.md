# 📚 LINE API Integration Library - Documentation

Complete documentation for the LINE API Python integration library.

## 🗂️ Documentation Structure

### Core Documentation

- **[FlexMessage Documentation](flex-messages/README.md)** - Comprehensive FlexMessage implementation guide
- **[Webhook Setup Guide](WEBHOOK_SETUP.md)** - Complete webhook configuration and handling
- **[FlexMessage Enhancement Summary](FLEXMESSAGE_DOCUMENTATION_COMPLETE.md)** - Implementation completion summary

### FlexMessage Guides

Navigate to `flex-messages/` for complete FlexMessage documentation:

| Guide | Description |
|-------|-------------|
| **[Elements](flex-messages/elements.md)** | All FlexMessage components with examples |
| **[Layout](flex-messages/layout.md)** | Advanced layout and positioning techniques |
| **[Video](flex-messages/video.md)** | Video component integration and requirements |
| **[Components Reference](flex-messages/components-reference.md)** | Quick component API reference |
| **[Properties Reference](flex-messages/properties-reference.md)** | All properties and validation rules |
| **[Type Safety](flex-messages/type-safety.md)** | Pydantic models and validation |
| **[Best Practices](flex-messages/best-practices.md)** | Development patterns and recommendations |

## 🚀 Quick Start

### FlexMessage Example

```python
from line_api.flex_messages import (
    FlexMessage, FlexBubble, FlexBox, FlexText,
    FlexLayout, FlexSize, FlexTextWeight
)

# Create a simple message
title = FlexText.create(
    "Welcome!",
    size=FlexSize.XL,
    weight=FlexTextWeight.BOLD
)

body = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[title]
)

bubble = FlexBubble.create(body=body)
message = FlexMessage.create(
    alt_text="Welcome",
    contents=bubble
)
```

### Webhook Setup

```python
from line_api.webhook import LineWebhookHandler
from line_api.core import LineAPIConfig

config = LineAPIConfig()
handler = LineWebhookHandler(config)

@handler.message_handler
async def handle_message(event):
    # Process incoming messages
    pass
```

## 🎯 Key Features

### Type Safety

- **Full Pydantic Integration**: All components use Pydantic models
- **Type-Safe Enums**: For sizes, colors, layouts, and styles
- **IDE Support**: Complete auto-completion and type checking

### Comprehensive API Coverage

- **FlexMessage Components**: Text, Image, Button, Video, Icon, Span, Box
- **Advanced Layout**: Flexbox properties, positioning, gradients
- **Webhook Handling**: Complete event processing with validation
- **Modern Features**: Video support, styled text, accessibility

### Developer Experience

- **Factory Methods**: Clean `.create()` methods for all components
- **JSON Export**: Direct LINE API-compatible JSON output
- **Debug Tools**: Built-in validation and testing utilities
- **Rich Documentation**: Examples and best practices

## 📖 Official LINE Documentation

This implementation is based on official LINE documentation:

- **[Flex Message Elements](https://developers.line.biz/en/docs/messaging-api/flex-message-elements/)**
- **[Flex Message Layout](https://developers.line.biz/en/docs/messaging-api/flex-message-layout/)**
- **[Video Messages](https://developers.line.biz/en/docs/messaging-api/create-flex-message-including-video/)**
- **[Webhook Events](https://developers.line.biz/en/docs/messaging-api/receiving-messages/)**

## 🔍 Navigation Guide

**New to FlexMessage?** Start with:

1. [FlexMessage Overview](flex-messages/README.md)
2. [Elements Guide](flex-messages/elements.md)
3. [Basic Examples](../examples/flex_message_example.py)

**Building Advanced Messages?** Check:

1. [Layout Guide](flex-messages/layout.md)
2. [Video Integration](flex-messages/video.md)
3. [Advanced Examples](../examples/enhanced_flex_message_example.py)

**Need Reference?** Use:

1. [Components Reference](flex-messages/components-reference.md)
2. [Properties Reference](flex-messages/properties-reference.md)
3. [Type Safety Guide](flex-messages/type-safety.md)

**Development Help?** See:

1. [Best Practices](flex-messages/best-practices.md)
2. [Migration Guide](flex-messages/migration.md)
3. [Webhook Setup](WEBHOOK_SETUP.md)

## 📁 Examples

Find working examples in `/examples/`:

- **`flex_message_example.py`** - Basic FlexMessage usage
- **`enhanced_flex_message_example.py`** - Advanced features showcase
- **`webhook_example.py`** - Webhook handler implementation
- **`push_message_example.py`** - Message sending patterns

## 🏷️ Tags

`line-api` `flex-messages` `webhook` `pydantic` `type-safety` `documentation` `python`
