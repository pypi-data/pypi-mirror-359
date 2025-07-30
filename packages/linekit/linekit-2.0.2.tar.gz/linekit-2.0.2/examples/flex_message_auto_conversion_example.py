#!/usr/bin/env python3
"""
FlexMessage Auto-Conversion Example.

This example demonstrates the new auto-conversion feature in LINE API v1.0.2+
that eliminates the need for manual .model_dump() calls when creating Flex messages.

Key Benefits:
- No more .model_dump() calls needed
- Cleaner, more intuitive API
- Automatic handling of serialization complexities
- Better developer experience

Requirements:
- Set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET environment variables
- Valid user ID for testing

Run with:
    python examples/flex_message_auto_conversion_example.py
"""

import asyncio

from line_api import (
    FlexBox,
    FlexBubble,
    FlexLayout,
    FlexText,
    LineAPIConfig,
    LineMessagingClient,
)
from line_api.flex_messages import FlexTextWeight
from line_api.messaging import FlexMessage


async def send_auto_converted_flex_message(user_id: str) -> None:
    """Demonstrate auto-conversion with a Flex message."""
    print("🎨 Creating Flex message with auto-conversion...")

    config = LineAPIConfig.from_env_file()

    # Create Flex components
    title = FlexText.create(
        text="🚀 Auto-Conversion Demo",
        weight=FlexTextWeight.BOLD,
        size="xl",
        color="#1DB954",
    )

    subtitle = FlexText.create(
        text="No more .model_dump() needed! This is so much cleaner and easier to use.",
        size="sm",
        color="#666666",
        wrap=True,
    )

    description = FlexText.create(
        text="The FlexMessage.create() method now automatically converts Pydantic models to the correct format for the LINE API.",
        wrap=True,
        color="#333333",
    )

    # Create layout
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[title, subtitle, description],
        spacing="md",
    )

    bubble = FlexBubble.create(body=body)

    # ✨ AUTO-CONVERSION: Direct Pydantic model usage!
    flex_message = FlexMessage.create(
        alt_text="Auto-Conversion Demo - No more .model_dump() needed!",
        contents=bubble,  # 🎉 No .model_dump() required!
    )

    try:
        async with LineMessagingClient(config) as client:
            success = await client.push_message(
                user_id=user_id,
                messages=[flex_message],
            )
            if success:
                print("✅ Auto-converted Flex message sent successfully!")
                print("💡 Notice: No .model_dump() was needed!")
            else:
                print("❌ Failed to send Flex message")
    except Exception as e:
        print(f"❌ Error: {e}")


def show_before_after_comparison() -> None:
    """Show the before/after code comparison."""
    print("\n" + "=" * 60)
    print("📊 BEFORE vs AFTER: Code Comparison")
    print("=" * 60)

    print("\n❌ BEFORE (LINE API v1.0.1 and earlier):")
    print("```python")
    print("# Manual serialization required")
    print("bubble = FlexBubble.create(body=body)")
    print("flex_message = FlexMessage.create(")
    print("    alt_text='Hello',")
    print("    contents=bubble.model_dump(exclude_none=True, mode='json')  # Manual!")
    print(")")
    print("```")

    print("\n✅ AFTER (LINE API v1.0.2+):")
    print("```python")
    print("# Auto-conversion - much cleaner!")
    print("bubble = FlexBubble.create(body=body)")
    print("flex_message = FlexMessage.create(")
    print("    alt_text='Hello',")
    print("    contents=bubble  # Auto-converted! 🎉")
    print(")")
    print("```")

    print("\n🎯 Benefits:")
    print("- ✨ Cleaner, more intuitive API")
    print("- 🚫 No more .model_dump() calls")
    print("- 🛡️ Automatic serialization handling")
    print("- 📱 Better developer experience")
    print("- 🔧 Reduced boilerplate code")


async def demonstrate_multicast_auto_conversion(user_id: str) -> None:
    """Demonstrate auto-conversion with multicast messages."""
    print("📡 Testing auto-conversion with multicast messages...")

    config = LineAPIConfig.from_env_file()

    # Create a promotional Flex message
    title = FlexText.create(
        text="🎉 Special Offer!",
        weight=FlexTextWeight.BOLD,
        size="xl",
        color="#FF6B6B",
    )

    offer = FlexText.create(
        text="Get 50% off on all items today only!",
        wrap=True,
        color="#555555",
    )

    cta = FlexText.create(
        text="Shop Now →",
        weight=FlexTextWeight.BOLD,
        color="#4ECDC4",
    )

    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[title, offer, cta],
        spacing="md",
    )

    bubble = FlexBubble.create(body=body)

    # ✨ AUTO-CONVERSION in multicast!
    flex_message = FlexMessage.create(
        alt_text="Special Offer - 50% off today!",
        contents=bubble,  # 🎉 Works with multicast too!
    )

    try:
        async with LineMessagingClient(config) as client:
            success = await client.multicast_message(
                user_ids=[user_id],
                messages=[flex_message],
            )
            if success:
                print("✅ Auto-converted multicast Flex message sent!")
                print("💡 Auto-conversion works with all message types!")
            else:
                print("❌ Failed to send multicast Flex message")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main() -> None:
    """Run auto-conversion demonstration."""
    print("🚀 LINE API FlexMessage Auto-Conversion Demo")
    print("=" * 50)

    show_before_after_comparison()

    # Get user ID for testing
    user_id = input("\n📝 Enter a user ID to test with: ").strip()

    if not user_id:
        print("⚠️ No user ID provided. Using placeholder for demonstration.")
        user_id = "USER_ID_PLACEHOLDER"

    print(f"\n🎯 Testing with user ID: {user_id}")

    # Run demonstrations
    examples = [
        (
            "Push Message Auto-Conversion",
            lambda: send_auto_converted_flex_message(user_id),
        ),
        (
            "Multicast Auto-Conversion",
            lambda: demonstrate_multicast_auto_conversion(user_id),
        ),
    ]

    for name, example_func in examples:
        print(f"\n📋 {name}")
        print("-" * 30)
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example failed: {e}")
        print()

    print("🎉 Auto-conversion demonstration completed!")
    print("\n💡 Key Takeaway:")
    print("   You can now pass Pydantic models directly to FlexMessage.create()")
    print("   without worrying about .model_dump() serialization!")


if __name__ == "__main__":
    asyncio.run(main())
