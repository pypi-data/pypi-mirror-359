# FlexMessage Migration Guide

Complete guide for migrating between FlexMessage versions and updating your FlexMessage implementations.

## Overview

This guide covers migration scenarios including:
- Updating from older FlexMessage implementations
- Migrating from deprecated components
- Adopting new features and best practices
- Breaking changes and compatibility notes

## Migration Scenarios

### From Basic LINE SDK to line-api Library

#### Before: Basic LINE SDK

```python
# Old approach with basic LINE SDK
from linebot.models import FlexSendMessage

# Manual JSON construction
flex_message = FlexSendMessage(
    alt_text="Product Card",
    contents={
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "Product Name",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": "$29.99",
                    "color": "#ff6b6b"
                }
            ]
        }
    }
)
```

#### After: line-api Library

```python
# New approach with type-safe components
from line_api.flex_messages import (
    FlexMessage, FlexBubble, FlexBox, FlexText,
    FlexLayout, FlexWeight, FlexTextSize
)

flex_message = FlexMessage.create(
    altText="Product Card",
    contents=FlexBubble.create(
        body=FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=[
                FlexText.create(
                    "Product Name",
                    weight=FlexWeight.BOLD,
                    size=FlexTextSize.LARGE
                ),
                FlexText.create(
                    "$29.99",
                    color="#ff6b6b"
                )
            ]
        )
    )
)
```

**Migration Benefits**:
- Type safety with Pydantic validation
- IDE autocomplete and error checking
- Better maintainability and refactoring
- Factory methods for easier component creation

### Deprecated Component Migration

#### FlexSpacer → Component Properties

**Before (Deprecated)**:
```python
# ❌ Old: Using FlexSpacer (deprecated)
box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[
        FlexText.create("First item"),
        FlexSpacer.create(size="md"),  # Deprecated
        FlexText.create("Second item")
    ]
)
```

**After (Recommended)**:
```python
# ✅ New: Using margin properties
box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[
        FlexText.create("First item"),
        FlexText.create("Second item", margin="md")  # Use margin instead
    ]
)

# Or use box spacing
box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="md",  # Automatic spacing between all children
    contents=[
        FlexText.create("First item"),
        FlexText.create("Second item")
    ]
)
```

#### FlexFiller → Modern Layout Properties

**Before (Deprecated)**:
```python
# ❌ Old: Using FlexFiller
box = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    contents=[
        FlexText.create("Left"),
        FlexFiller.create(),  # Deprecated filler
        FlexText.create("Right")
    ]
)
```

**After (Recommended)**:
```python
# ✅ New: Using justifyContent
box = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    justifyContent=FlexJustifyContent.SPACE_BETWEEN,
    contents=[
        FlexText.create("Left", flex=0),   # Fixed size
        FlexText.create("Right", flex=0)  # Fixed size
    ]
)

# Or using flex properties
box = FlexBox.create(
    layout=FlexLayout.HORIZONTAL,
    contents=[
        FlexText.create("Left"),
        FlexText.create("Right", margin="auto")  # Pushes to right
    ]
)
```

### String Values to Enum Migration

#### Before: String Literals

```python
# ❌ Old: String literals (error-prone)
text = FlexText.create(
    text="Hello",
    size="lg",           # String literal
    weight="bold",       # String literal
    align="center"       # String literal
)

box = FlexBox.create(
    layout="vertical",   # String literal
    contents=[text]
)
```

#### After: Type-Safe Enums

```python
# ✅ New: Type-safe enums with autocomplete
from line_api.flex_messages import (
    FlexText, FlexTextSize, FlexWeight, FlexAlignment,
    FlexBox, FlexLayout
)

text = FlexText.create(
    text="Hello",
    size=FlexTextSize.LARGE,        # Type-safe enum
    weight=FlexWeight.BOLD,         # Type-safe enum
    align=FlexAlignment.CENTER      # Type-safe enum
)

box = FlexBox.create(
    layout=FlexLayout.VERTICAL,     # Type-safe enum
    contents=[text]
)
```

**Migration Strategy**:
1. Replace string literals with enum imports
2. Use IDE autocomplete to find correct enum values
3. Run type checker to catch any remaining string literals
4. Update tests to use enums

### Property Name Updates

#### Size Property Changes

**Before**:
```python
# Some older implementations used different property names
component = SomeComponent(
    textSize="lg",      # Old property name
    imageSize="full"    # Old property name
)
```

**After**:
```python
# ✅ Standardized to 'size' property
text = FlexText.create(
    text="Content",
    size=FlexTextSize.LARGE    # Standardized property
)

image = FlexImage.create(
    url="https://example.com/image.jpg",
    size=FlexImageSize.FULL    # Standardized property
)
```

#### Alignment Property Consolidation

**Before**:
```python
# Old: Multiple alignment properties
text = FlexText.create(
    text="Content",
    horizontalAlign="center",  # Old property
    verticalAlign="middle"     # Old property
)
```

