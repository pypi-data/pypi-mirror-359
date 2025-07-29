# FlexMessage Type Safety Guide

Complete guide to type-safe FlexMessage development with Pydantic models and TypeScript-like type hints.

## Overview

The line-api library provides full type safety for FlexMessage development through Pydantic v2 models, comprehensive type hints, and runtime validation. This ensures your FlexMessages are valid before sending and provides excellent IDE support.

## Type Safety Benefits

### Compile-Time Checking

```python
from line_api.flex_messages import FlexText, FlexTextSize

# ✅ Type-safe: IDE will provide autocomplete and validation
text = FlexText.create(
    text="Hello, World!",
    size=FlexTextSize.LARGE,  # Enum ensures valid values
    weight="bold"             # String literals also supported
)

# ❌ Type error: Invalid enum value (caught by mypy/IDE)
text = FlexText.create(
    text="Hello",
    size="invalid_size"  # Error: not a valid FlexTextSize
)
```

### Runtime Validation

```python
try:
    # Pydantic validates all properties at runtime
    text = FlexText.create(
        text="",  # Invalid: empty text
        color="invalid_color"  # Invalid: not a hex color
    )
except ValidationError as e:
    print(f"Validation errors: {e}")
    # Handle validation errors appropriately
```

## Type-Safe Enums

All FlexMessage properties use type-safe enums with string values:

### Size Enums

```python
from line_api.flex_messages import FlexTextSize, FlexImageSize, FlexIconSize

# All equivalent approaches
text1 = FlexText.create("Text", size=FlexTextSize.LARGE)
text2 = FlexText.create("Text", size="lg")  # String literal
text3 = FlexText.create("Text", size="lg")  # Auto-completion available

# IDE shows available options
FlexTextSize.XX_SMALL  # "xxs"
FlexTextSize.X_SMALL   # "xs"
FlexTextSize.SMALL     # "sm"
FlexTextSize.MEDIUM    # "md"
FlexTextSize.LARGE     # "lg"
# ... etc
```

### Layout Enums

```python
from line_api.flex_messages import (
    FlexLayout, FlexAlignment, FlexGravity, FlexJustifyContent
)

box = FlexBox.create(
    layout=FlexLayout.VERTICAL,           # Type-safe layout
    justifyContent=FlexJustifyContent.CENTER,  # Type-safe distribution
    alignItems=FlexAlignItems.FLEX_START,      # Type-safe alignment
    contents=[
        FlexText.create(
            "Aligned text",
            align=FlexAlignment.CENTER,   # Type-safe text alignment
            gravity=FlexGravity.CENTER    # Type-safe vertical alignment
        )
    ]
)
```

### Style Enums

```python
from line_api.flex_messages import (
    FlexWeight, FlexDecoration, FlexButtonStyle, FlexImageAspectMode
)

# Typography
text = FlexText.create(
    "Styled text",
    weight=FlexWeight.BOLD,              # Type-safe font weight
    decoration=FlexDecoration.UNDERLINE  # Type-safe decoration
)

# Button styles
button = FlexButton.create(
    action=action,
    style=FlexButtonStyle.PRIMARY  # Type-safe button style
)

# Image modes
image = FlexImage.create(
    url="https://example.com/image.jpg",
    aspectMode=FlexImageAspectMode.COVER  # Type-safe aspect mode
)
```

## Generic Type Support

### Container Types

```python
from typing import List, Union, Optional
from line_api.flex_messages import FlexBox, FlexText, FlexImage

# Type-safe content lists
contents: List[Union[FlexText, FlexImage]] = [
    FlexText.create("Title"),
    FlexImage.create(url="https://example.com/image.jpg"),
    FlexText.create("Description")
]

box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=contents  # Type checker validates content types
)
```

### Optional Properties

```python
from typing import Optional
from line_api.flex_messages import FlexBubble

# All optional properties are properly typed
bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,
    header=Optional[FlexBox] = None,      # Properly typed optional
    hero=Optional[Union[FlexImage, FlexVideo]] = None,
    body=Optional[FlexBox] = None,
    footer=Optional[FlexBox] = None
)
```

## Validation Features

### Pydantic Field Validation

```python
from pydantic import ValidationError
from line_api.flex_messages import FlexText

try:
    # URL validation
    image = FlexImage.create(
        url="not-a-valid-url"  # Validation error
    )
except ValidationError as e:
    print("Invalid URL format")

try:
    # Color validation
    text = FlexText.create(
        text="Colored text",
        color="not-a-hex-color"  # Validation error
    )
except ValidationError as e:
    print("Invalid hex color format")

try:
    # Size validation
    text = FlexText.create(
        text="Text",
        size="invalid-size"  # Validation error
    )
except ValidationError as e:
    print("Invalid size value")
```

