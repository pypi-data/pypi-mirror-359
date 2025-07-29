#!/usr/bin/env python3
"""
LINE API Multicast Message Example.

This example demonstrates how to send multicast messages to multiple users
using various message types including text, images, flex messages, and more.

Requirements:
- Set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET environment variables
- Have valid user IDs from your LINE channel

Run with:
    python examples/multicast_message_example.py
"""

import asyncio
import uuid
from typing import Any, Optional

from line_api import (
    FlexBox,
    FlexBubble,
    FlexLayout,
    FlexMessage,
    FlexText,
    LineAPIConfig,
    LineMessagingClient,
    TextMessage,
)
from line_api.messaging import LocationMessage, StickerMessage


def get_user_ids_from_input() -> list[str]:
    """
    Get user IDs from terminal input for quick testing.

    Returns:
        List of user IDs entered by the user

    """
    print(
        "\n📝 Enter user IDs for testing (press Enter after each ID, empty line to finish):"
    )
    print(
        "💡 You can get user IDs from webhook events when users interact with your bot"
    )
    print("💡 For testing, you can use your own user ID from LINE Developers Console")

    user_ids: list[str] = []
    while True:
        try:
            user_id = input(
                f"User ID #{len(user_ids) + 1} (or press Enter to finish): "
            ).strip()
            if not user_id:
                break
            user_ids.append(user_id)
            print(f"✅ Added: {user_id}")
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return []

    if not user_ids:
        print(
            "⚠️  No user IDs entered. Using default placeholder IDs for demonstration."
        )
        return ["USER_ID_1", "USER_ID_2"]

    print(f"\n✅ Total {len(user_ids)} user ID(s) entered")
    return user_ids


async def send_basic_multicast_text(user_ids: Optional[list[str]] = None) -> None:
    """Send a basic text message to multiple users."""
    print("🚀 Sending basic multicast text message...")

    config = LineAPIConfig.from_env_file()

    # Use provided user IDs or get from input
    if user_ids is None:
        user_ids = get_user_ids_from_input()

    # Create a simple text message
    message = TextMessage.create(
        "🎉 Hello from multicast! This message was sent to multiple users simultaneously."
    )

    try:
        async with LineMessagingClient(config) as client:
            success = await client.multicast_message(
                user_ids=user_ids,
                messages=[message],
            )
            if success:
                print(
                    f"✅ Multicast message sent successfully to {len(user_ids)} users!"
                )
            else:
                print("❌ Failed to send multicast message")
    except Exception as e:
        print(f"❌ Error: {e}")


async def send_multicast_with_options(user_ids: Optional[list[str]] = None) -> None:
    """Send multicast message with advanced options."""
    print("🛠️ Sending multicast message with advanced options...")

    config = LineAPIConfig.from_env_file()

    # Use provided user IDs or get from input
    if user_ids is None:
        user_ids = get_user_ids_from_input()

    # Create messages
    messages = [
        TextMessage.create("📊 Marketing Campaign Update"),
        TextMessage.create("Check out our latest promotions!"),
    ]

    # Generate a unique retry key for idempotent requests
    retry_key = str(uuid.uuid4())

    try:
        async with LineMessagingClient(config) as client:
            success = await client.multicast_message(
                user_ids=user_ids,
                messages=messages,
                notification_disabled=False,  # Users will receive notifications
                custom_aggregation_units=["summer_campaign_2024"],  # For analytics
                retry_key=retry_key,  # For request idempotency
            )
            if success:
                print(f"✅ Advanced multicast message sent to {len(user_ids)} users!")
                print("Tracked under aggregation unit: summer_campaign_2024")
                print(f"🔄 Retry key: {retry_key}")
            else:
                print("❌ Failed to send multicast message")
    except Exception as e:
        print(f"❌ Error: {e}")


async def send_multicast_flex_message(user_ids: Optional[list[str]] = None) -> None:
    """Send a Flex message to multiple users."""
    print("🎨 Sending multicast Flex message...")

    config = LineAPIConfig.from_env_file()

    # Use provided user IDs or get from input
    if user_ids is None:
        user_ids = get_user_ids_from_input()

    # Create a Flex message
    title = FlexText.create(
        text="🛍️ Flash Sale Alert!",
        weight="bold",
        size="xl",
        color="#FF6B6B",
    )

    description = FlexText.create(
        text="50% off all items for the next 24 hours! Don't miss out on this amazing deal.",
        wrap=True,
        color="#555555",
    )

    cta = FlexText.create(
        text="Shop Now →",
        weight="bold",
        color="#4ECDC4",
    )

    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[title, description, cta],
        spacing="md",
        padding_all="20px",
    )

    bubble = FlexBubble.create(body=body)
    flex_message = FlexMessage.create(
        alt_text="Flash Sale Alert - 50% off all items!",
        contents=bubble,
    )

    try:
        async with LineMessagingClient(config) as client:
            success = await client.multicast_message(
                user_ids=user_ids,
                messages=[flex_message],
                custom_aggregation_units=["flash_sale_promotion"],
            )
            if success:
                print(f"✅ Flex multicast message sent to {len(user_ids)} users!")
            else:
                print("❌ Failed to send Flex multicast message")
    except Exception as e:
        print(f"❌ Error: {e}")


