# 🎨 Flex Message Elements Guide

This comprehensive guide covers all LINE Flex Message components with detailed explanations, properties, and examples.

## 📋 Overview

Flex Messages have a hierarchical structure with three levels:

1. **Container** - Top level (Bubble, Carousel)
2. **Block** - Middle level (Header, Hero, Body, Footer)
3. **Component** - Content level (Text, Image, Button, etc.)

## 🏗️ Architecture

```
FlexMessage
├── FlexBubble (Container)
│   ├── header: FlexBox (Block)
│   ├── hero: FlexImage | FlexVideo | FlexBox (Block)
│   ├── body: FlexBox (Block)
│   └── footer: FlexBox (Block)
└── FlexCarousel (Container)
    └── contents: List[FlexBubble]
```

## 📦 Containers

### FlexBubble

A container that displays a single message bubble.

```python
from line_api.flex_messages import FlexBubble, FlexBubbleSize, FlexDirection

bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,
    direction=FlexDirection.LTR,
    header=header_box,
    hero=hero_content,
    body=body_box,
    footer=footer_box,
    styles={"body": {"backgroundColor": "#f0f0f0"}},
    action=action  # Optional bubble-level action
)
```

**Properties:**
- `size`: Bubble size (nano, micro, kilo, mega, giga)
- `direction`: Text direction (ltr, rtl)
- `header`: Header block content
- `hero`: Hero block content (image, video, or box)
- `body`: Body block content
- `footer`: Footer block content
- `styles`: Style overrides for blocks
- `action`: Action triggered when bubble is tapped

**Size Requirements:**
- **Video support**: Requires `kilo`, `mega`, or `giga` size
- **Default**: No size restriction

### FlexCarousel

A container that displays multiple bubbles in a horizontal carousel.

```python
from line_api.flex_messages import FlexCarousel

carousel = FlexCarousel.create([
    bubble1,
    bubble2,
    bubble3
])
```

**Properties:**
- `contents`: List of FlexBubble objects (max 12)

**Limitations:**
- Cannot contain video components
- Each bubble must be properly sized for mobile display

## 🧱 Components

### FlexText

Renders text strings with comprehensive styling options.

```python
from line_api.flex_messages import (
    FlexText, FlexSize, FlexTextWeight, FlexAlignment,
    FlexGravity, FlexAdjustMode
)

text = FlexText.create(
    "Enhanced text content",
    size=FlexSize.LG,
    weight=FlexTextWeight.BOLD,
    color="#333333",
    align=FlexAlignment.CENTER,
    gravity=FlexGravity.CENTER,
    wrap=True,
    line_spacing="8px",
    max_lines=3,
    flex=1,
    margin=FlexSpacing.MD,
    adjust_mode=FlexAdjustMode.SHRINK_TO_FIT,
    scaling=True,
    action=text_action
)
```

**Key Properties:**
- `text`: Text content (required)
- `contents`: List of FlexSpan for styled text segments
- `size`: Text size (xxs to 5xl, or pixels like "24px")
- `weight`: Text weight (regular, bold)
- `color`: Text color (hex color)
- `align`: Horizontal alignment (start, center, end)
- `gravity`: Vertical alignment (top, center, bottom)
- `wrap`: Enable text wrapping
- `line_spacing`: Line spacing in pixels
- `max_lines`: Maximum number of lines
- `adjust_mode`: Font scaling mode (shrink-to-fit)
- `scaling`: Accessibility scaling support
- `action`: Action when text is tapped

**Advanced Features:**
- **Styled Text**: Use `contents` with FlexSpan for mixed styling
- **Line Spacing**: Control spacing between wrapped lines
- **Auto-scaling**: Responsive text sizing
- **Accessibility**: Automatic scaling based on user preferences

### FlexSpan

Renders styled text segments within FlexText components.

```python
from line_api.flex_messages import FlexSpan, FlexTextDecoration

spans = [
    FlexSpan.create("Bold text ", weight=FlexTextWeight.BOLD),
    FlexSpan.create("red text ", color="#ff0000"),
    FlexSpan.create("underlined", decoration=FlexTextDecoration.UNDERLINE)
]

text = FlexText.create("Mixed styles: ", contents=spans)
```

