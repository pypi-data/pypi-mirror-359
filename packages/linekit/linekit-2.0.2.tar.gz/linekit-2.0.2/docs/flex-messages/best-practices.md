# FlexMessage Best Practices

Comprehensive guide to building maintainable, performant, and user-friendly FlexMessages.

## Design Principles

### User-Centered Design

**Prioritize User Experience**:
- Keep messages concise and scannable
- Use clear visual hierarchy with headings and spacing
- Ensure important actions are easily accessible
- Test on different screen sizes and devices

**Content Organization**:
```python
from line_api.flex_messages import (
    FlexBubble, FlexBox, FlexLayout, FlexText, FlexWeight, FlexTextSize,
    FlexSeparator, FlexButton, FlexButtonStyle, FlexUriAction
)

# ✅ Good: Clear hierarchy and organization
bubble = FlexBubble.create(
    body=FlexBox.create(
        layout=FlexLayout.VERTICAL,
        spacing="md",
        contents=[
            # Primary information first
            FlexText.create("Product Launch", weight=FlexWeight.BOLD, size=FlexTextSize.LARGE),
            FlexText.create("New iPhone 15 Pro", size=FlexTextSize.MEDIUM, color="#666666"),

            # Separator for visual break
            FlexSeparator.create(margin="lg"),

            # Secondary details
            FlexText.create("Available now with advanced features", wrap=True, margin="md"),

            # Clear call-to-action
            FlexButton.create(
                action=FlexUriAction(uri="https://apple.com", label="Learn More"),
                style=FlexButtonStyle.PRIMARY,
                margin="lg"
            )
        ]
    )
)
```

### Progressive Disclosure

Reveal information progressively to avoid overwhelming users:

```python
from typing import Dict
from line_api.flex_messages import (
    FlexBubble, FlexImage, FlexBox, FlexLayout, FlexText, FlexWeight,
    FlexTextSize, FlexButton, FlexButtonStyle, FlexUriAction
)

# ✅ Good: Progressive information disclosure
def create_product_overview(product: Dict) -> FlexBubble:
    return FlexBubble.create(
        hero=FlexImage.create(url=product['image_url'], aspectRatio="16:9"),
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=[
                # Essential info first
                FlexText.create(product['name'], weight=FlexWeight.BOLD, size=FlexTextSize.LARGE),
                FlexText.create(f"${product['price']}", color="#ff6b6b", size=FlexTextSize.MEDIUM),

                # Brief description
                FlexText.create(
                    product['brief_description'],
                    wrap=True,
                    margin="md",
                    color="#666666"
                )
            ]
        ),
        footer=FlexBox.create(
            layout=FlexLayout.HORIZONTAL,
            spacing="sm",
            contents=[
                FlexButton.create(
                    action=FlexUriAction(uri=f"/product/{product['id']}", label="Details"),
                    style=FlexButtonStyle.SECONDARY,
                    flex=1
                ),
                FlexButton.create(
                    action=FlexUriAction(uri=f"/buy/{product['id']}", label="Buy Now"),
                    style=FlexButtonStyle.PRIMARY,
                    flex=1
                )
            ]
        )
    )
```

## Layout Strategies

### Responsive Design

Design for various screen sizes and orientations:

```python
# ✅ Good: Responsive layout using flex properties
def create_responsive_card() -> FlexBubble:
    return FlexBubble.create(
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            paddingAll="md",  # Consistent padding
            contents=[
                # Header adapts to content
                FlexBox.create(
                    layout=FlexLayout.HORIZONTAL,
                    contents=[
                        FlexText.create("Title", weight=FlexWeight.BOLD, flex=1),
                        FlexText.create("$99", color="#ff6b6b", flex=0)  # Fixed width for price
                    ]
                ),

                # Content scales with container
                FlexText.create(
                    "Description that wraps naturally on smaller screens",
                    wrap=True,
                    margin="md"
                ),

                # Buttons stack on mobile, row on larger screens
                FlexBox.create(
                    layout=FlexLayout.HORIZONTAL,
                    spacing="sm",
                    margin="lg",
                    contents=[
                        FlexButton.create(action=action1, flex=1),
                        FlexButton.create(action=action2, flex=1)
                    ]
                )
            ]
        )
    )
```

