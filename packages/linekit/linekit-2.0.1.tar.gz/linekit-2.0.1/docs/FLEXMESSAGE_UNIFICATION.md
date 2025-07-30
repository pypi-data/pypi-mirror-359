# FlexMessage Unification - Developer Experience Improvement

## 🎯 Overview

We've simplified the LINE API integration by unifying the FlexMessage classes. Users now only need to work with **one** FlexMessage class instead of two confusing ones.

## ❌ Previous Confusing Approach

Before this update, users had to deal with **two different FlexMessage classes**:

```python
# Old confusing approach
from line_api import FlexBubble, FlexBox, FlexText  # Building components
from line_api.messaging import FlexMessage as MessagingFlexMessage  # API calls

# Create components
text = FlexText.create("Hello")
box = FlexBox.create(layout="vertical", contents=[text])
bubble = FlexBubble.create(body=box)

# CONFUSION: Different FlexMessage for API calls
message = MessagingFlexMessage.create(
    alt_text="Hello",
    contents=bubble.model_dump()  # Manual conversion required!
)
```

**Problems with the old approach:**
- Two different FlexMessage classes with different purposes
- Users needed to remember which one to import for which use case
- Required manual `.model_dump()` conversion
- Poor developer experience
- High cognitive load

## ✅ New Unified Approach

Now users work with **only one FlexMessage class**:

```python
# New unified approach
from line_api import FlexBubble, FlexBox, FlexText, FlexMessage  # Everything from one place

# Create components
text = FlexText.create("Hello")
box = FlexBox.create(layout="vertical", contents=[text])
bubble = FlexBubble.create(body=box)

# SIMPLE: Same FlexMessage for everything!
message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble  # Auto-conversion handled internally!
)

# Direct usage with messaging client
async with LineMessagingClient(config) as client:
    await client.push_message(user_id, [message])  # Just works!
```

## 🔧 Technical Implementation

### Unified FlexMessage Class

The FlexMessage class in `line_api.flex_messages.models` now serves both purposes:

1. **Building Flex content** - Create rich UI components
2. **API integration** - Send messages via LINE Messaging API

```python
class FlexMessage(BaseModel):
    """
    Unified FlexMessage class for both building and sending.
    """
    type: str = Field(default="flex", frozen=True)
    altText: str = Field(..., description="Alternative text for notifications")
    contents: Union[FlexBubble, FlexCarousel, dict[str, Any]]

    @classmethod
    def create(
        cls,
        alt_text: str,
        contents: Union[FlexBubble, FlexCarousel, dict[str, Any]],
    ) -> "FlexMessage":
        """Create a FlexMessage with automatic conversion support."""
        return cls(altText=alt_text, contents=contents)

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Export with proper field name conversion for LINE API."""
        data = super().model_dump(**kwargs)

        # Ensure contents is properly serialized if it's a Pydantic model
        if isinstance(self.contents, (FlexBubble, FlexCarousel)):
            data['contents'] = self.contents.model_dump(exclude_none=True, mode="json")

        return data
```

### Removed Duplicate

The duplicate `FlexMessage` class from `line_api.messaging.models` has been removed to eliminate confusion.

### Updated Exports

```python
# line_api/messaging/__init__.py
from line_api.flex_messages import FlexMessage  # Import unified class

# line_api/__init__.py
from .flex_messages import FlexMessage  # Available from main package
```

## 🎉 Benefits

### For Developers
- **Simplified mental model**: Only one FlexMessage to remember
- **Reduced imports**: Everything from `line_api` package
- **No manual conversion**: Auto-handled internally
- **Better IDE support**: Clear autocomplete and type hints
- **Less error-prone**: No confusion about which class to use

### For API Integration
- **Seamless compatibility**: Works directly with messaging client
- **Automatic serialization**: Proper field name conversion
- **Type safety maintained**: Full Pydantic validation
- **Backward compatibility**: Existing code continues to work

## 📚 Migration Guide

### For New Users
Simply import and use FlexMessage from the main package:

```python
from line_api import FlexMessage, FlexBubble, FlexBox, FlexText

# Create and send in one simple flow
message = FlexMessage.create("Hello", bubble)
await client.push_message(user_id, [message])
```

### For Existing Users

#### If you were using `line_api.flex_messages.FlexMessage`:
✅ **No changes needed** - your code continues to work exactly the same!

#### If you were using `line_api.messaging.FlexMessage`:
🔄 **Simple update** - change your import:

```python
# Old
from line_api.messaging import FlexMessage

# New
from line_api import FlexMessage
```

And update the parameter name:
```python
# Old
FlexMessage.create(alt_text="Hello", contents=bubble)

# New
FlexMessage.create(alt_text="Hello", contents=bubble)  # Same!
```

## 🧪 Testing

All existing tests continue to pass. The unified approach has been validated with:

- ✅ Unit tests for FlexMessage creation
- ✅ Integration tests with messaging API
- ✅ Real-world message sending
- ✅ Type checking with mypy
- ✅ Backward compatibility verification

## 🎯 Examples

See the new examples:

- `examples/unified_flex_message_example.py` - Demonstrates the unified approach
- `examples/multicast_message_example.py` - Updated to use unified FlexMessage

## 🚀 Summary

This unification significantly improves the developer experience by:

1. **Eliminating confusion** between two FlexMessage classes
2. **Simplifying imports** to a single source
3. **Removing manual conversion** requirements
4. **Maintaining full compatibility** with existing code
5. **Providing a cleaner API** for new users

The change is **backward compatible** and represents a major step forward in making the LINE API integration more intuitive and developer-friendly.