**Properties:**
- `text`: Text content (required)
- `size`: Text size (xxs to 5xl, or pixels)
- `weight`: Text weight (regular, bold)
- `color`: Text color (hex)
- `decoration`: Text decoration (none, underline, line-through)

### FlexButton

Renders interactive buttons with actions.

```python
from line_api.flex_messages import (
    FlexButton, FlexButtonStyle, FlexButtonHeight, FlexUriAction
)

action = FlexUriAction(uri="https://example.com", label="Visit")

button = FlexButton.create(
    action=action,
    style=FlexButtonStyle.PRIMARY,
    color="#ff6b6b",
    height=FlexButtonHeight.MD,
    gravity=FlexGravity.CENTER,
    flex=1,
    margin=FlexSpacing.SM,
    adjust_mode=FlexAdjustMode.SHRINK_TO_FIT,
    scaling=True
)
```

**Properties:**
- `action`: Button action (required) - URI, message, or postback
- `style`: Button style (primary, secondary, link)
- `color`: Custom button color
- `height`: Button height (sm, md)
- `gravity`: Vertical alignment
- `adjust_mode`: Font scaling mode
- `scaling`: Accessibility scaling

**Button Styles:**
- **Primary**: Filled button with primary color
- **Secondary**: Outlined button
- **Link**: Text-only button

### FlexImage

Renders images with advanced control options.

```python
from line_api.flex_messages import (
    FlexImage, FlexImageAspectMode, FlexAlignment
)

image = FlexImage.create(
    url="https://example.com/image.jpg",
    size=FlexSize.FULL,
    aspect_ratio="16:9",
    aspect_mode=FlexImageAspectMode.COVER,
    background_color="#f0f0f0",
    gravity=FlexGravity.CENTER,
    flex=0,
    align=FlexAlignment.CENTER,
    animated=True,
    margin=FlexSpacing.MD,
    action=image_action
)
```

**Properties:**
- `url`: Image URL (required)
- `size`: Image size (xxs to full, percentage, or pixels)
- `aspect_ratio`: Image aspect ratio (e.g., "16:9", "1:1")
- `aspect_mode`: How image fits (cover, fit)
- `background_color`: Background color behind image
- `gravity`: Vertical alignment
- `align`: Horizontal alignment
- `animated`: Support for animated GIFs
- `action`: Action when image is tapped

**Size Options:**
- **Keywords**: xxs, xs, sm, md, lg, xl, xxl, 3xl, 4xl, 5xl, full
- **Percentage**: "50%", "75%"
- **Pixels**: "100px", "150px"

### FlexVideo

Renders video content in hero blocks with fallback support.

```python
from line_api.flex_messages import FlexVideo, FlexImage

# Fallback content for unsupported clients
alt_image = FlexImage.create(
    url="https://example.com/thumbnail.jpg",
    size=FlexSize.FULL,
    aspect_ratio="16:9",
    aspect_mode=FlexImageAspectMode.COVER
)

video = FlexVideo.create(
    url="https://example.com/video.mp4",
    preview_url="https://example.com/preview.jpg",
    alt_content=alt_image,
    aspect_ratio="16:9",
    action=video_action
)
```

**Properties:**
- `url`: Video file URL (required)
- `preview_url`: Preview image URL (required)
- `alt_content`: Fallback content for unsupported clients (required)
- `aspect_ratio`: Video aspect ratio (required)
- `action`: URI action for additional interactions

**Requirements:**
- Must be used in hero block only
- Bubble size must be kilo, mega, or giga
- Cannot be used in carousels
- Requires fallback content for compatibility

### FlexIcon

Renders decorative icons for baseline layouts.

```python
from line_api.flex_messages import FlexIcon

icon = FlexIcon.create(
    url="https://example.com/icon.png",
    size=FlexSize.MD,
    aspect_ratio="1:1",
    margin=FlexSpacing.XS,
    scaling=True
)
```