### Grid Layouts

Create grid-like structures using nested boxes:

```python
def create_feature_grid() -> FlexBox:
    """Create a 2x2 grid of features."""
    return FlexBox.create(
        layout=FlexLayout.VERTICAL,
        spacing="md",
        contents=[
            # First row
            FlexBox.create(
                layout=FlexLayout.HORIZONTAL,
                spacing="sm",
                contents=[
                    create_feature_card("Fast", "⚡", flex=1),
                    create_feature_card("Secure", "🔒", flex=1)
                ]
            ),
            # Second row
            FlexBox.create(
                layout=FlexLayout.HORIZONTAL,
                spacing="sm",
                contents=[
                    create_feature_card("Reliable", "✅", flex=1),
                    create_feature_card("Easy", "😊", flex=1)
                ]
            )
        ]
    )

def create_feature_card(title: str, icon: str, **kwargs) -> FlexBox:
    return FlexBox.create(
        layout=FlexLayout.VERTICAL,
        backgroundColor="#f8f9fa",
        cornerRadius="8px",
        paddingAll="md",
        contents=[
            FlexText.create(icon, align=FlexAlignment.CENTER, size=FlexTextSize.XX_LARGE),
            FlexText.create(title, align=FlexAlignment.CENTER, weight=FlexWeight.BOLD, margin="sm")
        ],
        **kwargs
    )
```

## Component Best Practices

### Text Components

**Typography Hierarchy**:
```python
# ✅ Good: Clear typography hierarchy
def create_article_content() -> List[FlexComponent]:
    return [
        # H1 - Main headline
        FlexText.create(
            "Breaking News",
            weight=FlexWeight.BOLD,
            size=FlexTextSize.XX_LARGE,
            color="#000000"
        ),

        # H2 - Subheadline
        FlexText.create(
            "Important Update",
            weight=FlexWeight.BOLD,
            size=FlexTextSize.LARGE,
            color="#333333",
            margin="md"
        ),

        # Body text
        FlexText.create(
            "Article content goes here with proper wrapping and readable spacing.",
            wrap=True,
            size=FlexTextSize.MEDIUM,
            color="#666666",
            lineSpacing="18px",
            margin="sm"
        ),

        # Caption
        FlexText.create(
            "Source: News Agency",
            size=FlexTextSize.SMALL,
            color="#999999",
            margin="md"
        )
    ]
```

**Text Length Guidelines**:
- **Headlines**: 50-60 characters max
- **Descriptions**: 120-150 characters for mobile
- **Button labels**: 15-25 characters
- **Alt text**: Descriptive but concise

### Image Components

**Image Optimization**:
```python
from line_api.flex_messages import FlexImage, FlexImageAspectMode, FlexUriAction

# ✅ Good: Optimized image usage
def create_product_image(product_url: str) -> FlexImage:
    return FlexImage.create(
        url=product_url,
        size="full",
        aspectRatio="16:9",           # Consistent aspect ratio
        aspectMode=FlexImageAspectMode.COVER,  # Prevent distortion
        backgroundColor="#f0f0f0",    # Fallback background
        action=FlexUriAction(         # Make images interactive
            uri=f"{product_url}?view=fullsize",
            label="View Full Size",
        )
    )
```

**Image Guidelines**:
- Use HTTPS URLs only
- Optimize file sizes (aim for <500KB)
- Provide consistent aspect ratios
- Include fallback background colors
- Test loading on slow connections

### Button Components

