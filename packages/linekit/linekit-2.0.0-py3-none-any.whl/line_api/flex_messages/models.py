"""
LINE Flex Message models and schemas.

This module provides Pydantic models for creating type-safe Flex Messages
that can be used with the LINE Messaging API.

Updated with comprehensive properties based on the latest LINE API documentation.
"""

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class FlexSize(str, Enum):
    """Size keywords for text, icon, and image components."""

    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"
    THREE_XL = "3xl"
    FOUR_XL = "4xl"
    FIVE_XL = "5xl"
    FULL = "full"  # For images only


class FlexSpacing(str, Enum):
    """Spacing keywords for margins, padding, and spacing."""

    NONE = "none"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"


class FlexGravity(str, Enum):
    """Gravity options for vertical alignment."""

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class FlexJustifyContent(str, Enum):
    """Justify content options for main axis distribution."""

    FLEX_START = "flex-start"
    CENTER = "center"
    FLEX_END = "flex-end"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"


class FlexAlignItems(str, Enum):
    """Align items options for cross axis distribution."""

    FLEX_START = "flex-start"
    CENTER = "center"
    FLEX_END = "flex-end"


class FlexTextWeight(str, Enum):
    """Text weight options."""

    REGULAR = "regular"
    BOLD = "bold"


class FlexTextDecoration(str, Enum):
    """Text decoration options for span component."""

    NONE = "none"
    UNDERLINE = "underline"
    LINE_THROUGH = "line-through"


class FlexAdjustMode(str, Enum):
    """Adjust mode for font scaling."""

    SHRINK_TO_FIT = "shrink-to-fit"


class FlexImageAspectMode(str, Enum):
    """Image aspect mode options."""

    COVER = "cover"
    FIT = "fit"


class FlexBubbleSize(str, Enum):
    """Bubble size options."""

    NANO = "nano"
    MICRO = "micro"
    KILO = "kilo"
    MEGA = "mega"
    GIGA = "giga"


class FlexButtonHeight(str, Enum):
    """Button height options."""

    SM = "sm"
    MD = "md"


class FlexDirection(str, Enum):
    """Text direction options."""

    LTR = "ltr"
    RTL = "rtl"


class FlexMessageType(str, Enum):
    """Flex message types."""

    BUBBLE = "bubble"
    CAROUSEL = "carousel"


class FlexPosition(str, Enum):
    """Flex position options."""

    RELATIVE = "relative"
    ABSOLUTE = "absolute"


class FlexAlignment(str, Enum):
    """Flex alignment options."""

    START = "start"
    END = "end"
    CENTER = "center"


