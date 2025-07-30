#!/usr/bin/env python3
"""
Enhanced FlexMessage example showcasing new components and properties.

This example demonstrates:
- Video component in hero block
- Icon components in baseline layout
- Span components for styled text
- Linear gradient backgrounds
- Enhanced sizing and spacing options
- New properties across all components
"""

from line_api.flex_messages import (
    FlexAlignment,
    FlexBox,
    FlexBubble,
    FlexBubbleSize,
    FlexButton,
    FlexButtonHeight,
    FlexButtonStyle,
    FlexGravity,
    FlexIcon,
    FlexImage,
    FlexImageAspectMode,
    FlexLayout,
    FlexLinearGradient,
    FlexMessage,
    FlexMessageAction,
    FlexSeparator,
    FlexSize,
    FlexSpacing,
    FlexSpan,
    FlexText,
    FlexTextWeight,
    FlexUriAction,
    FlexVideo,
    print_flex_json,
)


def create_enhanced_cafe_message() -> FlexMessage:
    """Create an enhanced cafe flex message with video and styled components."""
    # Create spans for styled brand text
    line_span = FlexSpan.create(
        "LINE",
        weight=FlexTextWeight.BOLD,
        color="#00C300",
        size=FlexSize.XL,
    )
    cafe_span = FlexSpan.create(
        " Cafe Premium",
        weight=FlexTextWeight.BOLD,
        color="#333333",
        size=FlexSize.XL,
    )

    # Header with styled text and gradient background
    header_text = FlexText.create(
        "Welcome to our premium cafe",
        contents=[line_span, cafe_span],
        align=FlexAlignment.CENTER,
        line_spacing="4px",
    )

    # Create gradient background
    header_gradient = FlexLinearGradient.create(
        angle="135deg",
        start_color="#00C300",
        end_color="#00A000",
    )

    header = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[header_text],
        padding_all=FlexSpacing.LG,
        background=header_gradient,
    )

    # Create alt content for video (fallback image)
    alt_image = FlexImage.create(
        "https://example.com/cafe-video-preview.jpg",
        size="full",
        aspect_ratio="16:9",
        aspect_mode=FlexImageAspectMode.COVER,
    )

    # Video hero with action
    video_action = FlexUriAction(
        uri="https://example.com/cafe-tour",
        label="Take Virtual Tour",
    )

    hero_video = FlexVideo.create(
        url="https://example.com/cafe-intro.mp4",
        preview_url="https://example.com/cafe-video-thumb.jpg",
        alt_content=alt_image,
        aspect_ratio="16:9",
        action=video_action,
    )

    # Rating section with star icons
    star_icon = FlexIcon.create(
        "https://example.com/star-filled.png",
        size=FlexSize.SM,
    )

    empty_star_icon = FlexIcon.create(
        "https://example.com/star-empty.png",
        size=FlexSize.SM,
    )

    rating_text = FlexText.create(
        "4.8 (2.1k reviews)",
        size=FlexSize.SM,
        color="#666666",
        margin=FlexSpacing.SM,
        flex=0,
    )

    rating_box = FlexBox.create(
        layout=FlexLayout.BASELINE,
        contents=[
            star_icon,
            star_icon,
            star_icon,
            star_icon,
            empty_star_icon,
            rating_text,
        ],
        spacing=FlexSpacing.XS,
        margin=FlexSpacing.MD,
    )

    # Menu highlights with enhanced text styling
    menu_title = FlexText.create(
        "Today's Special",
        size=FlexSize.LG,
        weight=FlexTextWeight.BOLD,
        color="#333333",
        margin=FlexSpacing.MD,
    )

    # Menu item with icon and description
    coffee_icon = FlexIcon.create(
        "https://example.com/coffee-icon.png",
        size=FlexSize.MD,
    )

    coffee_name = FlexText.create(
        "Premium Ethiopian Blend",
        weight=FlexTextWeight.BOLD,
        size=FlexSize.MD,
        flex=1,
    )

    coffee_price = FlexText.create(
        "$4.50",
        size=FlexSize.MD,
        color="#00C300",
        weight=FlexTextWeight.BOLD,
        align=FlexAlignment.END,
        flex=0,
    )

    coffee_item = FlexBox.create(
        layout=FlexLayout.BASELINE,
        contents=[coffee_icon, coffee_name, coffee_price],
        spacing=FlexSpacing.SM,
        margin=FlexSpacing.SM,
    )

    coffee_description = FlexText.create(
        "Rich, full-bodied coffee with notes of chocolate and citrus. Sustainably sourced from Ethiopian highlands.",
        wrap=True,
        color="#666666",
        size=FlexSize.SM,
        line_spacing="6px",
        margin=FlexSpacing.SM,
    )

    # Location info with enhanced styling
    location_icon = FlexIcon.create(
        "https://example.com/location-icon.png",
        size=FlexSize.SM,
    )

    location_text = FlexText.create(
        "Downtown - 5 min walk from station",
        size=FlexSize.SM,
        color="#666666",
        flex=1,
    )

    location_box = FlexBox.create(
        layout=FlexLayout.BASELINE,
        contents=[location_icon, location_text],
        spacing=FlexSpacing.SM,
        margin=FlexSpacing.MD,
    )

    # Hours with styled spans
    hours_label = FlexSpan.create("Hours: ", weight=FlexTextWeight.BOLD)
    hours_time = FlexSpan.create("7:00 AM - 9:00 PM", color="#666666")

    hours_text = FlexText.create(
        "Store hours",
        contents=[hours_label, hours_time],
        size=FlexSize.SM,
        margin=FlexSpacing.SM,
    )

    # Create separator with custom color
    separator = FlexSeparator.create(
        margin=FlexSpacing.LG,
        color="#e0e0e0",
    )

    # Body content
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            rating_box,
            separator,
            menu_title,
            coffee_item,
            coffee_description,
            separator,
            location_box,
            hours_text,
        ],
        spacing=FlexSpacing.SM,
        padding_all=FlexSpacing.LG,
        background_color="#ffffff",
    )

    # Action buttons with enhanced styling
    order_action = FlexUriAction(
        uri="https://example.com/order",
        label="Order Now",
    )

    order_button = FlexButton.create(
        action=order_action,
        style=FlexButtonStyle.PRIMARY,
        height=FlexButtonHeight.SM,
        color="#00C300",
        gravity=FlexGravity.CENTER,
    )

    directions_action = FlexMessageAction(
        label="Get Directions",
        text="Get directions to LINE Cafe",
    )

    directions_button = FlexButton.create(
        action=directions_action,
        style=FlexButtonStyle.SECONDARY,
        height=FlexButtonHeight.SM,
        color="#666666",
    )

    footer = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[order_button, directions_button],
        spacing=FlexSpacing.SM,
        padding_all=FlexSpacing.MD,
        background_color="#f8f8f8",
    )

    # Create bubble with video support (requires mega size)
    bubble = FlexBubble.create(
        size=FlexBubbleSize.MEGA,
        header=header,
        hero=hero_video,
        body=body,
        footer=footer,
        styles={
            "body": {
                "separator": True,
                "separatorColor": "#e0e0e0",
            },
            "footer": {
                "separator": True,
                "separatorColor": "#e0e0e0",
            },
        },
    )

    # Create the final message
    message = FlexMessage.create(
        alt_text="LINE Cafe Premium - Today's Special: Ethiopian Blend $4.50. Open 7AM-9PM downtown.",
        contents=bubble,
    )

    return message


def main() -> None:
    """Create and display the enhanced flex message."""
    message = create_enhanced_cafe_message()

    # Print JSON for testing in LINE Flex Message Simulator
    print_flex_json(message, "Enhanced LINE Cafe with Video")

    print("\n✅ Enhanced FlexMessage created successfully!")
    print("📱 Features demonstrated:")
    print("   • Video component in hero block")
    print("   • Icon components in baseline layout")
    print("   • Span components for styled text")
    print("   • Linear gradient backgrounds")
    print("   • Enhanced sizing with FlexSize enum")
    print("   • Improved spacing with FlexSpacing enum")
    print("   • New properties: line_spacing, scaling, adjust_mode")
    print("   • Enhanced button and image properties")
    print("   • Type-safe enums for all size and style options")


if __name__ == "__main__":
    main()
