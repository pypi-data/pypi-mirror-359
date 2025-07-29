"""
Flex message builders for common use cases.

This module provides builders for creating common types of Flex Messages
with a simple, fluent API.
"""

from typing import Optional, Union, cast

from .models import (
    FlexAlignment,
    FlexBox,
    FlexButton,
    FlexComponent,
    FlexFiller,
    FlexIcon,
    FlexImage,
    FlexLayout,
    FlexSeparator,
    FlexText,
    FlexTextWeight,
    FlexVideo,
)


class BaseFlexBuilder:
    """Base class for all flex message builders with common functionality."""

    # Common color scheme
    PRIMARY_COLOR = "#1E3A8A"
    SUCCESS_COLOR = "#00C851"
    WARNING_COLOR = "#FF9800"
    ERROR_COLOR = "#FF4444"
    TEXT_COLOR = "#555555"
    SUBTITLE_COLOR = "#666666"
    LIGHT_TEXT_COLOR = "#999999"

    # Common background colors
    LIGHT_BG = "#F8F9FA"
    PRIMARY_BG = "#F1F5F9"
    WARNING_BG = "#FFF3E0"

    @staticmethod
    def create_standard_header(
        title: str,
        subtitle: Optional[str] = None,
        icon: str = "",
        title_color: Optional[str] = None,
        bg_color: Optional[str] = None,
    ) -> FlexBox:
        """
        Create a standard header component for flex messages.

        Args:
            title: Main title text
            subtitle: Optional subtitle text
            icon: Emoji icon to show before title
            title_color: Color for the title text
            bg_color: Background color for header

        Returns:
            FlexBox: Header component

        """
        title_color = title_color or BaseFlexBuilder.PRIMARY_COLOR
        bg_color = bg_color or BaseFlexBuilder.PRIMARY_BG

        contents = [
            FlexText.create(
                text=f"{icon} {title}".strip(),
                weight=FlexTextWeight.BOLD,
                size="xl",
                color=title_color,
                align=FlexAlignment.CENTER,
            ),
        ]

        if subtitle:
            contents.append(
                FlexText.create(
                    text=subtitle,
                    size="md",
                    color=BaseFlexBuilder.SUBTITLE_COLOR,
                    align=FlexAlignment.CENTER,
                ),
            )

        return FlexBox.create(
            layout=FlexLayout.VERTICAL,
            contents=cast(
                "list[Union[FlexText, FlexButton, FlexImage, FlexIcon, FlexSeparator, FlexVideo, FlexFiller, FlexBox]]",
                contents,
            ),
            background_color=bg_color,
            padding_all="20px",
        )

    @staticmethod
    def create_info_row(
        label: str,
        value: str,
        label_color: Optional[str] = None,
        value_color: Optional[str] = None,
        value_weight: Optional[FlexTextWeight] = None,
    ) -> FlexBox:
        """
        Create a horizontal info row with label and value.

        Args:
            label: Label text
            value: Value text
            label_color: Color for label
            value_color: Color for value
            value_weight: Font weight for value

        Returns:
            FlexBox: Info row component

        """
        label_color = label_color or BaseFlexBuilder.SUBTITLE_COLOR
        value_color = value_color or BaseFlexBuilder.TEXT_COLOR

        # Convert string weight to enum if provided
        weight_enum = value_weight

        contents = [
            FlexText.create(
                text=label,
                size="sm",
                color=label_color,
                flex=2,
            ),
            FlexText.create(
                text=value,
                size="sm",
                color=value_color,
                weight=weight_enum,
                flex=1,
                align=FlexAlignment.END,
            ),
        ]

        return FlexBox.create(
            layout=FlexLayout.HORIZONTAL,
            contents=cast(
                "list[Union[FlexText, FlexButton, FlexImage, FlexIcon, FlexSeparator, FlexVideo, FlexFiller, FlexBox]]",
                contents,
            ),
        )

    @staticmethod
    def create_section_title(
        title: str,
        icon: str = "",
        color: Optional[str] = None,
    ) -> FlexText:
        """
        Create a section title text component.

        Args:
            title: Title text
            icon: Emoji icon
            color: Text color

        Returns:
            FlexText: Section title component

        """
        color = color or BaseFlexBuilder.PRIMARY_COLOR

        return FlexText.create(
            text=f"{icon} {title}".strip(),
            weight=FlexTextWeight.BOLD,
            size="lg",
            color=color,
        )

    @staticmethod
    def create_separator_with_margin(margin: str = "md") -> FlexSeparator:
        """Create a separator with margin."""
        return FlexSeparator.create(margin=margin)

    @staticmethod
    def create_separator(margin: str = "md", color: str = "#E0E0E0") -> FlexSeparator:
        """Create a separator with specified margin and color."""
        return FlexSeparator.create(margin=margin, color=color)


class FlexMessageBuilder:
    """Builder for creating common flex message patterns."""

    def __init__(self) -> None:
        """Initialize the builder."""
        self.base = BaseFlexBuilder()

    def create_simple_text_bubble(
        self,
        title: str,
        message: str,
    ) -> FlexBox:
        """
        Create a simple text bubble with title and message.

        Args:
            title: Main title
            message: Message text

        Returns:
            FlexBox: Complete bubble body

        """
        contents: list[FlexComponent] = [
            self.base.create_section_title(title),
            self.base.create_separator(margin="md"),
            FlexText.create(
                text=message,
                wrap=True,
                color=self.base.TEXT_COLOR,
            ),
        ]

        return FlexBox.create(
            layout=FlexLayout.VERTICAL,
            spacing="sm",
            contents=cast(
                "list[Union[FlexText, FlexButton, FlexImage, FlexIcon, FlexSeparator, FlexVideo, FlexFiller, FlexBox]]",
                contents,
            ),
            padding_all="20px",
        )