**Properties:**
- `url`: Icon image URL (required)
- `size`: Icon size (xxs to 5xl, or pixels)
- `aspect_ratio`: Icon aspect ratio
- `margin`: Margin around icon
- `scaling`: Accessibility scaling support

**Usage Restrictions:**
- Can only be used in baseline layout boxes
- Typically used for decorative purposes
- Aligned by baseline with adjacent text

### FlexSeparator

Renders separating lines between components.

```python
from line_api.flex_messages import FlexSeparator

separator = FlexSeparator.create(
    margin=FlexSpacing.MD,
    color="#e0e0e0"
)
```

**Properties:**
- `margin`: Margin around separator
- `color`: Separator line color

**Behavior:**
- Horizontal line in vertical layouts
- Vertical line in horizontal layouts

### FlexBox

Container component for organizing other components with advanced layout control.

```python
from line_api.flex_messages import (
    FlexBox, FlexLayout, FlexJustifyContent, FlexAlignItems,
    FlexLinearGradient
)

# Create gradient background
gradient = FlexLinearGradient.create(
    angle="45deg",
    start_color="#ff6b6b",
    end_color="#4ecdc4",
    center_color="#45b7d1",
    center_position="50%"
)

box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[text1, text2, button],
    flex=1,
    spacing=FlexSpacing.MD,
    margin=FlexSpacing.LG,
    width="100%",
    max_width="300px",
    height="200px",
    padding_all=FlexSpacing.LG,
    background_color="#ffffff",
    background=gradient,
    border_color="#dddddd",
    border_width="1px",
    corner_radius="8px",
    justify_content=FlexJustifyContent.SPACE_BETWEEN,
    align_items=FlexAlignItems.CENTER,
    action=box_action
)
```

**Layout Properties:**
- `layout`: Box orientation (vertical, horizontal, baseline)
- `contents`: List of child components
- `justify_content`: Main axis distribution
- `align_items`: Cross axis alignment
- `spacing`: Space between child components

**Size Properties:**
- `width`: Box width (pixels or percentage)
- `max_width`: Maximum width constraint
- `height`: Box height (pixels or percentage)
- `max_height`: Maximum height constraint
- `flex`: Flex grow factor

**Spacing Properties:**
- `margin`: External margin
- `padding_all`: Internal padding (all sides)
- `padding_top`, `padding_bottom`, `padding_start`, `padding_end`: Individual padding

**Appearance Properties:**
- `background_color`: Solid background color
- `background`: Linear gradient background
- `border_color`: Border color
- `border_width`: Border thickness
- `corner_radius`: Rounded corners

**Position Properties:**
- `position`: Positioning mode (relative, absolute)
- `offset_top`, `offset_bottom`, `offset_start`, `offset_end`: Position offsets

## 🎛️ Actions

### FlexUriAction

Opens URLs or makes phone calls.

```python
from line_api.flex_messages import FlexUriAction

uri_action = FlexUriAction(
    uri="https://example.com",
    label="Visit Website",
    alt_uri_desktop="https://example.com/desktop"
)
```

### FlexMessageAction

Sends a message when triggered.

```python
from line_api.flex_messages import FlexMessageAction

message_action = FlexMessageAction(
    text="Hello from Flex Message!",
    label="Send Hello"
)
```

### FlexPostbackAction

Sends postback data to your webhook.

```python
from line_api.flex_messages import FlexPostbackAction

postback_action = FlexPostbackAction(
    data="action=view&item=123",
    label="View Item",
    display_text="Viewing item 123"
)
```

## 🎨 Linear Gradients

Create sophisticated background gradients for boxes.

```python
from line_api.flex_messages import FlexLinearGradient

# Two-color gradient
gradient = FlexLinearGradient.create(
    angle="90deg",
    start_color="#ff6b6b",
    end_color="#4ecdc4"
)

# Three-color gradient with color stop
gradient = FlexLinearGradient.create(
    angle="45deg",
    start_color="#ff6b6b",
    center_color="#45b7d1",
    end_color="#4ecdc4",
    center_position="30%"
)
```

