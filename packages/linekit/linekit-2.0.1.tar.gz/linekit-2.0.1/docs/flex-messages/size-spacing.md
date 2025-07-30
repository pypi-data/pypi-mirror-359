# FlexMessage Size and Spacing Reference

Detailed reference for all size and spacing values in FlexMessage components.

## Size Values

### Text Size Reference

Text sizes are used for `FlexText`, `FlexSpan`, and `FlexIcon` components.

| Keyword | Approximate Size | CSS Equivalent | Use Case |
|---------|------------------|----------------|-----------|
| `xxs` | 8px | `font-size: 8px` | Tiny labels, legal text |
| `xs` | 10px | `font-size: 10px` | Small captions, metadata |
| `sm` | 12px | `font-size: 12px` | Secondary text, descriptions |
| `md` | 14px | `font-size: 14px` | Body text (default) |
| `lg` | 16px | `font-size: 16px` | Emphasized text, subtitles |
| `xl` | 18px | `font-size: 18px` | Section headings |
| `xxl` | 20px | `font-size: 20px` | Page headings |
| `3xl` | 24px | `font-size: 24px` | Large headings |
| `4xl` | 28px | `font-size: 28px` | Display headings |
| `5xl` | 32px | `font-size: 32px` | Hero text |

#### Custom Text Sizes

You can also specify exact pixel values:

```python
from line_api.flex_messages import FlexText

# Custom pixel sizes
text = FlexText.create("Custom size", size="22px")
text = FlexText.create("Large custom", size="36px")
text = FlexText.create("Small custom", size="9px")
```

**Guidelines**:
- Use keywords for consistency across designs
- Use custom pixels for precise control
- Ensure readability on mobile devices (minimum 12px recommended)
- Test with different LINE app font size settings

### Image Size Reference

Image sizes determine the width of `FlexImage` components. Height adjusts automatically based on aspect ratio.

#### Keyword Sizes

| Keyword | Responsive | Typical Width | Use Case |
|---------|------------|---------------|-----------|
| `xxs` | ✅ | ~32px | Tiny icons, badges |
| `xs` | ✅ | ~48px | Small icons, avatars |
| `sm` | ✅ | ~64px | Medium icons |
| `md` | ✅ | ~80px | Default image size |
| `lg` | ✅ | ~96px | Large icons, small photos |
| `xl` | ✅ | ~128px | Medium photos |
| `xxl` | ✅ | ~160px | Large photos |
| `3xl` | ✅ | ~192px | Hero images |
| `4xl` | ✅ | ~224px | Feature images |
| `5xl` | ✅ | ~256px | Cover images |
| `full` | ✅ | 100% width | Full-width images |

#### Percentage Sizes

Percentage values are relative to the original image dimensions:

```python
from line_api.flex_messages import FlexImage

# 75% of original image size
image = FlexImage.create(
    url="https://example.com/image.jpg",
    size="75%"
)

# 50% of original image size
image = FlexImage.create(
    url="https://example.com/image.jpg",
    size="50%"
)
```

#### Pixel Sizes

Fixed pixel widths for precise control:

```python
# Fixed 200px width
image = FlexImage.create(
    url="https://example.com/image.jpg",
    size="200px"
)

# Fixed 150px width
image = FlexImage.create(
    url="https://example.com/image.jpg",
    size="150px"
)
```

### Icon Size Reference

Icon sizes are specifically for `FlexIcon` components used in baseline layouts.

| Keyword | Size | Use Case |
|---------|------|----------|
| `xxs` | ~12px | Tiny indicators |
| `xs` | ~16px | Small status icons |
| `sm` | ~20px | Standard icons |
| `md` | ~24px | Default icon size |
| `lg` | ~32px | Emphasized icons |
| `xl` | ~40px | Large icons |
| `xxl` | ~48px | Very large icons |
| `3xl` | ~56px | Hero icons |
| `4xl` | ~64px | Feature icons |
| `5xl` | ~72px | Display icons |

#### Icon Size Examples

```python
from line_api.flex_messages import FlexIcon, FlexBox, FlexText, FlexLayout

# Icon-text combinations at different sizes
def create_icon_text_row(icon_url: str, text: str, size: str) -> FlexBox:
    return FlexBox.create(
        layout=FlexLayout.BASELINE,
        spacing="sm",
        contents=[
            FlexIcon.create(url=icon_url, size=size),
            FlexText.create(text, size=size, flex=1)
        ]
    )

# Usage
small_row = create_icon_text_row("https://example.com/icon.png", "Small text", "sm")
medium_row = create_icon_text_row("https://example.com/icon.png", "Medium text", "md")
large_row = create_icon_text_row("https://example.com/icon.png", "Large text", "lg")
```

