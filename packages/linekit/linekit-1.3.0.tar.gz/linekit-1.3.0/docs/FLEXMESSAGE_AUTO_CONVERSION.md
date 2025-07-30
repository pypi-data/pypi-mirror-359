# FlexMessage Auto-Conversion Feature

## Overview

In LINE API v1.0.2+, we've implemented a significant developer experience improvement: **automatic Pydantic model conversion** in `FlexMessage.create()`. This eliminates the need for users to manually call `.model_dump()` when creating Flex messages.

## The Problem (Before)

Previously, users had to manually convert Pydantic models to dictionaries:

```python
# ❌ Before: Manual serialization required
bubble = FlexBubble.create(body=body)
flex_message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble.model_dump(exclude_none=True, mode="json")  # Manual!
)
```

**Issues with this approach:**
- **Boilerplate code**: Users had to remember the correct `.model_dump()` parameters
- **Inconsistent API**: Different serialization needs for different use cases
- **Error-prone**: Easy to forget the right parameters and get API errors
- **Poor UX**: Exposed internal serialization complexity to users

## The Solution (After)

Now, `FlexMessage.create()` automatically detects and converts Pydantic models:

```python
# ✅ After: Auto-conversion - much cleaner!
bubble = FlexBubble.create(body=body)
flex_message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble  # Auto-converted! 🎉
)
```

## Implementation Details

### Enhanced FlexMessage.create() Method

```python
@classmethod
def create(cls, alt_text: str, contents: dict[str, Any] | BaseModel) -> FlexMessage:
    """
    Create a Flex message.

    Automatically converts Pydantic models to dictionaries for LINE API compatibility.
    This eliminates the need for users to manually call .model_dump().
    """
    # Auto-convert Pydantic models to dictionaries
    if isinstance(contents, BaseModel):
        contents_dict = contents.model_dump(exclude_none=True, mode="json")
    else:
        contents_dict = contents

    return cls(altText=alt_text, contents=contents_dict)
```

### Key Features

1. **Type Safety**: Accepts both `dict[str, Any]` and `BaseModel` (Pydantic models)
2. **Auto-Detection**: Uses `isinstance(contents, BaseModel)` to detect Pydantic models
3. **Proper Serialization**: Uses `exclude_none=True, mode="json"` for LINE API compatibility
4. **Backward Compatible**: Still accepts dictionaries for advanced use cases

## Benefits

### 🎯 For Developers
- **Cleaner Code**: No more boilerplate `.model_dump()` calls
- **Better UX**: More intuitive and consistent API
- **Fewer Errors**: Eliminates serialization parameter mistakes
- **Type Safety**: Full type hints with union types

### 🚀 For the Library
- **Better API Design**: Follows principle of least surprise
- **Reduced Support**: Fewer questions about serialization
- **Future-Proof**: Easy to extend for other message types
- **Consistent**: Aligns with modern Python library patterns

## Examples

### Basic Usage

```python
from line_api import FlexBox, FlexBubble, FlexText, FlexLayout
from line_api.messaging import FlexMessage

# Create flex components
text = FlexText.create("Hello World!")
box = FlexBox.create(layout=FlexLayout.VERTICAL, contents=[text])
bubble = FlexBubble.create(body=box)

# Auto-conversion - no .model_dump() needed!
message = FlexMessage.create("Hello", bubble)
```

### With Multicast

```python
# Works seamlessly with all messaging methods
async with LineMessagingClient(config) as client:
    await client.multicast_message(
        user_ids=["user1", "user2"],
        messages=[message],  # Auto-converted message
    )
```

### Complex Nested Structures

```python
# Even complex nested structures work automatically
carousel = FlexCarousel.create(bubbles=[bubble1, bubble2, bubble3])
message = FlexMessage.create("Carousel", carousel)  # All auto-converted!
```

## Migration

### Existing Code
No breaking changes! Existing code with `.model_dump()` continues to work:

```python
# Still works fine
flex_message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble.model_dump(exclude_none=True, mode="json")
)
```

### Recommended Updates
For new code, use the cleaner syntax:

```python
# Recommended for new code
flex_message = FlexMessage.create(
    alt_text="Hello",
    contents=bubble  # Much cleaner!
)
```

## Technical Notes

### Performance
- **Minimal Overhead**: Only checks `isinstance()` once per call
- **Same Output**: Produces identical results to manual `.model_dump()`
- **Memory Efficient**: No extra copies, direct conversion

### Type Checking
- **Full mypy Support**: Passes strict type checking
- **Union Types**: Uses modern `dict[str, Any] | BaseModel` syntax
- **Pydantic Compatible**: Works with all Pydantic v2 models

## Future Enhancements

This pattern could be extended to:
- Other message types with complex content
- Multicast/push message methods for automatic message conversion
- Template message creation
- Rich menu content generation

## Conclusion

The FlexMessage auto-conversion feature significantly improves the developer experience by eliminating boilerplate code and reducing the complexity of working with Flex messages. It maintains full backward compatibility while providing a much cleaner and more intuitive API.

This change aligns with modern Python library design principles and makes the LINE API integration library more user-friendly and professional.
