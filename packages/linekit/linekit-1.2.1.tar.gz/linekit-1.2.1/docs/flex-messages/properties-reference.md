# FlexMessage Properties Reference

Comprehensive reference for all FlexMessage properties, their values, and usage guidelines.

## Size Properties

### Text Sizes

Used for `FlexText`, `FlexSpan`, and `FlexIcon` components.

| Keyword | Pixel Equivalent | Use Case |
|---------|------------------|-----------|
| `xxs` | ~8px | Very small labels |
| `xs` | ~10px | Small labels, captions |
| `sm` | ~12px | Secondary text |
| `md` | ~14px | Default text size |
| `lg` | ~16px | Emphasized text |
| `xl` | ~18px | Subheadings |
| `xxl` | ~20px | Headings |
| `3xl` | ~24px | Large headings |
| `4xl` | ~28px | Display text |
| `5xl` | ~32px | Hero text |

**Custom Sizes**: You can also specify exact pixel values:

```python
text = FlexText.create("Custom size", size="22px")
```

### Image Sizes

Used for `FlexImage` components.

| Keyword | Description | Responsive |
|---------|-------------|------------|
| `xxs` | Very small image | ✅ |
| `xs` | Small image | ✅ |
| `sm` | Small-medium image | ✅ |
| `md` | Default medium image | ✅ |
| `lg` | Large image | ✅ |
| `xl` | Extra large image | ✅ |
| `xxl` | Very large image | ✅ |
| `3xl` | Huge image | ✅ |
| `4xl` | Maximum image | ✅ |
| `5xl` | Largest image | ✅ |
| `full` | Full container width | ✅ |

**Percentage Sizes**: Relative to original image size:

```python
image = FlexImage.create(url="...", size="75%")  # 75% of original
```

**Pixel Sizes**: Fixed dimensions:

```python
image = FlexImage.create(url="...", size="200px")  # Fixed 200px width
```

### Button Heights

Used for `FlexButton` components.

| Value | Description | Height |
|-------|-------------|--------|
| `sm` | Small button | ~32px |
| `md` | Medium button (default) | ~40px |

### Bubble Sizes

Used for `FlexBubble` components.

| Size | Use Case | Video Support |
|------|----------|---------------|
| `nano` | Minimal content | ❌ |
| `micro` | Small content | ❌ |
| `kilo` | Standard content | ✅ |
| `mega` | Rich content | ✅ |
| `giga` | Maximum content | ✅ |

## Spacing Properties

### Spacing Values

Used for `spacing`, `margin`, and `padding` properties.

| Keyword | Pixel Equivalent | Use Case |
|---------|------------------|-----------|
| `none` | 0px | No spacing |
| `xs` | ~4px | Minimal spacing |
| `sm` | ~8px | Small spacing |
| `md` | ~16px | Default spacing |
| `lg` | ~24px | Large spacing |
| `xl` | ~32px | Extra large spacing |
| `xxl` | ~40px | Maximum spacing |

**Custom Spacing**: Pixel and percentage values:

```python
box = FlexBox.create(
    spacing="12px",      # Custom pixel spacing
    paddingAll="5%",     # Percentage padding
    margin="20px"        # Custom margin
)
```

### Spacing Guidelines

**Between Components**:
- `xs` (4px): Tight layouts, related items
- `sm` (8px): Close relationships
- `md` (16px): Standard spacing
- `lg` (24px): Clear separation
- `xl` (32px): Strong separation
- `xxl` (40px): Maximum separation

**Padding Recommendations**:
- `sm`: Dense content
- `md`: Standard content
- `lg`: Comfortable content
- `xl`: Spacious layouts

## Color Properties

### Color Formats

All color properties accept hex color values:

```python
# Standard hex colors
text = FlexText.create("Red text", color="#ff0000")
text = FlexText.create("Blue text", color="#0066cc")

# Short hex format
text = FlexText.create("Green text", color="#0f0")

# Named colors (use hex equivalents)
black = "#000000"
white = "#ffffff"
gray = "#808080"
```

### Color Usage

**Text Colors**:
- `#000000`: Primary text
- `#333333`: Dark text
- `#666666`: Secondary text
- `#999999`: Muted text
- `#cccccc`: Disabled text

