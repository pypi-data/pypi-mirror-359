# 🎨 LINE Flex Messages Documentation

This directory contains comprehensive documentation for LINE Flex Messages implementation in the LINE API Python library.

## 📚 Documentation Structure

### Core Documentation
- **[Elements Guide](elements.md)** - Complete guide to all Flex Message components
- **[Layout Guide](layout.md)** - Advanced layout techniques and positioning
- **[Video Guide](video.md)** - Video component integration and requirements

### Quick References
- **[Components Reference](components-reference.md)** - Quick reference for all components
- **[Properties Reference](properties-reference.md)** - All properties with validation rules
- **[Size & Spacing Guide](size-spacing.md)** - Size keywords and spacing options

### Advanced Topics
- **[Type Safety Guide](type-safety.md)** - Pydantic models and validation
- **[Best Practices](best-practices.md)** - Development patterns and recommendations
- **[Migration Guide](migration.md)** - Upgrading from older versions

## 🚀 Quick Start

```python
from line_api.flex_messages import (
    FlexMessage, FlexBubble, FlexBox, FlexText, FlexButton,
    FlexLayout, FlexSize, FlexTextWeight, FlexButtonStyle
)

# Create a simple flex message
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
    alt_text="Welcome message",
    contents=bubble
)
```

## 🎯 Key Features

### Type-Safe Components
- **Full Pydantic Integration**: All components use Pydantic models for validation
- **Enum Support**: Type-safe enums for sizes, colors, and layouts
- **IDE Support**: Complete auto-completion and type checking

### Comprehensive API Coverage
- **All Components**: Text, Image, Button, Video, Icon, Span, Box, Separator
- **Advanced Layout**: Flexbox properties, positioning, gradients
- **Modern Features**: Video support, styled text, accessibility options

### Developer Experience
- **Factory Methods**: Clean `.create()` methods for all components
- **JSON Export**: Direct LINE API-compatible JSON output
- **Debug Tools**: Built-in validation and testing utilities

## 📖 LINE Official Documentation

This implementation is based on the official LINE documentation:

- **[Flex Message Elements](https://developers.line.biz/en/docs/messaging-api/flex-message-elements/)**
- **[Flex Message Layout](https://developers.line.biz/en/docs/messaging-api/flex-message-layout/)**
- **[Video Messages](https://developers.line.biz/en/docs/messaging-api/create-flex-message-including-video/)**

## 🔍 Navigation

Choose a topic to explore:

| Topic | Description |
|-------|-------------|
| [Elements](elements.md) | Complete component guide with examples |
| [Layout](layout.md) | Advanced layout and positioning techniques |
| [Video](video.md) | Video component requirements and usage |
| [Components Reference](components-reference.md) | Quick component reference |
| [Properties Reference](properties-reference.md) | All properties and validation |
| [Type Safety](type-safety.md) | Pydantic models and validation |
| [Best Practices](best-practices.md) | Development recommendations |

## 🏷️ Tags
`flex-messages` `line-api` `pydantic` `type-safety` `documentation`
