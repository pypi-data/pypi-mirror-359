# FlexMessage Components Reference

Complete reference for all FlexMessage components with properties, methods, and usage examples.

## Container Components

### FlexMessage

The top-level FlexMessage container.

```python
from line_api.flex_messages import FlexMessage

message = FlexMessage.create(
    altText="Alternative text for accessibility",
    contents=bubble_or_carousel
)
```

**Properties**:
- `altText` (required): Text displayed in push notifications and chat lists
- `contents` (required): FlexBubble or FlexCarousel

### FlexBubble

Single message bubble container.

```python
from line_api.flex_messages import FlexBubble, FlexBubbleSize, FlexDirection

bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,
    direction=FlexDirection.LTR,
    header=header_box,
    hero=hero_component,
    body=body_box,
    footer=footer_box,
    styles=bubble_styles
)
```

**Properties**:
- `size`: Bubble size (`nano`, `micro`, `kilo`, `mega`, `giga`)
- `direction`: Text direction (`ltr`, `rtl`)
- `header`: Header block component
- `hero`: Hero block component (image or video)
- `body`: Body block component
- `footer`: Footer block component
- `styles`: Bubble styling options

### FlexCarousel

Container for multiple bubbles in horizontal scroll.

```python
from line_api.flex_messages import FlexCarousel

carousel = FlexCarousel.create(
    contents=[bubble1, bubble2, bubble3]
)
```

**Properties**:
- `contents` (required): List of FlexBubble components (max 12)

## Layout Components

### FlexBox

Container for organizing child components.

```python
from line_api.flex_messages import (
    FlexBox, FlexLayout, FlexJustifyContent, FlexAlignItems
)

box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[component1, component2],
    flex=1,
    spacing="md",
    margin="lg",
    paddingAll="sm",
    backgroundColor="#f0f0f0",
    borderWidth="2px",
    borderColor="#cccccc",
    cornerRadius="8px",
    justifyContent=FlexJustifyContent.CENTER,
    alignItems=FlexAlignItems.CENTER,
    background=gradient_background,
    position="relative",
    offsetTop="10px",
    width="100%",
    height="200px",
    maxWidth="400px",
    maxHeight="300px"
)
```

**Layout Properties**:
- `layout` (required): Box orientation (`vertical`, `horizontal`, `baseline`)
- `contents` (required): List of child components
- `flex`: Flexibility in parent container (0 or positive number)

**Spacing Properties**:
- `spacing`: Space between child components
- `margin`: Space before this component
- `paddingAll`: Inner padding on all sides
- `paddingTop`, `paddingBottom`, `paddingStart`, `paddingEnd`: Specific padding

**Visual Properties**:
- `backgroundColor`: Background color (hex color)
- `borderWidth`: Border thickness
- `borderColor`: Border color (hex color)
- `cornerRadius`: Rounded corner radius
- `background`: Linear gradient background

**Alignment Properties**:
- `justifyContent`: Main axis distribution
- `alignItems`: Cross axis alignment

**Position Properties**:
- `position`: Positioning type (`relative`, `absolute`)
- `offsetTop`, `offsetBottom`, `offsetStart`, `offsetEnd`: Position offsets

**Size Properties**:
- `width`, `height`: Fixed dimensions
- `maxWidth`, `maxHeight`: Maximum dimensions

## Content Components

### FlexText

Text content with rich formatting options.

```python
from line_api.flex_messages import (
    FlexText, FlexTextSize, FlexWeight, FlexAlignment, FlexGravity, FlexDecoration
)

text = FlexText.create(
    text="Hello, World!",
    contents=[span1, span2],  # For rich text with spans
    adjustMode="shrink-to-fit",
    flex=1,
    margin="md",
    position="relative",
    offsetStart="10px",
    size=FlexTextSize.LARGE,
    align=FlexAlignment.CENTER,
    gravity=FlexGravity.CENTER,
    wrap=True,
    lineSpacing="20px",
    weight=FlexWeight.BOLD,
    color="#333333",
    decoration=FlexDecoration.UNDERLINE,
    scaling=True
)
```

**Content Properties**:
- `text` (required): Text content (can include `\n` for line breaks)
- `contents`: List of FlexSpan components for rich text

**Layout Properties**:
- `flex`: Flexibility in parent container
- `margin`: Space before component
- `position`, `offsetTop`, etc.: Positioning

**Typography Properties**:
- `size`: Text size (keywords or pixels)
- `align`: Horizontal alignment (`start`, `center`, `end`)
- `gravity`: Vertical alignment (`top`, `center`, `bottom`)
- `wrap`: Enable text wrapping
- `lineSpacing`: Line spacing for wrapped text
- `weight`: Font weight (`regular`, `bold`)
- `color`: Text color (hex color)
- `decoration`: Text decoration (`none`, `underline`, `line-through`)