### Custom Validators

The library includes custom validators for FlexMessage-specific rules:

```python
# Automatic validation for:
# - Valid hex colors (#ffffff, #fff)
# - Valid URLs (HTTPS required for images/videos)
# - Valid aspect ratios (16:9, 4:3, etc.)
# - Valid size values (keywords, pixels, percentages)
# - Valid component hierarchies
# - Content length limits
```

## IDE Support

### Auto-completion

```python
from line_api.flex_messages import FlexText

text = FlexText.create(
    text="Hello",
    # IDE shows all available properties with types:
    # - size: Union[FlexTextSize, str]
    # - weight: Union[FlexWeight, str]
    # - color: Optional[str]
    # - align: Union[FlexAlignment, str]
    # ... etc
)
```

### Type Hints in Function Signatures

```python
from typing import List
from line_api.flex_messages import FlexMessage, FlexBubble

def create_product_card(
    title: str,
    description: str,
    image_url: str,
    price: float
) -> FlexMessage:
    """Create a type-safe product card FlexMessage."""

    bubble = FlexBubble.create(
        # Type checker ensures proper component hierarchy
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=[
                FlexText.create(title, weight=FlexWeight.BOLD),
                FlexText.create(description),
                FlexText.create(f"${price:.2f}", color="#ff6b6b")
            ]
        )
    )

    return FlexMessage.create(
        altText=f"Product: {title}",
        contents=bubble
    )

# Function signature ensures type safety
message: FlexMessage = create_product_card(
    title="Product Name",
    description="Product description",
    image_url="https://example.com/image.jpg",
    price=29.99
)
```

## Type-Safe Factory Methods

### Factory Pattern Benefits

All components use the `.create()` factory method for better type inference:

```python
# ✅ Preferred: Factory method with full type inference
text = FlexText.create(
    text="Hello",
    size=FlexTextSize.LARGE
)

# ✅ Also valid: Direct instantiation
text = FlexText(
    text="Hello",
    size=FlexTextSize.LARGE
)

# Both approaches provide full type safety
```

### Builder Pattern Support

```python
from line_api.flex_messages import FlexBox, FlexText, FlexLayout

# Type-safe builder pattern
def create_message_card() -> FlexBubble:
    # Each step is type-checked
    header = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexText.create("Header", weight=FlexWeight.BOLD)
        ]
    )

    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        spacing=FlexSpacing.MEDIUM,
        contents=[
            FlexText.create("Main content"),
            FlexText.create("Secondary content", color="#666666")
        ]
    )

    return FlexBubble.create(
        header=header,
        body=body
    )
```

## Error Handling

### Validation Error Types

```python
from pydantic import ValidationError
from line_api.flex_messages import FlexText

def safe_create_text(text: str, **kwargs) -> Optional[FlexText]:
    """Safely create FlexText with error handling."""
    try:
        return FlexText.create(text=text, **kwargs)
    except ValidationError as e:
        # Handle specific validation errors
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            message = error.get('msg', 'Unknown error')
            print(f"Validation error in {field}: {message}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
text = safe_create_text(
    text="Hello",
    color="invalid-color"  # Will be caught and handled
)
```

### Type-Safe Error Recovery

```python
from typing import Union
from line_api.flex_messages import FlexText, FlexTextSize

def create_text_with_fallback(
    text: str,
    size: Union[FlexTextSize, str] = FlexTextSize.MEDIUM
) -> FlexText:
    """Create text with fallback to default size on error."""
    try:
        return FlexText.create(text=text, size=size)
    except ValidationError:
        # Fallback to default
        return FlexText.create(text=text, size=FlexTextSize.MEDIUM)
```

## Advanced Type Patterns

### Union Types for Flexibility

```python
from typing import Union
from line_api.flex_messages import FlexImage, FlexVideo

# Hero component can be image or video
HeroComponent = Union[FlexImage, FlexVideo]

def create_hero_bubble(hero: HeroComponent) -> FlexBubble:
    return FlexBubble.create(
        size=FlexBubbleSize.MEGA,
        hero=hero  # Type checker accepts both image and video
    )

# Usage
image_hero = FlexImage.create(url="https://example.com/image.jpg")
video_hero = FlexVideo.create(
    url="https://example.com/video.mp4",
    previewUrl="https://example.com/preview.jpg",
    altContent=image_hero,
    aspectRatio="16:9"
)

# Both are valid
bubble1 = create_hero_bubble(image_hero)
bubble2 = create_hero_bubble(video_hero)
```