**Action Hierarchy**:
```python
from line_api.flex_messages import (
    FlexBox, FlexLayout, FlexButton, FlexButtonStyle, FlexButtonHeight, FlexUriAction
)

def create_action_buttons() -> FlexBox:
    return FlexBox.create(
        layout=FlexLayout.VERTICAL,
        spacing="sm",
        contents=[
            # Primary action - most important
            FlexButton.create(
                action=FlexUriAction(uri="/purchase", label="Buy Now"),
                style=FlexButtonStyle.PRIMARY,
                height=FlexButtonHeight.MEDIUM
            ),

            # Secondary action - supporting
            FlexButton.create(
                action=FlexUriAction(uri="/details", label="Learn More"),
                style=FlexButtonStyle.SECONDARY,
                height=FlexButtonHeight.MEDIUM
            ),

            # Tertiary action - least important
            FlexButton.create(
                action=FlexUriAction(uri="/wishlist", label="Add to Wishlist"),
                style=FlexButtonStyle.LINK,
                height=FlexButtonHeight.SMALL
            )
        ]
    )
```

**Button Guidelines**:
- Limit to 3 actions maximum per message
- Use clear, action-oriented labels
- Follow platform color conventions
- Ensure sufficient touch target size

## Performance Optimization

### Component Reuse

Create reusable component functions:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def create_star_rating(rating: float, max_stars: int = 5) -> FlexBox:
    """Cached star rating component."""
    full_stars = int(rating)
    has_half = rating % 1 >= 0.5

    stars = []
    for i in range(max_stars):
        if i < full_stars:
            stars.append(FlexIcon.create(url="https://cdn.example.com/star-full.png", size="sm"))
        elif i == full_stars and has_half:
            stars.append(FlexIcon.create(url="https://cdn.example.com/star-half.png", size="sm"))
        else:
            stars.append(FlexIcon.create(url="https://cdn.example.com/star-empty.png", size="sm"))

    stars.append(FlexText.create(f"{rating:.1f}", size="sm", margin="sm", color="#666666"))

    return FlexBox.create(
        layout=FlexLayout.BASELINE,
        spacing="xs",
        contents=stars
    )
```

### Message Size Optimization

Keep messages lean for better performance:

```python
# ✅ Good: Efficient message structure
def create_efficient_card(data: Dict) -> FlexMessage:
    # Build only necessary components
    bubble = FlexBubble.create(
        size=FlexBubbleSize.KILO,  # Use appropriate size
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=[
                FlexText.create(data['title'], weight=FlexWeight.BOLD),
                FlexText.create(data['description'], wrap=True, margin="sm") if data.get('description') else None,
                create_action_button(data['action_url'], data['action_label'])
            ]
        )
    )

    # Filter out None components
    bubble.body.contents = [c for c in bubble.body.contents if c is not None]

    return FlexMessage.create(
        altText=data['title'],
        contents=bubble
    )

# ❌ Avoid: Overly complex nested structures
def create_heavy_card() -> FlexMessage:
    # Too many nested levels
    return FlexMessage.create(
        altText="Heavy card",
        contents=FlexBubble.create(
            body=FlexBox.create(
                layout=FlexLayout.VERTICAL,
                contents=[
                    FlexBox.create(  # Unnecessary wrapper
                        layout=FlexLayout.HORIZONTAL,
                        contents=[
                            FlexBox.create(  # Another unnecessary wrapper
                                layout=FlexLayout.VERTICAL,
                                contents=[
                                    FlexText.create("Over-nested content")
                                ]
                            )
                        ]
                    )
                ]
            )
        )
    )
```

## Accessibility

### Screen Reader Support

Provide meaningful alternative text:

```python
def create_accessible_message() -> FlexMessage:
    bubble = FlexBubble.create(
        hero=FlexImage.create(
            url="https://example.com/product.jpg",
            aspectRatio="16:9"
        ),
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=[
                FlexText.create("iPhone 15 Pro", weight=FlexWeight.BOLD),
                FlexText.create("Starting at $999", color="#666666")
            ]
        )
    )

    return FlexMessage.create(
        # Descriptive alt text for screen readers
        altText="iPhone 15 Pro product announcement - Starting at $999",
        contents=bubble
    )
