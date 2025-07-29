"""Test latest FlexMessage functionality with comprehensive components."""

import pytest
from pydantic import ValidationError

from line_api.flex_messages import (
    FlexAlignment,
    FlexBox,
    FlexBubble,
    FlexBubbleSize,
    FlexButton,
    FlexButtonStyle,
    FlexIcon,
    FlexImage,
    FlexLayout,
    FlexLinearGradient,
    FlexMessage,
    FlexSize,
    FlexSpacing,
    FlexSpan,
    FlexText,
    FlexTextWeight,
    FlexUriAction,
    FlexVideo,
    print_flex_json,
)


def test_enhanced_flex_message() -> None:
    """Test creating a comprehensive FlexMessage with all latest components."""
    # 1. Create fallback image for video
    fallback_image = FlexImage.create(
        url="https://example.com/fallback.jpg",
        size="full",
        aspect_ratio="16:9",
    )

    # 2. Create video component for hero
    video = FlexVideo.create(
        url="https://example.com/video.mp4",
        preview_url="https://example.com/preview.jpg",
        alt_content=fallback_image,
        aspect_ratio="16:9",
    )

    # 3. Create styled text with spans
    styled_text = FlexText.create(
        text="",  # Empty when using spans
        contents=[
            FlexSpan.create("Welcome to ", weight=FlexTextWeight.REGULAR),
            FlexSpan.create("LINE API", weight=FlexTextWeight.BOLD, color="#00C300"),
            FlexSpan.create(" Testing!", weight=FlexTextWeight.BOLD),
        ],
        size=FlexSize.XL,
    )

    # 4. Create icon-based rating
    rating_box = FlexBox.create(
        layout=FlexLayout.BASELINE,
        contents=[
            FlexIcon.create("https://example.com/star.png", size=FlexSize.SM),
            FlexIcon.create("https://example.com/star.png", size=FlexSize.SM),
            FlexIcon.create("https://example.com/star.png", size=FlexSize.SM),
            FlexText.create("4.5/5", size=FlexSize.SM, margin=FlexSpacing.SM, flex=0),
        ],
        spacing=FlexSpacing.XS,
    )

    # 5. Create gradient background
    gradient = FlexLinearGradient.create(
        angle="45deg",
        start_color="#FF6B35",
        end_color="#F7931E",
    )

    # 6. Create action for button
    uri_action = FlexUriAction(uri="https://example.com", label="Test Action")

    # 7. Create info section with gradient background
    info_section = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexText.create(
                "Enhanced FlexMessage Test",
                align=FlexAlignment.CENTER,
                color="#FFFFFF",
                weight=FlexTextWeight.BOLD,
            ),
        ],
        background=gradient,
        padding_all=FlexSpacing.MD,
    )

    # 8. Create action button
    action_button = FlexButton.create(
        action=uri_action,
        style=FlexButtonStyle.PRIMARY,
    )

    # 9. Assemble body content
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            styled_text,
            rating_box,
            info_section,
            action_button,
        ],
        spacing=FlexSpacing.MD,
        padding_all=FlexSpacing.LG,
    )

    # 10. Create bubble with video hero
    bubble = FlexBubble.create(
        size=FlexBubbleSize.MEGA,  # Required for video
        hero=video,
        body=body,
    )

    # 11. Create complete flex message
    message = FlexMessage.create(
        alt_text="Enhanced FlexMessage with video, icons, spans, and gradients",
        contents=bubble,
    )

    # Assertions
    assert message.type == "flex"
    assert (
        message.alt_text
        == "Enhanced FlexMessage with video, icons, spans, and gradients"
    )
    assert isinstance(message.contents, FlexBubble)
    assert message.contents.size == FlexBubbleSize.MEGA

    # Test video component
    assert isinstance(message.contents.hero, FlexVideo)
    assert message.contents.hero.url == "https://example.com/video.mp4"
    assert message.contents.hero.aspect_ratio == "16:9"

    # Test body structure
    assert isinstance(message.contents.body, FlexBox)
    assert len(message.contents.body.contents) == 4

    # Test styled text with spans
    styled_text_component = message.contents.body.contents[0]
    assert isinstance(styled_text_component, FlexText)
    assert styled_text_component.contents is not None
    assert len(styled_text_component.contents) == 3
    assert isinstance(styled_text_component.contents[0], FlexSpan)

    # Test icon components in rating
    rating_component = message.contents.body.contents[1]
    assert isinstance(rating_component, FlexBox)
    assert rating_component.layout == FlexLayout.BASELINE
    assert isinstance(rating_component.contents[0], FlexIcon)

    # Test gradient background
    info_component = message.contents.body.contents[2]
    assert isinstance(info_component, FlexBox)
    assert isinstance(info_component.background, FlexLinearGradient)
    assert info_component.background.angle == "45deg"

    # Test JSON export
    result = print_flex_json(message, copy_to_clipboard=False)
    assert result is True

    # Test model validation
    json_data = message.model_dump(exclude_none=True)
    assert json_data["type"] == "flex"
    assert json_data["contents"]["type"] == "bubble"
    assert json_data["contents"]["size"] == "mega"
    assert json_data["contents"]["hero"]["type"] == "video"


def test_enum_validation() -> None:
    """Test that enum validation works correctly."""
    # Test valid enum usage
    text = FlexText.create(
        "Test",
        weight=FlexTextWeight.BOLD,
        size=FlexSize.LG,
        align=FlexAlignment.CENTER,
    )
    assert text.weight == FlexTextWeight.BOLD
    assert text.size == FlexSize.LG
    assert text.align == FlexAlignment.CENTER

    # Test invalid enum value raises validation error
    with pytest.raises(ValidationError):
        FlexBox.create(
            layout="invalid_layout",  # type: ignore[arg-type]
            contents=[],
        )