async def send_multicast_mixed_messages(user_ids: Optional[list[str]] = None) -> None:
    """Send multiple different message types in one multicast."""
    print("🎭 Sending mixed message types via multicast...")

    config = LineAPIConfig.from_env_file()

    # Use provided user IDs or get from input
    if user_ids is None:
        user_ids = get_user_ids_from_input()

    # Create various message types
    messages: list[Any] = [
        TextMessage.create("📍 Check out this amazing location!"),
        LocationMessage.create(
            title="Tokyo Tower",
            address="4 Chome-2-8 Shibakoen, Minato City, Tokyo 105-0011, Japan",
            latitude=35.6586,
            longitude=139.7454,
        ),
        StickerMessage.create(
            package_id="446",  # LINE basic stickers
            sticker_id="1988",  # Thumbs up
        ),
    ]

    try:
        async with LineMessagingClient(config) as client:
            success = await client.multicast_message(
                user_ids=user_ids,
                messages=messages,
                notification_disabled=False,
            )
            if success:
                print(f"✅ Mixed multicast messages sent to {len(user_ids)} users!")
            else:
                print("❌ Failed to send mixed multicast messages")
    except Exception as e:
        print(f"❌ Error: {e}")


async def send_silent_multicast(user_ids: Optional[list[str]] = None) -> None:
    """Send a multicast message without push notifications."""
    print("🔇 Sending silent multicast message...")

    config = LineAPIConfig.from_env_file()

    # Use provided user IDs or get from input
    if user_ids is None:
        user_ids = get_user_ids_from_input()

    message = TextMessage.create(
        "📱 This is a silent update - you won't get a push notification for this message.",
    )

    try:
        async with LineMessagingClient(config) as client:
            success = await client.multicast_message(
                user_ids=user_ids,
                messages=[message],
                notification_disabled=True,  # No push notifications
            )
            if success:
                print(f"✅ Silent multicast message sent to {len(user_ids)} users!")
                print("🔇 No push notifications were sent")
            else:
                print("❌ Failed to send silent multicast message")
    except Exception as e:
        print(f"❌ Error: {e}")


async def demonstrate_error_handling() -> None:
    """Demonstrate error handling for multicast messages."""
    print("⚠️ Demonstrating error handling...")

    config = LineAPIConfig.from_env_file()

    # Test various error conditions
    test_cases = [
        {
            "name": "Empty user list",
            "user_ids": [],
            "messages": [TextMessage.create("Test")],
        },
        {
            "name": "Too many users",
            "user_ids": [f"USER_{i}" for i in range(501)],  # Over 500 limit
            "messages": [TextMessage.create("Test")],
        },
        {
            "name": "Too many messages",
            "user_ids": ["USER_1"],
            "messages": [
                TextMessage.create(f"Message {i}") for i in range(6)
            ],  # Over 5 limit
        },
        {
            "name": "Too many aggregation units",
            "user_ids": ["USER_1"],
            "messages": [TextMessage.create("Test")],
            "custom_aggregation_units": ["unit1", "unit2"],  # Over 1 limit
        },
    ]

    async with LineMessagingClient(config) as client:
        for test_case in test_cases:
            try:
                await client.multicast_message(
                    user_ids=list(test_case["user_ids"]),  # type: ignore
                    messages=list(test_case["messages"]),
                    custom_aggregation_units=test_case.get("custom_aggregation_units"),  # type: ignore
                )
                print(
                    f"❌ Expected error for '{test_case['name']}' but request succeeded"
                )
            except Exception as e:
                print(f"✅ Correctly caught error for '{test_case['name']}': {e}")


async def main() -> None:
    """Run all multicast message examples."""
    print("🎯 LINE API Multicast Message Examples")
    print("=" * 50)

    # Get user IDs once for all examples
    print(
        "⚠️  Important: You need valid user IDs from your LINE channel to test multicast messages"
    )
    print(
        "   You can get user IDs from webhook events when users interact with your bot"
    )

    use_input = (
        input("\n📋 Get user IDs from input? (y/n, default: n): ").strip().lower()
    )

    user_ids = None
    if use_input in ("y", "yes"):
        user_ids = get_user_ids_from_input()
    else:
        print("Using default placeholder user IDs for demonstration...")
        user_ids = ["USER_ID_1", "USER_ID_2"]

    examples = [
        ("Basic Text Multicast", lambda: send_basic_multicast_text(user_ids)),
        ("Advanced Options", lambda: send_multicast_with_options(user_ids)),
        ("Flex Message Multicast", lambda: send_multicast_flex_message(user_ids)),
        ("Mixed Message Types", lambda: send_multicast_mixed_messages(user_ids)),
        ("Silent Multicast", lambda: send_silent_multicast(user_ids)),
        ("Error Handling", demonstrate_error_handling),
    ]

    for name, example_func in examples:
        print(f"\n📋 {name}")
        print("-" * 30)
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example failed: {e}")
        print()

    print("🎉 All examples completed!")
    print("\n💡 Tips:")
    print("- Always validate user IDs before sending multicast messages")
    print("- Use retry keys for important messages to prevent duplicates")
    print("- Consider using custom aggregation units for analytics")
    print("- Be mindful of LINE's rate limits (200 requests/second for multicast)")


if __name__ == "__main__":
    asyncio.run(main())