class FlexLayout(str, Enum):
    """Flex container layouts."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    BASELINE = "baseline"


class FlexButtonStyle(str, Enum):
    """Button styles."""

    LINK = "link"
    PRIMARY = "primary"
    SECONDARY = "secondary"


class FlexAction(BaseModel):
    """Base flex action."""

    type: str

    model_config = {"extra": "forbid"}


class FlexPostbackAction(FlexAction):
    """Postback action."""

    type: str = Field(default="postback", frozen=True)
    label: str  # Required for button actions
    data: str
    display_text: Optional[str] = Field(default=None, alias="displayText")

    @classmethod
    def create(
        cls,
        data: str,
        label: str,
        display_text: Optional[str] = None,
    ) -> "FlexPostbackAction":
        """
        Create a postback action.

        Args:
            data: The data to send in the postback
            label: The label for the action (required for buttons)
            display_text: Text to display in the chat when action is performed

        Returns:
            FlexPostbackAction instance

        """
        return cls(
            data=data,
            label=label,
            displayText=display_text,
        )


class FlexMessageAction(FlexAction):
    """Message action."""

    type: str = Field(default="message", frozen=True)
    label: str  # Required for button actions
    text: str

    @classmethod
    def create(
        cls,
        text: str,
        label: str,
    ) -> "FlexMessageAction":
        """
        Create a message action.

        Args:
            text: The text message to send
            label: The label for the action (required for buttons)

        Returns:
            FlexMessageAction instance

        """
        return cls(
            text=text,
            label=label,
        )


class FlexUriAction(FlexAction):
    """URI action."""

    type: str = Field(default="uri", frozen=True)
    label: str  # Required for button actions
    uri: str
    alt_uri_desktop: Optional[str] = Field(default=None, alias="altUriDesktop")

    @classmethod
    def create(
        cls,
        uri: str,
        label: str,
        alt_uri_desktop: Optional[str] = None,
    ) -> "FlexUriAction":
        """
        Create a URI action.

        Args:
            uri: The URI to open when the action is performed
            label: The label for the action (required for buttons)
            alt_uri_desktop: Alternative URI for desktop users

        Returns:
            FlexUriAction instance

        """
        return cls(
            uri=uri,
            label=label,
            altUriDesktop=alt_uri_desktop,
        )


class FlexComponent(BaseModel):
    """Base flex component."""

    type: str

    model_config = {"extra": "forbid"}


class FlexText(FlexComponent):
    """Text component."""

    type: str = Field(default="text", frozen=True)
    text: str
    contents: Optional[list["FlexSpan"]] = None  # For spans within text
    size: Optional[Union[FlexSize, str]] = None
    weight: Optional[FlexTextWeight] = None
    color: Optional[str] = None
    align: Optional[FlexAlignment] = None
    gravity: Optional[FlexGravity] = None
    wrap: Optional[bool] = None
    line_spacing: Optional[str] = Field(default=None, alias="lineSpacing")
    max_lines: Optional[int] = Field(default=None, alias="maxLines")
    flex: Optional[int] = None
    margin: Optional[Union[FlexSpacing, str]] = None
    position: Optional[FlexPosition] = None
    offset_top: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetTop",
    )
    offset_bottom: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetBottom",
    )
    offset_start: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetStart",
    )
    offset_end: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetEnd",
    )
    action: Optional[Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]] = None
    adjust_mode: Optional[FlexAdjustMode] = Field(default=None, alias="adjustMode")
    scaling: Optional[bool] = None

    @classmethod
    def create(
        cls,
        text: str,
        *,
        contents: Optional[list["FlexSpan"]] = None,
        size: Optional[Union[FlexSize, str]] = None,
        weight: Optional[FlexTextWeight] = None,
        color: Optional[str] = None,
        align: Optional[FlexAlignment] = None,
        gravity: Optional[FlexGravity] = None,
        wrap: Optional[bool] = None,
        line_spacing: Optional[str] = None,
        max_lines: Optional[int] = None,
        flex: Optional[int] = None,
        margin: Optional[Union[FlexSpacing, str]] = None,
        action: Optional[
            Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
        ] = None,
        adjust_mode: Optional[FlexAdjustMode] = None,
        scaling: Optional[bool] = None,
    ) -> "FlexText":
        """Create a FlexText component with the given parameters."""
        return cls(
            text=text,
            contents=contents,
            size=size,
            weight=weight,
            color=color,
            align=align,
            gravity=gravity,
            wrap=wrap,
            lineSpacing=line_spacing,
            maxLines=max_lines,
            flex=flex,
            margin=margin,
            action=action,
            adjustMode=adjust_mode,
            scaling=scaling,
        )


class FlexButton(FlexComponent):
    """Button component."""

    type: str = Field(default="button", frozen=True)
    action: Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
    style: Optional[FlexButtonStyle] = None
    color: Optional[str] = None
    height: Optional[FlexButtonHeight] = None
    gravity: Optional[FlexGravity] = None
    flex: Optional[int] = None
    margin: Optional[Union[FlexSpacing, str]] = None
    position: Optional[FlexPosition] = None
    offset_top: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetTop",
    )
    offset_bottom: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetBottom",
    )
    offset_start: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetStart",
    )
    offset_end: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetEnd",
    )
    adjust_mode: Optional[FlexAdjustMode] = Field(default=None, alias="adjustMode")
    scaling: Optional[bool] = None

    @classmethod
    def create(
        cls,
        action: Union[FlexPostbackAction, FlexMessageAction, FlexUriAction],
        *,
        style: Optional[FlexButtonStyle] = None,
        color: Optional[str] = None,
        height: Optional[FlexButtonHeight] = None,
        gravity: Optional[FlexGravity] = None,
        flex: Optional[int] = None,
        margin: Optional[Union[FlexSpacing, str]] = None,
        adjust_mode: Optional[FlexAdjustMode] = None,
        scaling: Optional[bool] = None,
    ) -> "FlexButton":
        """Create a FlexButton component with the given parameters."""
        return cls(
            action=action,
            style=style,
            color=color,
            height=height,
            gravity=gravity,
            flex=flex,
            margin=margin,
            adjustMode=adjust_mode,
            scaling=scaling,
        )


class FlexImage(FlexComponent):
    """Image component."""

    type: str = Field(default="image", frozen=True)
    url: str
    position: Optional[FlexPosition] = None
    margin: Optional[Union[FlexSpacing, str]] = None
    size: Optional[Union[FlexSize, str]] = None
    aspect_ratio: Optional[str] = Field(default=None, alias="aspectRatio")
    aspect_mode: Optional[FlexImageAspectMode] = Field(default=None, alias="aspectMode")
    background_color: Optional[str] = Field(default=None, alias="backgroundColor")
    gravity: Optional[FlexGravity] = None
    flex: Optional[int] = None
    align: Optional[FlexAlignment] = None
    animated: Optional[bool] = None
    offset_top: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetTop",
    )
    offset_bottom: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetBottom",
    )
    offset_start: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetStart",
    )
    offset_end: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetEnd",
    )
    action: Optional[Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]] = None

    @classmethod
    def create(
        cls,
        url: str,
        *,
        size: Optional[Union[FlexSize, str]] = None,
        aspect_ratio: Optional[str] = None,
        aspect_mode: Optional[FlexImageAspectMode] = None,
        background_color: Optional[str] = None,
        gravity: Optional[FlexGravity] = None,
        flex: Optional[int] = None,
        align: Optional[FlexAlignment] = None,
        animated: Optional[bool] = None,
        margin: Optional[Union[FlexSpacing, str]] = None,
        action: Optional[
            Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
        ] = None,
    ) -> "FlexImage":
        """Create a FlexImage component with the given parameters."""
        return cls(
            url=url,
            size=size,
            aspectRatio=aspect_ratio,
            aspectMode=aspect_mode,
            backgroundColor=background_color,
            gravity=gravity,
            flex=flex,
            align=align,
            animated=animated,
            margin=margin,
            action=action,
        )


class FlexSeparator(FlexComponent):
    """Separator component."""

    type: str = Field(default="separator", frozen=True)
    margin: Optional[Union[FlexSpacing, str]] = None
    color: Optional[str] = None

    @classmethod
    def create(
        cls,
        *,
        margin: Optional[Union[FlexSpacing, str]] = None,
        color: Optional[str] = None,
    ) -> "FlexSeparator":
        """Create a FlexSeparator component with the given parameters."""
        return cls(margin=margin, color=color)


class FlexIcon(FlexComponent):
    """Icon component for decorating text (baseline box only)."""

    type: str = Field(default="icon", frozen=True)
    url: str
    size: Optional[Union[FlexSize, str]] = None
    aspect_ratio: Optional[str] = Field(default=None, alias="aspectRatio")
    margin: Optional[Union[FlexSpacing, str]] = None
    position: Optional[FlexPosition] = None
    offset_top: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetTop",
    )
    offset_bottom: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetBottom",
    )
    offset_start: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetStart",
    )
    offset_end: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetEnd",
    )
    scaling: Optional[bool] = None

    @classmethod
    def create(
        cls,
        url: str,
        *,
        size: Optional[Union[FlexSize, str]] = None,
        aspect_ratio: Optional[str] = None,
        margin: Optional[Union[FlexSpacing, str]] = None,
        scaling: Optional[bool] = None,
    ) -> "FlexIcon":
        """Create a FlexIcon component with the given parameters."""
        return cls(
            url=url,
            size=size,
            aspectRatio=aspect_ratio,
            margin=margin,
            scaling=scaling,
        )


class FlexSpan(FlexComponent):
    """Span component for styled text within text components."""

    type: str = Field(default="span", frozen=True)
    text: str
    size: Optional[Union[FlexSize, str]] = None
    weight: Optional[FlexTextWeight] = None
    color: Optional[str] = None
    decoration: Optional[FlexTextDecoration] = None
    style: Optional[str] = None  # For future extensions

    @classmethod
    def create(
        cls,
        text: str,
        *,
        size: Optional[Union[FlexSize, str]] = None,
        weight: Optional[FlexTextWeight] = None,
        color: Optional[str] = None,
        decoration: Optional[FlexTextDecoration] = None,
    ) -> "FlexSpan":
        """Create a FlexSpan component with the given parameters."""
        return cls(
            type="span",
            text=text,
            size=size,
            weight=weight,
            color=color,
            decoration=decoration,
        )


class FlexVideo(FlexComponent):
    """Video component for hero blocks."""

    type: str = Field(default="video", frozen=True)
    url: str
    preview_url: str = Field(alias="previewUrl")
    alt_content: Union["FlexImage", "FlexBox"] = Field(alias="altContent")
    aspect_ratio: str = Field(alias="aspectRatio")
    action: Optional[FlexUriAction] = None

    @classmethod
    def create(
        cls,
        url: str,
        preview_url: str,
        alt_content: Union["FlexImage", "FlexBox"],
        aspect_ratio: str,
        *,
        action: Optional[FlexUriAction] = None,
    ) -> "FlexVideo":
        """Create a FlexVideo component with the given parameters."""
        return cls(
            url=url,
            previewUrl=preview_url,
            altContent=alt_content,
            aspectRatio=aspect_ratio,
            action=action,
        )


class FlexFiller(FlexComponent):
    """Deprecated: Filler component for spacing (use padding/margin instead)."""

    type: str = Field(default="filler", frozen=True)
    flex: Optional[int] = None

    @classmethod
    def create(cls, *, flex: Optional[int] = None) -> "FlexFiller":
        """
        Create a FlexFiller component.

        Note: Filler is deprecated. Use padding/margin properties instead.
        """
        return cls(flex=flex)


class FlexLinearGradient(BaseModel):
    """Linear gradient background for boxes."""

    type: str = Field(default="linearGradient", frozen=True)
    angle: str
    start_color: str = Field(alias="startColor")
    end_color: str = Field(alias="endColor")
    center_color: Optional[str] = Field(default=None, alias="centerColor")
    center_position: Optional[str] = Field(default=None, alias="centerPosition")

    @classmethod
    def create(
        cls,
        angle: str,
        start_color: str,
        end_color: str,
        *,
        center_color: Optional[str] = None,
        center_position: Optional[str] = None,
    ) -> "FlexLinearGradient":
        """Create a FlexLinearGradient with the given parameters."""
        return cls(
            angle=angle,
            startColor=start_color,
            endColor=end_color,
            centerColor=center_color,
            centerPosition=center_position,
        )


class FlexBox(FlexComponent):
    """Box container component."""

    type: str = Field(default="box", frozen=True)
    layout: FlexLayout
    contents: list[
        Union[
            FlexText,
            FlexButton,
            FlexImage,
            FlexIcon,
            FlexSeparator,
            FlexVideo,
            FlexFiller,
            "FlexBox",
        ]
    ]
    flex: Optional[int] = None
    spacing: Optional[Union[FlexSpacing, str]] = None
    margin: Optional[Union[FlexSpacing, str]] = None
    width: Optional[str] = None
    max_width: Optional[str] = Field(default=None, alias="maxWidth")
    height: Optional[str] = None
    max_height: Optional[str] = Field(default=None, alias="maxHeight")
    padding_all: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="paddingAll",
    )
    padding_top: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="paddingTop",
    )
    padding_bottom: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="paddingBottom",
    )
    padding_start: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="paddingStart",
    )
    padding_end: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="paddingEnd",
    )
    position: Optional[FlexPosition] = None
    offset_top: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetTop",
    )
    offset_bottom: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetBottom",
    )
    offset_start: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetStart",
    )
    offset_end: Optional[Union[FlexSpacing, str]] = Field(
        default=None,
        alias="offsetEnd",
    )
    background_color: Optional[str] = Field(default=None, alias="backgroundColor")
    background: Optional[FlexLinearGradient] = None
    border_color: Optional[str] = Field(default=None, alias="borderColor")
    border_width: Optional[str] = Field(default=None, alias="borderWidth")
    justify_content: Optional[FlexJustifyContent] = Field(
        default=None,
        alias="justifyContent",
    )
    align_items: Optional[FlexAlignItems] = Field(default=None, alias="alignItems")
    action: Optional[Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]] = None

    @classmethod
    def create(
        cls,
        layout: FlexLayout,
        contents: list[
            Union[
                FlexText,
                FlexButton,
                FlexImage,
                FlexIcon,
                FlexSeparator,
                FlexVideo,
                FlexFiller,
                "FlexBox",
            ]
        ],
        *,
        flex: Optional[int] = None,
        spacing: Optional[Union[FlexSpacing, str]] = None,
        margin: Optional[Union[FlexSpacing, str]] = None,
        width: Optional[str] = None,
        max_width: Optional[str] = None,
        height: Optional[str] = None,
        max_height: Optional[str] = None,
        padding_all: Optional[Union[FlexSpacing, str]] = None,
        padding_top: Optional[Union[FlexSpacing, str]] = None,
        padding_bottom: Optional[Union[FlexSpacing, str]] = None,
        padding_start: Optional[Union[FlexSpacing, str]] = None,
        padding_end: Optional[Union[FlexSpacing, str]] = None,
        background_color: Optional[str] = None,
        background: Optional[FlexLinearGradient] = None,
        border_color: Optional[str] = None,
        border_width: Optional[str] = None,
        justify_content: Optional[FlexJustifyContent] = None,
        align_items: Optional[FlexAlignItems] = None,
        action: Optional[
            Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
        ] = None,
    ) -> "FlexBox":
        """Create a FlexBox component with the given parameters."""
        return cls(
            layout=layout,
            contents=contents,
            flex=flex,
            spacing=spacing,
            margin=margin,
            width=width,
            maxWidth=max_width,
            height=height,
            maxHeight=max_height,
            paddingAll=padding_all,
            paddingTop=padding_top,
            paddingBottom=padding_bottom,
            paddingStart=padding_start,
            paddingEnd=padding_end,
            backgroundColor=background_color,
            background=background,
            borderColor=border_color,
            borderWidth=border_width,
            justifyContent=justify_content,
            alignItems=align_items,
            action=action,
        )


class FlexBubble(BaseModel):
    """Flex bubble container."""

    type: str = Field(default="bubble", frozen=True)
    size: Optional[FlexBubbleSize] = None
    direction: Optional[FlexDirection] = None
    header: Optional[FlexBox] = None
    hero: Optional[Union[FlexImage, FlexVideo, FlexBox]] = None
    body: Optional[FlexBox] = None
    footer: Optional[FlexBox] = None
    styles: Optional[dict[str, Any]] = None
    action: Optional[Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]] = None

    @classmethod
    def create(
        cls,
        *,
        size: Optional[FlexBubbleSize] = None,
        direction: Optional[FlexDirection] = None,
        header: Optional[FlexBox] = None,
        hero: Optional[Union[FlexImage, FlexVideo, FlexBox]] = None,
        body: Optional[FlexBox] = None,
        footer: Optional[FlexBox] = None,
        styles: Optional[dict[str, Any]] = None,
        action: Optional[
            Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
        ] = None,
    ) -> "FlexBubble":
        """Create a FlexBubble with the given components."""
        return cls(
            size=size,
            direction=direction,
            header=header,
            hero=hero,
            body=body,
            footer=footer,
            styles=styles,
            action=action,
        )


class FlexCarousel(BaseModel):
    """Flex carousel container."""

    type: str = Field(default="carousel", frozen=True)
    contents: list[FlexBubble]

    @classmethod
    def create(cls, bubbles: list[FlexBubble]) -> "FlexCarousel":
        """Create a FlexCarousel with the given bubbles."""
        return cls(contents=bubbles)


class FlexMessage(BaseModel):
    """
    Main flex message structure.

    This is the unified FlexMessage class that can be used both for building
    Flex content and for sending via the LINE Messaging API.
    """

    type: str = Field(default="flex", frozen=True)
    altText: str = Field(..., description="Alternative text for notifications")
    contents: Union[FlexBubble, FlexCarousel, dict[str, Any]]

    # For API compatibility
    model_config = {"extra": "forbid"}

    @classmethod
    def create(
        cls,
        alt_text: str,
        contents: Union[FlexBubble, FlexCarousel, dict[str, Any]],
    ) -> "FlexMessage":
        """
        Create a FlexMessage with the given alt text and contents.

        Supports both Pydantic models and dict contents for maximum flexibility.
        Automatically converts Pydantic models to the proper format for the LINE API.

        Args:
            alt_text: Alternative text for notifications
            contents: Flex message content (FlexBubble, FlexCarousel, or dict)

        Returns:
            FlexMessage instance

        Example:
            >>> from line_api import FlexMessage, FlexBubble, FlexBox, FlexText
            >>>
            >>> # Create flex components
            >>> text = FlexText.create("Hello")
            >>> box = FlexBox.create(layout="vertical", contents=[text])
            >>> bubble = FlexBubble.create(body=box)
            >>>
            >>> # Create message - works with both Pydantic models and dicts
            >>> message = FlexMessage.create("Hello", bubble)

        """
        return cls(altText=alt_text, contents=contents)

    def model_dump(
        self,
        *,
        exclude_none: bool = True,
        mode: str = "json",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Export the FlexMessage to a dictionary format suitable for the LINE API.

        This method ensures that nested Pydantic models are properly converted
        to dictionaries when sending to the LINE API.
        """
        # Get base model dump
        data = super().model_dump(exclude_none=exclude_none, mode=mode, **kwargs)

        # Ensure contents is properly serialized if it's a Pydantic model
        if isinstance(self.contents, (FlexBubble, FlexCarousel)):
            data["contents"] = self.contents.model_dump(exclude_none=True, mode="json")

        return data