**Background Colors**:
- `#ffffff`: White background
- `#f8f9fa`: Light gray background
- `#e9ecef`: Medium gray background
- `#dee2e6`: Darker gray background

**Accent Colors**:
- `#007bff`: Primary blue
- `#28a745`: Success green
- `#dc3545`: Error red
- `#ffc107`: Warning yellow

## Layout Properties

### Box Layouts

| Layout | Description | Child Components | Use Case |
|--------|-------------|------------------|-----------|
| `vertical` | Vertical stacking | All except Icon | Standard layouts |
| `horizontal` | Side-by-side | All except Icon | Rows, toolbars |
| `baseline` | Baseline-aligned | Text, Icon, Span | Icon-text pairs |

### Flex Values

Controls how components share available space:

| Value | Behavior | Use Case |
|-------|----------|-----------|
| `0` | Fixed size | Buttons, icons, labels |
| `1` | Equal sharing | Balanced layouts |
| `2` | Double share | Emphasized content |
| `3+` | Triple+ share | Primary content |

**Flex Examples**:

```python
# Equal width columns
FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    contents=[
        FlexText.create("Left", flex=1),
        FlexText.create("Right", flex=1)
    ]
)

# 2:1 ratio
FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    contents=[
        FlexText.create("Main", flex=2),
        FlexText.create("Side", flex=1)
    ]
)
```

### Alignment Properties

**Horizontal Alignment** (`align`):
- `start`: Left in LTR, right in RTL
- `center`: Center alignment
- `end`: Right in LTR, left in RTL

**Vertical Alignment** (`gravity`):
- `top`: Top alignment
- `center`: Center alignment
- `bottom`: Bottom alignment

**Content Distribution** (`justifyContent`):
- `flex-start`: Pack to start
- `center`: Pack to center
- `flex-end`: Pack to end
- `space-between`: Space between items
- `space-around`: Space around items
- `space-evenly`: Even spacing

**Cross-Axis Alignment** (`alignItems`):
- `flex-start`: Align to start
- `center`: Align to center
- `flex-end`: Align to end

## Position Properties

### Position Types

| Position | Description | Offset Behavior |
|----------|-------------|-----------------|
| `relative` | Normal flow | Relative to original position |
| `absolute` | Out of flow | Relative to parent edges |

### Offset Properties

**Relative Positioning**:
- `offsetTop`: Move down from original position
- `offsetBottom`: Move up from original position
- `offsetStart`: Move away from text start
- `offsetEnd`: Move away from text end

**Absolute Positioning**:
- `offsetTop`: Distance from parent top
- `offsetBottom`: Distance from parent bottom
- `offsetStart`: Distance from parent start edge
- `offsetEnd`: Distance from parent end edge