### Button Height Reference

Button heights control the vertical size of `FlexButton` components.

| Height | Size | Use Case |
|--------|------|----------|
| `sm` | ~32px | Compact buttons, secondary actions |
| `md` | ~40px | Standard buttons (default) |

```python
from line_api.flex_messages import FlexButton, FlexButtonHeight, FlexUriAction

# Small button
small_button = FlexButton.create(
    action=FlexUriAction(uri="https://example.com", label="Small"),
    height=FlexButtonHeight.SMALL
)

# Medium button (default)
medium_button = FlexButton.create(
    action=FlexUriAction(uri="https://example.com", label="Medium"),
    height=FlexButtonHeight.MEDIUM
)
```

### Bubble Size Reference

Bubble sizes affect the overall container size and video support.

| Size | Use Case | Video Support | Typical Width |
|------|----------|---------------|---------------|
| `nano` | Minimal content, status updates | ❌ | ~240px |
| `micro` | Small cards, notifications | ❌ | ~280px |
| `kilo` | Standard content, product cards | ✅ | ~320px |
| `mega` | Rich content, detailed cards | ✅ | ~360px |
| `giga` | Maximum content, galleries | ✅ | ~400px |

```python
from line_api.flex_messages import FlexBubble, FlexBubbleSize

# Different bubble sizes
nano_bubble = FlexBubble.create(size=FlexBubbleSize.NANO, body=content)
kilo_bubble = FlexBubble.create(size=FlexBubbleSize.KILO, body=content)
giga_bubble = FlexBubble.create(size=FlexBubbleSize.GIGA, body=content)
```

## Spacing Values

### Standard Spacing Scale

All spacing properties use the same scale for consistency.

| Keyword | Size | CSS Equivalent | Use Case |
|---------|------|----------------|-----------|
| `none` | 0px | `margin: 0` | No spacing |
| `xs` | 4px | `margin: 4px` | Tight spacing |
| `sm` | 8px | `margin: 8px` | Small spacing |
| `md` | 16px | `margin: 16px` | Standard spacing |
| `lg` | 24px | `margin: 24px` | Large spacing |
| `xl` | 32px | `margin: 32px` | Extra large spacing |
| `xxl` | 40px | `margin: 40px` | Maximum spacing |

### Box Spacing Property

Controls space between child components within a box.

```python
from line_api.flex_messages import FlexBox, FlexText, FlexSpacing

# Different spacing examples
tight_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing=FlexSpacing.X_SMALL,  # 4px between items
    contents=[
        FlexText.create("Item 1"),
        FlexText.create("Item 2"),
        FlexText.create("Item 3")
    ]
)

standard_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing=FlexSpacing.MEDIUM,  # 16px between items
    contents=[
        FlexText.create("Item 1"),
        FlexText.create("Item 2"),
        FlexText.create("Item 3")
    ]
)

spacious_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing=FlexSpacing.XX_LARGE,  # 40px between items
    contents=[
        FlexText.create("Item 1"),
        FlexText.create("Item 2"),
        FlexText.create("Item 3")
    ]
)
```

### Component Margin Property

Controls space before individual components, overriding parent spacing.

```python
from line_api.flex_messages import FlexBox, FlexText, FlexSeparator

box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="sm",  # Default 8px spacing
    contents=[
        FlexText.create("Normal spacing"),
        FlexText.create("Large margin", margin="xl"),  # 32px margin overrides spacing
        FlexSeparator.create(margin="lg"),  # 24px margin for separator
        FlexText.create("Back to normal spacing")
    ]
)
```

### Padding Properties

Controls inner spacing within box components.

#### Uniform Padding

```python
from line_api.flex_messages import FlexBox

# Same padding on all sides
box = FlexBox.create(
    paddingAll="md",  # 16px padding on all sides
    backgroundColor="#f0f0f0",
    contents=[
        FlexText.create("Padded content")
    ]
)
```

#### Directional Padding

```python
# Different padding on each side
box = FlexBox.create(
    paddingTop="lg",      # 24px top padding
    paddingBottom="lg",   # 24px bottom padding
    paddingStart="md",    # 16px start padding (left in LTR)
    paddingEnd="md",      # 16px end padding (right in LTR)
    backgroundColor="#f0f0f0",
    contents=[
        FlexText.create("Custom padded content")
    ]
)
```

#### Padding Priority

Directional padding takes precedence over `paddingAll`:

```python
box = FlexBox.create(
    paddingAll="xl",      # 32px - ignored where directional padding is set
    paddingTop="sm",      # 8px - overrides paddingAll for top
    paddingStart="lg",    # 24px - overrides paddingAll for start
    # paddingBottom and paddingEnd use paddingAll value (32px)
    contents=[content]
)
```

