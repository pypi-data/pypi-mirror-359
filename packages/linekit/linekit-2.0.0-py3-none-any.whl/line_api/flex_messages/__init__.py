"""
LINE Flex Messages module.

This module provides type-safe Pydantic models for creating LINE Flex Messages
and utilities for testing and validation.

Updated with comprehensive components and properties from the latest LINE API docs.
"""

from .models import (  # Enums for type safety; Components; Actions
    FlexAdjustMode,
    FlexAlignItems,
    FlexAlignment,
    FlexBox,
    FlexBubble,
    FlexBubbleSize,
    FlexButton,
    FlexButtonHeight,
    FlexButtonStyle,
    FlexCarousel,
    FlexComponent,
    FlexDirection,
    FlexFiller,
    FlexGravity,
    FlexIcon,
    FlexImage,
    FlexImageAspectMode,
    FlexJustifyContent,
    FlexLayout,
    FlexLinearGradient,
    FlexMessage,
    FlexMessageAction,
    FlexMessageType,
    FlexPosition,
    FlexPostbackAction,
    FlexSeparator,
    FlexSize,
    FlexSpacing,
    FlexSpan,
    FlexText,
    FlexTextDecoration,
    FlexTextWeight,
    FlexUriAction,
    FlexVideo,
)
from .utils import (
    FlexMessageJsonPrinter,
    export_flex_json,
    print_flex_json,
    validate_flex_json,
)

# Aliases for better ergonomics and backward compatibility
URIAction = FlexUriAction
PostbackAction = FlexPostbackAction
MessageAction = FlexMessageAction

__all__ = [
    "FlexAdjustMode",
    "FlexAlignItems",
    "FlexAlignment",
    "FlexBox",
    "FlexBubble",
    "FlexBubbleSize",
    "FlexButton",
    "FlexButtonHeight",
    "FlexButtonStyle",
    "FlexCarousel",
    "FlexComponent",
    "FlexDirection",
    "FlexFiller",
    "FlexGravity",
    "FlexIcon",
    "FlexImage",
    "FlexImageAspectMode",
    "FlexJustifyContent",
    "FlexLayout",
    "FlexLinearGradient",
    "FlexMessage",
    "FlexMessageAction",
    "FlexMessageJsonPrinter",
    "FlexMessageType",
    "FlexPosition",
    "FlexPostbackAction",
    "FlexSeparator",
    "FlexSize",
    "FlexSpacing",
    "FlexSpan",
    "FlexText",
    "FlexTextDecoration",
    "FlexTextWeight",
    "FlexUriAction",
    "FlexVideo",
    "MessageAction",
    "PostbackAction",
    "URIAction",
    "export_flex_json",
    "print_flex_json",
    "validate_flex_json",
]