```

### High Contrast Design

Ensure sufficient color contrast:

```python
# ✅ Good: High contrast colors
COLORS = {
    'primary_text': '#000000',     # Black on white = 21:1 ratio
    'secondary_text': '#666666',   # Dark gray = 5.7:1 ratio
    'accent': '#0066cc',           # Blue = 4.5:1 ratio
    'success': '#28a745',          # Green = 3.1:1 ratio (large text only)
    'error': '#dc3545',            # Red = 5.1:1 ratio
    'background': '#ffffff'        # White background
}

def create_accessible_text(text: str, level: str = 'primary') -> FlexText:
    return FlexText.create(
        text=text,
        color=COLORS[f'{level}_text'],
        size=FlexTextSize.MEDIUM if level == 'primary' else FlexTextSize.SMALL
    )
```

### Font Scaling Support

Enable font scaling for accessibility:

```python
def create_scalable_text(text: str, **kwargs) -> FlexText:
    return FlexText.create(
        text=text,
        scaling=True,  # Respects user's font size settings
        **kwargs
    )
```

## Error Handling

### Graceful Degradation

Handle missing data gracefully:

```python
def create_robust_product_card(product: Dict[str, Any]) -> FlexMessage:
    """Create product card with graceful error handling."""

    # Required fields with fallbacks
    title = product.get('name', 'Untitled Product')
    price = product.get('price')
    description = product.get('description', '')
    image_url = product.get('image_url')

    # Build content list dynamically
    contents = [
        FlexText.create(title, weight=FlexWeight.BOLD, size=FlexTextSize.LARGE)
    ]

    # Add price if available
    if price is not None:
        contents.append(
            FlexText.create(f"${price:.2f}", color="#ff6b6b", margin="sm")
        )

    # Add description if available and not empty
    if description.strip():
        contents.append(
            FlexText.create(description, wrap=True, margin="md", color="#666666")
        )

    # Create bubble with hero image if available
    bubble_kwargs = {
        'body': FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=contents
        )
    }

    if image_url:
        bubble_kwargs['hero'] = FlexImage.create(
            url=image_url,
            size="full",
            aspectRatio="16:9",
            aspectMode=FlexImageAspectMode.COVER
        )

    return FlexMessage.create(
        altText=f"Product: {title}" + (f" - ${price:.2f}" if price else ""),
        contents=FlexBubble.create(**bubble_kwargs)
    )
```

### Validation and Fallbacks

Implement robust validation:

```python
from pydantic import ValidationError
from typing import Optional

def safe_create_flex_message(data: Dict[str, Any]) -> Optional[FlexMessage]:
    """Safely create FlexMessage with validation and fallbacks."""
    try:
        return create_product_card(data)
    except ValidationError as e:
        print(f"FlexMessage validation failed: {e}")
        # Return simple fallback message
        return FlexMessage.create(
            altText=data.get('title', 'Product Update'),
            contents=FlexBubble.create(
                body=FlexBox.create(
                    layout=FlexLayout.VERTICAL,
                    contents=[
                        FlexText.create(
                            data.get('title', 'Product Update'),
                            weight=FlexWeight.BOLD
                        ),
                        FlexText.create(
                            "Unable to display rich content. Please visit our website for details.",
                            wrap=True,
                            margin="md"
                        )
                    ]
                )
            )
        )
    except Exception as e:
        print(f"Unexpected error creating FlexMessage: {e}")
        return None
```

## Testing Strategies

### Component Testing

Test individual components thoroughly:

```python
import pytest
from line_api.flex_messages import FlexText, FlexTextSize, FlexWeight

def test_text_component_creation():
    """Test text component with various properties."""
    text = FlexText.create(
        text="Test text",
        size=FlexTextSize.LARGE,
        weight=FlexWeight.BOLD,
        color="#333333"
    )

    assert text.text == "Test text"
    assert text.size == "lg"
    assert text.weight == "bold"
    assert text.color == "#333333"

def test_text_component_defaults():
    """Test text component default values."""
    text = FlexText.create(text="Default text")

    assert text.text == "Default text"
    assert text.size is None  # Should use default
    assert text.weight is None
    assert text.color is None