**Offset Values**:
- Pixels: `"10px"`, `"25px"`
- Keywords: `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, `"xxl"`
- Percentage: `"10%"`, `"25%"` (for horizontal offsets)

## Dimension Properties

### Width and Height

**Fixed Dimensions**:

```python
box = FlexBox.create(
    width="200px",
    height="100px"
)
```

**Percentage Dimensions**:

```python
box = FlexBox.create(
    width="50%",    # 50% of parent width
    height="75%"    # 75% of parent height
)
```

**Maximum Dimensions**:

```python
box = FlexBox.create(
    maxWidth="400px",   # Won't exceed 400px
    maxHeight="200px"   # Won't exceed 200px
)
```

### Aspect Ratios

Used for images and videos:

| Ratio | Description | Use Case |
|-------|-------------|-----------|
| `"1:1"` | Square | Avatars, icons |
| `"4:3"` | Traditional | Classic photos |
| `"16:9"` | Widescreen | Modern videos |
| `"21:9"` | Ultrawide | Cinematic |
| `"9:16"` | Vertical | Mobile stories |
| `"3:4"` | Portrait | Portrait photos |

## Style Properties

### Font Weights

| Weight | Description | Use Case |
|--------|-------------|-----------|
| `regular` | Normal text | Body text |
| `bold` | Bold text | Headings, emphasis |

### Text Decorations

| Decoration | Description | Use Case |
|------------|-------------|-----------|
| `none` | No decoration | Normal text |
| `underline` | Underlined text | Links, emphasis |
| `line-through` | Strikethrough text | Deleted content |

### Button Styles

| Style | Appearance | Use Case |
|-------|------------|-----------|
| `link` | Text-like button | Secondary actions |
| `primary` | Filled button | Primary actions |
| `secondary` | Outlined button | Secondary actions |

### Image Aspect Modes

| Mode | Behavior | Use Case |
|------|----------|-----------|
| `cover` | Fill container, crop if needed | Backgrounds |
| `fit` | Fit inside container | Full image display |

## Border Properties

### Border Widths

Pixel values for border thickness:

```python
box = FlexBox.create(borderWidth="1px")  # Thin border
box = FlexBox.create(borderWidth="2px")  # Medium border
box = FlexBox.create(borderWidth="4px")  # Thick border
```

### Corner Radius

Rounded corner values:

```python
box = FlexBox.create(cornerRadius="4px")   # Slightly rounded
box = FlexBox.create(cornerRadius="8px")   # Moderately rounded
box = FlexBox.create(cornerRadius="16px")  # Very rounded
box = FlexBox.create(cornerRadius="50%")   # Circular
```

## Gradient Properties

### Linear Gradient

**Angles**:
- `"0deg"`: Bottom to top
- `"45deg"`: Bottom-left to top-right
- `"90deg"`: Left to right
- `"135deg"`: Top-left to bottom-right
- `"180deg"`: Top to bottom
- `"270deg"`: Right to left

**Colors**:
- `startColor`: Gradient start color (hex)
- `endColor`: Gradient end color (hex)
- `centerColor`: Middle color for 3-color gradient
- `centerPosition`: Position of center color (`"10%"` to `"90%"`)

## Action Properties

### URI Actions

For buttons, images, and videos:

```python
from line_api.flex_messages import FlexUriAction

action = FlexUriAction(
    uri="https://example.com",
    label="Visit Website"
)
```

**URI Formats**:
- `https://...`: Web URLs
- `http://...`: Non-secure web URLs
- `tel:+1234567890`: Phone numbers
- `mailto:user@example.com`: Email addresses

## Text Direction

### Direction Values

| Direction | Description | Use Case |
|-----------|-------------|-----------|
| `ltr` | Left-to-right | English, European languages |
| `rtl` | Right-to-left | Arabic, Hebrew |

**Direction Effects**:
- Changes meaning of `start`/`end` alignment
- Affects `offsetStart`/`offsetEnd` behavior
- Influences `justifyContent` positioning

## Advanced Properties

### Adjust Mode

Auto-resize behavior for text and buttons:

```python
text = FlexText.create(
    "Long text that might overflow",
    adjustMode="shrink-to-fit"
)
```

### Scaling

Font size scaling with LINE app settings:

```python
text = FlexText.create(
    "Accessible text",
    scaling=True  # Scales with user's font size preference
)
```

### Line Spacing

Control line spacing for wrapped text:

```python
text = FlexText.create(
    "Multi-line\nwrapped text",
    wrap=True,
    lineSpacing="20px"  # 20px between lines
)
```

## Property Validation

### Required Properties

Components have different required properties:

- **FlexMessage**: `altText`, `contents`
- **FlexBubble**: None (all optional)
- **FlexBox**: `layout`, `contents`
- **FlexText**: `text`
- **FlexImage**: `url`
- **FlexVideo**: `url`, `previewUrl`, `altContent`, `aspectRatio`
- **FlexButton**: `action`

### Property Constraints

**Text Length**:
- FlexText: Up to 2,000 characters
- FlexSpan: Up to 1,000 characters
- Button labels: Up to 300 characters

**Array Limits**:
- FlexCarousel: Up to 12 bubbles
- FlexBox contents: Up to 10 components
- FlexText contents: Up to 20 spans

**URL Requirements**:
- Must use HTTPS for images and videos
- Maximum URL length: 2,000 characters

This comprehensive properties reference provides detailed information about all available FlexMessage properties, their values, and proper usage guidelines.