**Advanced Properties**:
- `adjustMode`: Auto-shrink behavior (`shrink-to-fit`)
- `scaling`: Scale with LINE app font size

### FlexSpan

Styled text segments within FlexText.

```python
from line_api.flex_messages import FlexSpan, FlexTextSize, FlexWeight, FlexDecoration

span = FlexSpan.create(
    text="Styled text",
    size=FlexTextSize.LARGE,
    weight=FlexWeight.BOLD,
    color="#ff0000",
    decoration=FlexDecoration.UNDERLINE
)
```

**Properties**:
- `text` (required): Text content
- `size`: Text size
- `weight`: Font weight
- `color`: Text color
- `decoration`: Text decoration

### FlexImage

Image component with various display options.

```python
from line_api.flex_messages import (
    FlexImage, FlexImageSize, FlexImageAspectMode, FlexAlignment, FlexGravity,
    FlexUriAction
)

image = FlexImage.create(
    url="https://example.com/image.jpg",
    flex=1,
    margin="md",
    position="relative",
    align=FlexAlignment.CENTER,
    gravity=FlexGravity.CENTER,
    size=FlexImageSize.FULL,
    aspectRatio="16:9",
    aspectMode=FlexImageAspectMode.COVER,
    backgroundColor="#f0f0f0",
    action=FlexUriAction(uri="https://example.com", label="View")
)
```

**Properties**:
- `url` (required): Image URL (HTTPS required)
- `flex`: Flexibility in parent container
- `margin`: Space before component
- `position`, etc.: Positioning
- `align`: Horizontal alignment
- `gravity`: Vertical alignment
- `size`: Image size (keywords, pixels, or percentage)
- `aspectRatio`: Image aspect ratio (e.g., "16:9")
- `aspectMode`: How image fits container (`cover`, `fit`)
- `backgroundColor`: Background color
- `action`: Action when image is tapped

### FlexVideo

Video component for hero blocks.

```python
from line_api.flex_messages import FlexVideo, FlexUriAction

video = FlexVideo.create(
    url="https://example.com/video.mp4",
    previewUrl="https://example.com/preview.jpg",
    altContent=fallback_image,
    aspectRatio="16:9",
    action=FlexUriAction(uri="https://example.com", label="Learn More")
)
```

**Properties**:
- `url` (required): Video file URL
- `previewUrl` (required): Preview image URL
- `altContent` (required): Fallback content for unsupported clients
- `aspectRatio` (required): Video aspect ratio
- `action`: Action when video is tapped

### FlexIcon

Small decorative icons for baseline layouts.

```python
from line_api.flex_messages import FlexIcon, FlexIconSize

icon = FlexIcon.create(
    url="https://example.com/icon.png",
    margin="sm",
    position="relative",
    offsetTop="2px",
    size=FlexIconSize.SMALL,
    aspectRatio="1:1",
    scaling=True
)
```

**Properties**:
- `url` (required): Icon image URL
- `margin`: Space before component
- `position`, etc.: Positioning
- `size`: Icon size (keywords or pixels)
- `aspectRatio`: Icon aspect ratio
- `scaling`: Scale with LINE app font size

### FlexButton

Interactive button component.

```python
from line_api.flex_messages import (
    FlexButton, FlexButtonStyle, FlexButtonHeight, FlexGravity, FlexUriAction
)

button = FlexButton.create(
    action=FlexUriAction(uri="https://example.com", label="Click Me"),
    flex=1,
    margin="md",
    position="relative",
    height=FlexButtonHeight.SMALL,
    style=FlexButtonStyle.PRIMARY,
    color="#ffffff",
    gravity=FlexGravity.CENTER,
    adjustMode="shrink-to-fit",
    scaling=True
)
```

**Properties**:
- `action` (required): Action when button is tapped
- `flex`: Flexibility in parent container
- `margin`: Space before component
- `position`, etc.: Positioning
- `height`: Button height (`sm`, `md`)
- `style`: Button style (`link`, `primary`, `secondary`)
- `color`: Button color (hex color)
- `gravity`: Vertical alignment
- `adjustMode`: Auto-shrink behavior
- `scaling`: Scale with LINE app font size

### FlexSeparator

Visual separator line.

```python
from line_api.flex_messages import FlexSeparator

separator = FlexSeparator.create(
    margin="lg",
    color="#cccccc"
)
```

**Properties**:
- `margin`: Space before component
- `color`: Separator color (hex color)

### FlexFiller (Deprecated)