### Custom Spacing Values

#### Pixel Values

```python
# Custom pixel spacing
box = FlexBox.create(
    spacing="12px",       # Custom 12px spacing
    paddingAll="20px",    # Custom 20px padding
    contents=[
        FlexText.create("Custom spacing", margin="18px")
    ]
)
```

#### Percentage Values

Percentage values are relative to parent container:

```python
# Percentage padding (relative to parent width)
box = FlexBox.create(
    paddingStart="10%",   # 10% of parent width
    paddingEnd="5%",      # 5% of parent width
    contents=[content]
)
```

## Responsive Spacing

### Device-Adaptive Spacing

Spacing adapts to different screen sizes and device types:

```python
# Spacing that works well across devices
def create_responsive_card() -> FlexBubble:
    return FlexBubble.create(
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            paddingAll="md",     # Comfortable padding
            spacing="sm",        # Not too tight, not too loose
            contents=[
                FlexText.create("Title", size="lg", weight="bold"),
                FlexText.create("Subtitle", margin="xs", color="#666666"),
                FlexSeparator.create(margin="md"),
                FlexText.create("Content", wrap=True, margin="sm")
            ]
        )
    )
```

### Spacing Guidelines by Content Type

#### Text-Heavy Content

```python
# Generous spacing for readability
article_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    paddingAll="lg",      # 24px padding for comfortable reading
    spacing="md",         # 16px between paragraphs
    contents=[
        FlexText.create("Heading", size="xl", weight="bold"),
        FlexText.create("Subheading", margin="sm", color="#666666"),
        FlexText.create("Paragraph 1", wrap=True, margin="md"),
        FlexText.create("Paragraph 2", wrap=True)
    ]
)
```

#### Form-Like Content

```python
# Tighter spacing for form elements
form_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    paddingAll="md",      # 16px padding
    spacing="sm",         # 8px between form elements
    contents=[
        FlexText.create("Form Title", weight="bold"),
        FlexText.create("Field 1", margin="xs"),
        FlexText.create("Field 2"),
        FlexText.create("Field 3"),
        FlexButton.create(action=submit_action, margin="md")
    ]
)
```

#### Icon Grid

```python
# Minimal spacing for icon grids
icon_grid = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    spacing="xs",         # 4px between icons
    contents=[
        FlexIcon.create(url="icon1.png", size="md"),
        FlexIcon.create(url="icon2.png", size="md"),
        FlexIcon.create(url="icon3.png", size="md"),
        FlexIcon.create(url="icon4.png", size="md")
    ]
)
```

## Best Practices

### Consistent Spacing Scale

Use the standard spacing scale for visual consistency:

```python
# ✅ Good: Consistent spacing scale
box = FlexBox.create(
    spacing="md",          # 16px
    paddingAll="lg",       # 24px (next step up)
    contents=[
        FlexText.create("Content", margin="sm")  # 8px (step down)
    ]
)

# ❌ Avoid: Random pixel values
box = FlexBox.create(
    spacing="13px",        # Random value
    paddingAll="19px",     # Random value
    contents=[
        FlexText.create("Content", margin="11px")  # Random value
    ]
)
```

### Hierarchy Through Spacing

Use spacing to create visual hierarchy:

```python
def create_hierarchical_content() -> FlexBox:
    return FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            # Main heading - large spacing after
            FlexText.create("Main Title", size="xxl", weight="bold"),

            # Section 1 - medium spacing
            FlexText.create("Section 1", size="lg", weight="bold", margin="lg"),
            FlexText.create("Section content", margin="sm"),

            # Section 2 - medium spacing
            FlexText.create("Section 2", size="lg", weight="bold", margin="lg"),
            FlexText.create("Section content", margin="sm"),

            # Footer - extra large spacing before
            FlexText.create("Footer", size="sm", color="#666666", margin="xxl")
        ]
    )
```

### Touch Target Sizing

Ensure adequate spacing for touch interactions:

```python
# ✅ Good: Adequate spacing for touch targets
button_row = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    spacing="md",         # 16px between buttons (minimum recommended)
    contents=[
        FlexButton.create(action=action1, flex=1),
        FlexButton.create(action=action2, flex=1)
    ]
)

# ❌ Avoid: Buttons too close together
cramped_buttons = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    spacing="xs",         # Only 4px - too cramped for touch
    contents=[
        FlexButton.create(action=action1, flex=1),
        FlexButton.create(action=action2, flex=1)
    ]
)
```

This comprehensive size and spacing reference provides detailed information for creating well-proportioned and visually appealing FlexMessages.