### Generic Content Builders

```python
from typing import TypeVar, Generic, List, Callable
from line_api.flex_messages import FlexBox, FlexLayout

T = TypeVar('T')

class FlexListBuilder(Generic[T]):
    """Type-safe builder for lists of FlexMessage components."""

    def __init__(self, layout: FlexLayout = FlexLayout.VERTICAL):
        self.layout = layout
        self.items: List[T] = []

    def add_item(self, item: T) -> 'FlexListBuilder[T]':
        """Add an item with type checking."""
        self.items.append(item)
        return self

    def build(self) -> FlexBox:
        """Build the final FlexBox."""
        return FlexBox.create(
            layout=self.layout,
            contents=self.items
        )

# Usage with type safety
text_list = (FlexListBuilder[FlexText]()
    .add_item(FlexText.create("Item 1"))
    .add_item(FlexText.create("Item 2"))
    .add_item(FlexText.create("Item 3"))
    .build()
)
```

## Type Checking Configuration

### mypy Configuration

Add to your `mypy.ini` or `pyproject.toml`:

```ini
[mypy]
plugins = pydantic.mypy

[pydantic-mypy]
init_forbid_extra = True
init_typed = True
warn_required_dynamic_aliases = True
warn_untyped_fields = True
```

### VS Code Settings

Add to your `.vscode/settings.json`:

```json
{
    "python.analysis.typeCheckingMode": "strict",
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true
}
```

## Testing with Type Safety

### Type-Safe Test Fixtures

```python
import pytest
from typing import List
from line_api.flex_messages import FlexText, FlexBox, FlexLayout

@pytest.fixture
def sample_texts() -> List[FlexText]:
    """Type-safe test fixture."""
    return [
        FlexText.create("Title", weight=FlexWeight.BOLD),
        FlexText.create("Content", wrap=True),
        FlexText.create("Footer", size=FlexTextSize.SMALL)
    ]

def test_vertical_box_creation(sample_texts: List[FlexText]) -> None:
    """Type-safe test function."""
    box = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=sample_texts
    )

    assert box.layout == FlexLayout.VERTICAL
    assert len(box.contents) == 3

    # Type checker knows contents are FlexText
    for text in box.contents:
        assert isinstance(text, FlexText)
        assert text.text is not None
```

### Mock Type-Safe Components

```python
from unittest.mock import Mock
from line_api.flex_messages import FlexMessage

def test_with_mock_message() -> None:
    """Test with properly typed mock."""
    mock_message = Mock(spec=FlexMessage)
    mock_message.altText = "Test message"

    # Type checker understands this is a FlexMessage
    assert mock_message.altText == "Test message"
```

## Best Practices

### Type Import Organization

```python
# Standard library types
from typing import List, Optional, Union, Dict, Any

# Third-party types
from pydantic import ValidationError

# Local types and enums
from line_api.flex_messages import (
    # Components
    FlexMessage, FlexBubble, FlexBox, FlexText,
    # Enums
    FlexLayout, FlexTextSize, FlexWeight, FlexAlignment,
    # Type aliases
    FlexComponent, FlexContainer
)
```

### Type Annotation Consistency

```python
# ✅ Consistent type annotations
def create_text_list(items: List[str]) -> List[FlexText]:
    return [FlexText.create(text=item) for item in items]

def create_message_box(texts: List[FlexText]) -> FlexBox:
    return FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=texts
    )

# ✅ Return type annotations for public functions
def create_product_message(product: Dict[str, Any]) -> FlexMessage:
    # Implementation with full type safety
    pass
```

### Error Handling Patterns

```python
from typing import Result, Union
from line_api.flex_messages import FlexText

# Result-like pattern for error handling
def safe_create_component(
    data: Dict[str, Any]
) -> Union[FlexText, ValidationError]:
    """Type-safe component creation with error handling."""
    try:
        return FlexText.create(**data)
    except ValidationError as e:
        return e

# Usage
result = safe_create_component({"text": "Hello", "size": "invalid"})
if isinstance(result, ValidationError):
    print(f"Validation failed: {result}")
else:
    # result is FlexText
    print(f"Created text: {result.text}")
```

This type safety guide provides comprehensive coverage of how to leverage Python's type system and Pydantic validation for robust FlexMessage development.
