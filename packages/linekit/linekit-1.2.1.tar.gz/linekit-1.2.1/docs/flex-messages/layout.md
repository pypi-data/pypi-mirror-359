# FlexMessage Layout and Positioning

Advanced layout features for building complex FlexMessage structures using CSS flexbox principles.

## Overview

FlexMessage layouts are based on the CSS Flexible Box (CSS flexbox) specification. The flex container corresponds to the [box component](./elements.md#flexbox) and flex items correspond to the child components.

## Box Component Orientation

Box components have three orientations that determine how child components are arranged:

| Layout | Value | Main Axis | Cross Axis | Child Arrangement |
|--------|-------|-----------|------------|------------------|
| Horizontal box | `horizontal` | Horizontal | Vertical | Horizontally |
| Vertical box | `vertical` | Vertical | Horizontal | Vertically |
| Baseline box | `baseline` | Horizontal | Vertical | Horizontally with baseline alignment |

### Baseline Boxes

Baseline boxes behave like horizontal boxes but with special alignment:

- **Baseline Alignment**: All child components align to the same baseline regardless of font size
- **Icon Baseline**: Icon components use the bottom of the icon image as their baseline
- **Property Restrictions**: Cannot use `gravity` and `offsetBottom` properties in child components

## Available Child Components

Different box layouts support different child components:

| Component | Baseline Box | Horizontal/Vertical Box |
|-----------|--------------|------------------------|
| Box | ❌ | ✅ |
| Button | ❌ | ✅ |
| Image | ❌ | ✅ |
| Video | ❌ | ✅ |
| Icon | ✅ | ❌ |
| Text | ✅ | ✅ |
| Span | ❌ | ❌ (Use as child of text) |
| Separator | ❌ | ✅ |
| Filler (deprecated) | ✅ | ✅ |

## Component Size

### Width Allocation in Horizontal Boxes

Child components with `flex` property ≥ 1 share the parent box's width proportionally:

```python
from line_api.flex_messages import FlexBox, FlexText, FlexLayout

# Two components with 2:3 width ratio
box = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    contents=[
        FlexText.create("Narrow", flex=2, color="#ff0000"),
        FlexText.create("Wide", flex=3, color="#0000ff")
    ]
)
```

**Flex Property Behavior**:

- `flex=0`: Component takes width needed for content
- `flex≥1`: Component shares remaining space proportionally
- Default: `flex=1` for horizontal boxes

### Height Allocation in Vertical Boxes

Child components with `flex` property ≥ 1 share the parent box's height:

```python
# Two components with 2:3 height ratio
vertical_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[
        FlexText.create("Short", flex=2),
        FlexText.create("Tall", flex=3)
    ]
)
```

**Default**: `flex=0` for vertical boxes

### Box Dimensions

**Width Properties**:
```python
from line_api.flex_messages import FlexBox

# Fixed width
box = FlexBox.create(width="200px", contents=[])

# Percentage width
box = FlexBox.create(width="50%", contents=[])

# Maximum width
box = FlexBox.create(maxWidth="300px", contents=[])
```

**Height Properties**:
```python
# Fixed height
box = FlexBox.create(height="100px", contents=[])

# Maximum height
box = FlexBox.create(maxHeight="200px", contents=[])
```

### Image Sizing

Images support various size specifications:

```python
from line_api.flex_messages import FlexImage, FlexImageSize

# Keyword sizes
image = FlexImage.create(url="https://example.com/image.jpg", size=FlexImageSize.LARGE)

# Percentage sizes
image = FlexImage.create(url="https://example.com/image.jpg", size="50%")

# Pixel sizes
image = FlexImage.create(url="https://example.com/image.jpg", size="200px")
```

**Available Keywords** (in order): `xxs`, `xs`, `sm`, `md` (default), `lg`, `xl`, `xxl`, `3xl`, `4xl`, `5xl`, `full`

### Text, Icon, and Span Sizing

```python
from line_api.flex_messages import FlexText, FlexIcon, FlexTextSize

# Keyword sizes
text = FlexText.create("Hello", size=FlexTextSize.EXTRA_LARGE)

# Pixel sizes
text = FlexText.create("Hello", size="24px")

# Icon sizing
icon = FlexIcon.create(url="https://example.com/icon.png", size="lg")
```

### Automatic Font Scaling

**Shrink to Fit**:
```python
text = FlexText.create(
    "Long text that needs to fit",
    adjustMode="shrink-to-fit"
)
```

**Accessibility Scaling**:
```python
text = FlexText.create(
    "Accessible text",
    size="20px",
    scaling=True  # Scales with LINE app font size setting
)
```

## Component Position

### Horizontal Alignment

Use the `align` property for text and image components:

```python
from line_api.flex_messages import FlexText, FlexAlignment

# Left alignment
text = FlexText.create("Left", align=FlexAlignment.START)

# Center alignment (default)
text = FlexText.create("Center", align=FlexAlignment.CENTER)

# Right alignment
text = FlexText.create("Right", align=FlexAlignment.END)
```

### Vertical Alignment

Use the `gravity` property for text, image, and button components:

```python
from line_api.flex_messages import FlexText, FlexGravity

# Top alignment (default)
text = FlexText.create("Top", gravity=FlexGravity.TOP)

# Center alignment
text = FlexText.create("Middle", gravity=FlexGravity.CENTER)

# Bottom alignment
text = FlexText.create("Bottom", gravity=FlexGravity.BOTTOM)
```

**Note**: `gravity` is ignored in baseline boxes.

### Box Padding

Position child components using box padding:

```python
from line_api.flex_messages import FlexBox

# All-around padding
box = FlexBox.create(
    contents=[],
    paddingAll="md",
    backgroundColor="#f0f0f0"
)

# Specific padding (takes precedence over paddingAll)
box = FlexBox.create(
    contents=[],
    paddingTop="lg",
    paddingStart="sm",
    paddingEnd="sm",
    paddingBottom="xs"
)
```

**Padding Values**: `none`, `xs`, `sm`, `md` (default), `lg`, `xl`, `xxl`, pixels (`"20px"`), percentage (`"10%"`)

### Free Space Distribution

#### Main Axis Distribution (justifyContent)

Distribute child components along the main axis when all children have `flex=0`:

```python
from line_api.flex_messages import FlexBox, FlexJustifyContent

box = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    justifyContent=FlexJustifyContent.SPACE_BETWEEN,
    contents=[
        # All children must have flex=0
        FlexText.create("Start", flex=0),
        FlexText.create("End", flex=0)
    ]
)
```

**JustifyContent Options**:
- `FLEX_START`: Group at text beginning/top
- `CENTER`: Group at center
- `FLEX_END`: Group at text end/bottom
- `SPACE_BETWEEN`: Even distribution with children at edges
- `SPACE_AROUND`: Even distribution with equal space around each child
- `SPACE_EVENLY`: Even distribution with equal space between all elements

#### Cross Axis Distribution (alignItems)

Distribute child components along the cross axis:

```python
from line_api.flex_messages import FlexBox, FlexAlignItems

box = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    alignItems=FlexAlignItems.FLEX_START,
    height="200px",
    contents=[
        FlexBox.create(height="100px", backgroundColor="#00aaff", flex=0),
        FlexBox.create(height="50px", backgroundColor="#00aaff", flex=0)
    ]
)
```

**AlignItems Options**:
- `FLEX_START`: Align at top/text beginning
- `CENTER`: Align at middle
- `FLEX_END`: Align at bottom/text end

### Spacing and Margins

**Box Spacing** (between child components):
```python
from line_api.flex_messages import FlexBox

box = FlexBox.create(
    spacing="lg",  # Space between all children
    contents=[
        FlexText.create("Item 1"),
        FlexText.create("Item 2"),
        FlexText.create("Item 3")
    ]
)
```

**Component Margins** (overrides parent spacing):
```python
box = FlexBox.create(
    spacing="md",
    contents=[
        FlexText.create("Normal spacing"),
        FlexText.create("Large margin", margin="xxl"),  # Overrides spacing
        FlexText.create("Normal spacing")
    ]
)
```

**Spacing Values**: `none`, `xs`, `sm`, `md`, `lg`, `xl`, `xxl`, pixels (`"15px"`)

### Offset Positioning

#### Relative Positioning

Shift components from their original position:

```python
from line_api.flex_messages import FlexBox

box = FlexBox.create(
    contents=[FlexText.create("Shifted text")],
    position="relative",
    offsetTop="10px",     # Shift down
    offsetStart="20px"    # Shift away from text start
)
```

**Relative Offset Properties**:
- `offsetTop`: Shift down from top edge
- `offsetBottom`: Shift up from bottom edge
- `offsetStart`: Shift away from text start (right in LTR)
- `offsetEnd`: Shift away from text end (left in LTR)

#### Absolute Positioning

Position components relative to parent edges:

```python
box = FlexBox.create(
    contents=[FlexText.create("Absolutely positioned")],
    position="absolute",
    offsetTop="10px",
    offsetBottom="20px",
    offsetStart="30px",
    offsetEnd="40px"
)
```

**Absolute Positioning Notes**:
- Component doesn't affect parent size
- Parent doesn't affect component size
- Content outside parent bounds is clipped
- Always specify both vertical and horizontal offsets

## Linear Gradient Backgrounds

Create gradient backgrounds for box components:

```python
from line_api.flex_messages import FlexBox, FlexLinearGradient

# Basic gradient
gradient = FlexLinearGradient.create(
    angle="90deg",        # Left to right
    startColor="#ff0000", # Red
    endColor="#0000ff"    # Blue
)

box = FlexBox.create(
    contents=[],
    background=gradient,
    height="200px"
)
```

### Gradient Angles

- `0deg`: Bottom to top
- `45deg`: Bottom-left to top-right
- `90deg`: Left to right
- `180deg`: Top to bottom
- Direction rotates clockwise as angle increases

### Color Stops

Add intermediate colors to gradients:

```python
# Three-color gradient
gradient = FlexLinearGradient.create(
    angle="0deg",
    startColor="#ff0000",    # Red at start
    centerColor="#00ff00",   # Green at center
    endColor="#0000ff",      # Blue at end
    centerPosition="25%"     # Green appears at 25% mark
)
```

## Rendering Order

Components are rendered in JSON definition order:
- First component renders at bottom layer
- Last component renders at top layer
- Later components appear on top of earlier ones

To change layering, reorder components in the contents array.

## Text Direction Support

FlexMessages support both LTR (Left-to-Right) and RTL (Right-to-Left) text directions:

```python
from line_api.flex_messages import FlexBubble, FlexDirection

bubble = FlexBubble.create(
    direction=FlexDirection.RTL,  # Right-to-left layout
    body=FlexBox.create(contents=[...])
)
```

**Direction Effects**:
- `offsetStart`/`offsetEnd` meanings flip
- `justifyContent` `flex-start`/`flex-end` behavior changes
- Gradient directions remain unchanged

## Best Practices

### Layout Design
- Use horizontal boxes for side-by-side content
- Use vertical boxes for stacked content
- Use baseline boxes for icon-text combinations
- Plan your component hierarchy before implementation

### Responsive Design
- Use `flex` properties instead of fixed pixel widths
- Test layouts on different screen sizes
- Use percentage values for adaptable sizing
- Consider using `maxWidth`/`maxHeight` for constraints

### Performance
- Minimize deeply nested structures
- Use appropriate component types for content
- Avoid unnecessary wrapper boxes
- Test complex layouts thoroughly

### Accessibility
- Use `scaling=True` for text components when appropriate
- Ensure adequate color contrast in gradients
- Provide meaningful `altText` for images
- Test with different font size settings

## Common Layout Patterns

### Card Layout
```python
card = FlexBubble.create(
    body=FlexBox.create(
        layout=FlexLayout.VERTICAL,
        paddingAll="lg",
        contents=[
            FlexText.create("Title", weight=FlexWeight.BOLD, size=FlexTextSize.LARGE),
            FlexText.create("Subtitle", color="#666666", margin="sm"),
            FlexSeparator.create(margin="md"),
            FlexText.create("Content goes here...", wrap=True, margin="md")
        ]
    )
)
```

### Icon-Text Row
```python
row = FlexBox.create(
    layout=FlexLayout.BASELINE,
    spacing="sm",
    contents=[
        FlexIcon.create(url="https://example.com/icon.png", size="sm"),
        FlexText.create("Text with icon", flex=1)
    ]
)
```

### Button Grid
```python
grid = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="sm",
    contents=[
        FlexBox.create(
            layout=FlexLayout.HORIZONTAL,
            spacing="sm",
            contents=[
                FlexButton.create(action=uri_action1, flex=1),
                FlexButton.create(action=uri_action2, flex=1)
            ]
        ),
        FlexBox.create(
            layout=FlexLayout.HORIZONTAL,
            spacing="sm",
            contents=[
                FlexButton.create(action=uri_action3, flex=1),
                FlexButton.create(action=uri_action4, flex=1)
            ]
        )
    ]
)
```

This layout documentation provides comprehensive coverage of FlexMessage positioning, sizing, and layout capabilities based on the official LINE documentation.