**Properties:**
- `angle`: Gradient direction (0deg to 359deg)
- `start_color`: Starting color
- `end_color`: Ending color
- `center_color`: Middle color (optional)
- `center_position`: Position of middle color (optional)

**Angle Reference:**
- `0deg`: Bottom to top
- `45deg`: Bottom-left to top-right
- `90deg`: Left to right
- `180deg`: Top to bottom

## ⚠️ Deprecated Components

### FlexFiller (Deprecated)

```python
# Deprecated - Use padding/margin instead
filler = FlexFiller.create(flex=1)
```

**Replacement:** Use `margin` and `padding` properties on components and boxes for spacing.

## 🔗 Component Relationships

### Layout Compatibility

| Component | Vertical Box | Horizontal Box | Baseline Box |
|-----------|--------------|----------------|--------------|
| FlexBox | ✅ | ✅ | ❌ |
| FlexButton | ✅ | ✅ | ❌ |
| FlexImage | ✅ | ✅ | ❌ |
| FlexText | ✅ | ✅ | ✅ |
| FlexIcon | ❌ | ❌ | ✅ |
| FlexSeparator | ✅ | ✅ | ❌ |
| FlexVideo | Hero block only | Hero block only | ❌ |

### Hero Block Compatibility

| Component | Hero Block Support |
|-----------|-------------------|
| FlexImage | ✅ |
| FlexVideo | ✅ |
| FlexBox | ✅ |
| Other components | ❌ (must be in FlexBox) |

## 📝 Examples

### Complete Message Example

```python
from line_api.flex_messages import *

# Create styled text with spans
title_spans = [
    FlexSpan.create("Welcome to ", weight=FlexTextWeight.BOLD),
    FlexSpan.create("Coffee Shop", color="#8B4513", weight=FlexTextWeight.BOLD)
]

title = FlexText.create(
    "Our amazing cafe!",
    contents=title_spans,
    size=FlexSize.XL,
    align=FlexAlignment.CENTER
)

# Create rating with icons
stars = [FlexIcon.create(
    url="https://example.com/star.png",
    size=FlexSize.SM
) for _ in range(4)]

rating_box = FlexBox.create(
    layout=FlexLayout.BASELINE,
    contents=stars + [
        FlexText.create("4.0", size=FlexSize.SM, flex=0, margin=FlexSpacing.MD)
    ]
)

# Create action buttons
call_button = FlexButton.create(
    action=FlexUriAction(uri="tel:+1234567890", label="Call"),
    style=FlexButtonStyle.PRIMARY,
    color="#28a745"
)

website_button = FlexButton.create(
    action=FlexUriAction(uri="https://cafe.example.com", label="Website"),
    style=FlexButtonStyle.SECONDARY
)

# Create gradient background
gradient = FlexLinearGradient.create(
    angle="135deg",
    start_color="#667eea",
    end_color="#764ba2"
)

# Assemble the message
header = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[title],
    padding_all=FlexSpacing.LG,
    background=gradient
)

body = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[rating_box],
    spacing=FlexSpacing.MD,
    padding_all=FlexSpacing.LG
)

footer = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    contents=[call_button, website_button],
    spacing=FlexSpacing.SM,
    padding_all=FlexSpacing.LG
)

bubble = FlexBubble.create(
    size=FlexBubbleSize.KILO,
    header=header,
    body=body,
    footer=footer
)

message = FlexMessage.create(
    alt_text="Coffee Shop Information",
    contents=bubble
)
```

## 🔍 Related Documentation

- **[Layout Guide](layout.md)** - Advanced layout techniques
- **[Video Guide](video.md)** - Video component details
- **[Properties Reference](properties-reference.md)** - Complete property reference
- **[Type Safety Guide](type-safety.md)** - Pydantic validation details

## 🏷️ Tags
`flex-elements` `components` `pydantic` `line-api` `documentation`