@pytest.mark.parametrize("size,expected", [
    (FlexTextSize.SMALL, "sm"),
    (FlexTextSize.MEDIUM, "md"),
    (FlexTextSize.LARGE, "lg"),
    ("xs", "xs"),
    ("24px", "24px")
])
def test_text_size_values(size, expected):
    """Test various size value formats."""
    text = FlexText.create(text="Test", size=size)
    assert text.size == expected
```

### Integration Testing

Test complete message structures:

```python
def test_complete_product_message():
    """Test complete product message structure."""
    product_data = {
        'name': 'Test Product',
        'price': 29.99,
        'description': 'A great product for testing',
        'image_url': 'https://example.com/product.jpg'
    }

    message = create_product_card(product_data)

    # Test message structure
    assert isinstance(message, FlexMessage)
    assert message.altText == "Product: Test Product - $29.99"

    # Test bubble structure
    bubble = message.contents
    assert isinstance(bubble, FlexBubble)
    assert bubble.hero is not None
    assert bubble.body is not None

    # Test content
    body_contents = bubble.body.contents
    assert len(body_contents) >= 2  # At least title and price

    title_text = body_contents[0]
    assert title_text.text == "Test Product"
    assert title_text.weight == "bold"
```

### Visual Testing

Test with Flex Message Simulator:

```python
from line_api.flex_messages.utils import export_flex_json

def test_visual_output():
    """Export messages for visual testing."""
    message = create_product_card({
        'name': 'Visual Test Product',
        'price': 99.99,
        'description': 'Test description for visual validation'
    })

    # Export for Flex Message Simulator
    export_flex_json(message, "test_product_card.json")

    # Manual verification:
    # 1. Open LINE Flex Message Simulator
    # 2. Import test_product_card.json
    # 3. Verify visual appearance
    # 4. Test on different screen sizes
```

## Code Organization

### Modular Architecture

Organize code into reusable modules:

```python
# flex_components/cards.py
def create_product_card(product: Dict) -> FlexMessage:
    """Product card component."""
    pass

def create_event_card(event: Dict) -> FlexMessage:
    """Event card component."""
    pass

# flex_components/layouts.py
def create_two_column_layout(left: FlexComponent, right: FlexComponent) -> FlexBox:
    """Two-column layout utility."""
    pass

def create_centered_content(content: FlexComponent) -> FlexBox:
    """Centered content wrapper."""
    pass

# flex_components/utils.py
def truncate_text(text: str, max_length: int = 100) -> str:
    """Utility for text truncation."""
    pass

def format_price(price: float, currency: str = "USD") -> str:
    """Utility for price formatting."""
    pass
```

### Configuration Management

Centralize styling and configuration:

```python
# config/flex_styles.py
from line_api.flex_messages import FlexTextSize, FlexWeight, FlexSpacing

class FlexTheme:
    # Typography
    HEADING_SIZE = FlexTextSize.LARGE
    BODY_SIZE = FlexTextSize.MEDIUM
    CAPTION_SIZE = FlexTextSize.SMALL

    HEADING_WEIGHT = FlexWeight.BOLD
    BODY_WEIGHT = FlexWeight.REGULAR

    # Colors
    PRIMARY_COLOR = "#007bff"
    SECONDARY_COLOR = "#6c757d"
    SUCCESS_COLOR = "#28a745"
    ERROR_COLOR = "#dc3545"

    TEXT_PRIMARY = "#000000"
    TEXT_SECONDARY = "#666666"
    TEXT_MUTED = "#999999"

    # Spacing
    SECTION_SPACING = FlexSpacing.LARGE
    ITEM_SPACING = FlexSpacing.MEDIUM
    TIGHT_SPACING = FlexSpacing.SMALL

# Usage
def create_themed_heading(text: str) -> FlexText:
    return FlexText.create(
        text=text,
        size=FlexTheme.HEADING_SIZE,
        weight=FlexTheme.HEADING_WEIGHT,
        color=FlexTheme.TEXT_PRIMARY
    )
```

This comprehensive best practices guide covers design principles, performance optimization, accessibility, error handling, testing, and code organization for building high-quality FlexMessages.