**After**:
```python
# ✅ New: Consolidated alignment properties
text = FlexText.create(
    text="Content",
    align=FlexAlignment.CENTER,   # Horizontal alignment
    gravity=FlexGravity.CENTER    # Vertical alignment
)
```

## Breaking Changes

### Version 2.0 Breaking Changes

#### Required Properties
- `FlexMessage.altText` is now required (was optional)
- `FlexVideo.altContent` is now required for video components
- `FlexBox.contents` cannot be empty (must have at least one component)

#### Property Type Changes
- All size properties now accept enums or strings (was strings only)
- Color properties now require hex format (no named colors)
- URL properties now require HTTPS (HTTP no longer supported)

#### Component Hierarchy Changes
- `FlexSpacer` and `FlexFiller` are deprecated
- `FlexIcon` can only be used in baseline layouts
- Video components require specific bubble sizes

### Validation Changes

#### Stricter Validation

**Before**:
```python
# Old: Lenient validation
text = FlexText.create(
    text="",           # Empty text was allowed
    color="red",       # Named colors were allowed
    size="invalid"     # Invalid sizes were silently ignored
)
```

**After**:
```python
# ✅ New: Strict validation with helpful errors
try:
    text = FlexText.create(
        text="Hello World",      # Non-empty text required
        color="#ff0000",         # Hex colors required
        size=FlexTextSize.LARGE  # Valid size enum required
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Handle validation errors appropriately
```

## Migration Strategies

### Gradual Migration

#### Step 1: Update Imports

```python
# Before
from linebot.models import FlexSendMessage

# After
from line_api.flex_messages import FlexMessage, FlexBubble, FlexBox, FlexText
from line_api.messaging import LineMessagingClient
```

#### Step 2: Convert JSON to Components

```python
# Migration helper function
def migrate_json_to_components(json_data: dict) -> FlexMessage:
    """Convert JSON FlexMessage to type-safe components."""

    if json_data.get("type") == "flex":
        return FlexMessage.create(
            altText=json_data.get("altText", "FlexMessage"),
            contents=migrate_bubble_json(json_data["contents"])
        )

    raise ValueError("Not a valid FlexMessage JSON")

def migrate_bubble_json(bubble_data: dict) -> FlexBubble:
    """Convert bubble JSON to FlexBubble component."""

    bubble_kwargs = {}

    if "size" in bubble_data:
        bubble_kwargs["size"] = FlexBubbleSize(bubble_data["size"])

    if "body" in bubble_data:
        bubble_kwargs["body"] = migrate_box_json(bubble_data["body"])

    # Add other blocks (header, hero, footer) as needed

    return FlexBubble.create(**bubble_kwargs)

def migrate_box_json(box_data: dict) -> FlexBox:
    """Convert box JSON to FlexBox component."""

    contents = []
    for item in box_data.get("contents", []):
        if item["type"] == "text":
            contents.append(migrate_text_json(item))
        elif item["type"] == "box":
            contents.append(migrate_box_json(item))
        # Add other component types as needed

    return FlexBox.create(
        layout=FlexLayout(box_data["layout"]),
        contents=contents,
        spacing=box_data.get("spacing"),
        margin=box_data.get("margin")
    )

def migrate_text_json(text_data: dict) -> FlexText:
    """Convert text JSON to FlexText component."""

    return FlexText.create(
        text=text_data["text"],
        size=text_data.get("size"),
        weight=text_data.get("weight"),
        color=text_data.get("color"),
        align=text_data.get("align")
    )
```

#### Step 3: Replace Factory Calls

```python
# Before: Manual component creation
def create_old_card():
    return FlexSendMessage(
        alt_text="Card",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "Title", "weight": "bold"}
                ]
            }
        }
    )

# After: Type-safe factory methods
def create_new_card():
    return FlexMessage.create(
        altText="Card",
        contents=FlexBubble.create(
            body=FlexBox.create(
                layout=FlexLayout.VERTICAL,
                contents=[
                    FlexText.create("Title", weight=FlexWeight.BOLD)
                ]
            )
        )
    )
```

### Automated Migration Tools

#### Migration Script Template

```python
#!/usr/bin/env python3
"""
FlexMessage migration script.
Converts JSON-based FlexMessages to type-safe components.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

def migrate_file(input_file: Path, output_file: Path):
    """Migrate a single file from JSON to type-safe components."""

    with open(input_file, 'r') as f:
        content = f.read()

    # Find FlexMessage JSON patterns
    flex_pattern = r'FlexSendMessage\(([^)]+)\)'
    matches = re.findall(flex_pattern, content)

    migrated_content = content

    for match in matches:
        # Parse and convert each FlexMessage
        old_code = f"FlexSendMessage({match})"
        new_code = convert_to_components(match)
        migrated_content = migrated_content.replace(old_code, new_code)

    with open(output_file, 'w') as f:
        f.write(migrated_content)

def convert_to_components(json_str: str) -> str:
    """Convert JSON string to component creation code."""
    # Implementation depends on specific JSON structure
    # This is a simplified example
    return "FlexMessage.create(altText='Migrated', contents=...)"

if __name__ == "__main__":
    input_dir = Path("src/old_flex_messages")
    output_dir = Path("src/new_flex_messages")

    for py_file in input_dir.glob("*.py"):
        output_file = output_dir / py_file.name
        migrate_file(py_file, output_file)
        print(f"Migrated {py_file} -> {output_file}")
```