Empty space component (deprecated - use component properties instead).

```python
from line_api.flex_messages import FlexFiller

filler = FlexFiller.create(
    flex=1
)
```

**Properties**:
- `flex`: Space allocation

## Background Components

### FlexLinearGradient

Linear gradient background for boxes.

```python
from line_api.flex_messages import FlexLinearGradient

gradient = FlexLinearGradient.create(
    angle="90deg",
    startColor="#ff0000",
    endColor="#0000ff",
    centerColor="#00ff00",
    centerPosition="50%"
)
```

**Properties**:
- `angle` (required): Gradient angle in degrees
- `startColor` (required): Starting color (hex)
- `endColor` (required): Ending color (hex)
- `centerColor`: Middle color for three-color gradient
- `centerPosition`: Position of middle color (percentage)

## Styling Components

### FlexBubbleStyle

Bubble-level styling options.

```python
from line_api.flex_messages import FlexBubbleStyle, FlexBlockStyle

style = FlexBubbleStyle.create(
    header=FlexBlockStyle.create(backgroundColor="#ff0000"),
    hero=FlexBlockStyle.create(separator=True, separatorColor="#cccccc"),
    body=FlexBlockStyle.create(backgroundColor="#f0f0f0"),
    footer=FlexBlockStyle.create(separator=True, backgroundColor="#e0e0e0")
)
```

### FlexBlockStyle

Block-level styling options.

```python
from line_api.flex_messages import FlexBlockStyle

block_style = FlexBlockStyle.create(
    backgroundColor="#f0f0f0",
    separator=True,
    separatorColor="#cccccc"
)
```

**Properties**:
- `backgroundColor`: Block background color
- `separator`: Enable separator line
- `separatorColor`: Separator line color

## Enums Reference

### Size Enums

```python
from line_api.flex_messages import (
    FlexBubbleSize, FlexTextSize, FlexImageSize, FlexIconSize,
    FlexButtonHeight, FlexSpacing
)

# Bubble sizes
FlexBubbleSize.NANO, .MICRO, .KILO, .MEGA, .GIGA

# Text sizes
FlexTextSize.XX_SMALL, .X_SMALL, .SMALL, .MEDIUM, .LARGE, .X_LARGE, .XX_LARGE, .XXX_LARGE, .XXXX_LARGE, .XXXXX_LARGE

# Image sizes
FlexImageSize.XX_SMALL, .X_SMALL, .SMALL, .MEDIUM, .LARGE, .X_LARGE, .XX_LARGE, .XXX_LARGE, .XXXX_LARGE, .XXXXX_LARGE, .FULL

# Icon sizes
FlexIconSize.XX_SMALL, .X_SMALL, .SMALL, .MEDIUM, .LARGE, .X_LARGE, .XX_LARGE, .XXX_LARGE, .XXXX_LARGE, .XXXXX_LARGE

# Spacing values
FlexSpacing.NONE, .X_SMALL, .SMALL, .MEDIUM, .LARGE, .X_LARGE, .XX_LARGE
```

### Layout Enums

```python
from line_api.flex_messages import (
    FlexLayout, FlexJustifyContent, FlexAlignItems, FlexAlignment,
    FlexGravity, FlexDirection
)

# Box layouts
FlexLayout.VERTICAL, .HORIZONTAL, .BASELINE

# Main axis distribution
FlexJustifyContent.FLEX_START, .CENTER, .FLEX_END, .SPACE_BETWEEN, .SPACE_AROUND, .SPACE_EVENLY

# Cross axis alignment
FlexAlignItems.FLEX_START, .CENTER, .FLEX_END

# Component alignment
FlexAlignment.START, .CENTER, .END

# Component gravity
FlexGravity.TOP, .CENTER, .BOTTOM

# Text direction
FlexDirection.LTR, .RTL
```

### Style Enums

```python
from line_api.flex_messages import (
    FlexWeight, FlexDecoration, FlexButtonStyle, FlexImageAspectMode
)

# Font weights
FlexWeight.REGULAR, .BOLD

# Text decorations
FlexDecoration.NONE, .UNDERLINE, .LINE_THROUGH

# Button styles
FlexButtonStyle.LINK, .PRIMARY, .SECONDARY

# Image aspect modes
FlexImageAspectMode.COVER, .FIT
```

## Factory Methods

All components use the `.create()` factory method:

```python
# Factory method pattern
component = ComponentClass.create(
    required_property="value",
    optional_property="value"
)

# Equivalent to
component = ComponentClass(
    required_property="value",
    optional_property="value"
)
```

This reference provides complete coverage of all FlexMessage components, their properties, and usage patterns for building rich interactive messages.