## Testing Migration

### Compatibility Testing

```python
import pytest
from line_api.flex_messages import FlexMessage

def test_migration_compatibility():
    """Test that migrated components produce expected JSON."""

    # Original JSON structure
    expected_json = {
        "type": "flex",
        "altText": "Test message",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Hello",
                        "size": "lg",
                        "weight": "bold"
                    }
                ]
            }
        }
    }

    # New component-based creation
    message = FlexMessage.create(
        altText="Test message",
        contents=FlexBubble.create(
            body=FlexBox.create(
                layout=FlexLayout.VERTICAL,
                contents=[
                    FlexText.create(
                        "Hello",
                        size=FlexTextSize.LARGE,
                        weight=FlexWeight.BOLD
                    )
                ]
            )
        )
    )

    # Compare JSON output
    actual_json = message.model_dump(exclude_none=True)
    assert actual_json == expected_json

def test_deprecated_component_migration():
    """Test migration from deprecated components."""

    # Test that deprecated FlexSpacer usage is detected
    with pytest.warns(DeprecationWarning):
        # Code that uses deprecated components
        pass
```

### Visual Regression Testing

```python
def test_visual_regression():
    """Test that migrated components look the same."""

    # Export both old and new versions
    old_message = create_old_flex_message()
    new_message = create_migrated_flex_message()

    # Export to JSON for visual comparison
    export_flex_json(old_message, "test_old.json")
    export_flex_json(new_message, "test_new.json")

    # Manual verification in Flex Message Simulator
    # 1. Import both JSON files
    # 2. Compare visual output
    # 3. Ensure identical appearance
```

## Common Migration Issues

### Issue 1: Invalid Component Hierarchy

**Problem**:
```python
# ❌ Error: Icon in non-baseline layout
box = FlexBox.create(
    layout=FlexLayout.VERTICAL,  # Not baseline
    contents=[
        FlexIcon.create(url="https://example.com/icon.png")  # Error!
    ]
)
```

**Solution**:
```python
# ✅ Fix: Use baseline layout for icons
box = FlexBox.create(
    layout=FlexLayout.BASELINE,  # Baseline layout required
    contents=[
        FlexIcon.create(url="https://example.com/icon.png", size="sm"),
        FlexText.create("Text with icon", flex=1)
    ]
)
```

### Issue 2: Empty Component Contents

**Problem**:
```python
# ❌ Error: Empty contents array
box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[]  # Validation error: empty contents
)
```

**Solution**:
```python
# ✅ Fix: Add placeholder or conditional content
contents = get_dynamic_contents()

if contents:
    box = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=contents
    )
else:
    # Provide fallback content
    box = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexText.create("No content available", color="#999999")
        ]
    )
```

### Issue 3: Color Format Changes

**Problem**:
```python
# ❌ Error: Named colors not supported
text = FlexText.create(
    text="Red text",
    color="red"  # Error: must be hex format
)
```

**Solution**:
```python
# ✅ Fix: Use hex color values
text = FlexText.create(
    text="Red text",
    color="#ff0000"  # Hex format required
)

# Create color constants for consistency
COLORS = {
    'red': '#ff0000',
    'blue': '#0000ff',
    'green': '#008000'
}

text = FlexText.create(
    text="Red text",
    color=COLORS['red']
)
```

## Post-Migration Validation

### Checklist

- [ ] All FlexMessages use type-safe components
- [ ] No deprecated components (FlexSpacer, FlexFiller)
- [ ] All colors use hex format
- [ ] All URLs use HTTPS
- [ ] Component hierarchies are valid
- [ ] Required properties are provided
- [ ] Tests pass with new implementation
- [ ] Visual output matches original
- [ ] Performance is maintained or improved

### Validation Tools

```python
def validate_migration():
    """Validate that migration is complete and correct."""

    # Check for deprecated imports
    deprecated_imports = [
        "FlexSpacer",
        "FlexFiller"
    ]

    # Check for string literals that should be enums
    string_literals = [
        'layout="vertical"',
        'size="lg"',
        'weight="bold"'
    ]

    # Run validation checks
    check_deprecated_usage(deprecated_imports)
    check_string_literals(string_literals)
    check_component_hierarchy()
    check_required_properties()

def check_deprecated_usage(deprecated: list):
    """Check for usage of deprecated components."""
    # Implementation to scan codebase
    pass

def check_string_literals(literals: list):
    """Check for string literals that should be enums."""
    # Implementation to find string literals
    pass
```

This migration guide provides comprehensive coverage of upgrading FlexMessage implementations to use modern, type-safe components with proper validation and best practices.
