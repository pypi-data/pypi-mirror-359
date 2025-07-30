#!/usr/bin/env python3
"""
Unified FlexMessage Example - Simplified Developer Experience.

This example demonstrates the simplified FlexMessage API where users only need
to work with one FlexMessage class instead of two confusing ones.

Key Benefits:
- Only ONE FlexMessage class to import and use
- No confusion between flex_messages.FlexMessage and messaging.FlexMessage
- Seamless integration with messaging API
- Clean, intuitive developer experience

Requirements:
- Set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET environment variables
- Have a valid user ID from your LINE channel

Run with:
    python examples/unified_flex_message_example.py
"""

import asyncio

from line_api import (
    FlexBox,
    FlexBubble,
    FlexButton,
    FlexImage,
    FlexLayout,
    FlexMessage,
    FlexText,
    LineAPIConfig,
    LineMessagingClient,
)
from line_api.flex_messages import (
    FlexButtonStyle,
    FlexSpacing,
    FlexTextWeight,
    FlexUriAction,
)


async def send_unified_flex_message() -> None:
    """Demonstrate the unified FlexMessage approach."""
    print("🎯 Unified FlexMessage Example")
    print("=" * 40)

    config = LineAPIConfig.from_env_file()

    # Get user ID for testing
    user_id = input("Enter your LINE user ID: ").strip()
    if not user_id:
        print("❌ User ID is required")
        return

    # Create Flex components using the familiar API
    hero_image = FlexImage.create(
        url="https://via.placeholder.com/400x200/FF6B6B/FFFFFF?text=Sale+Alert",
        size="full",
    )

    title = FlexText.create(
        text="🛍️ FLASH SALE",
        weight=FlexTextWeight.BOLD,
        size="xl",
        color="#FF6B6B",
    )

    description = FlexText.create(
        text="Get 70% off on all items! Limited time offer. Don't miss out!",
        wrap=True,
        color="#666666",
        size="sm",
    )

    action_button = FlexButton.create(
        action=FlexUriAction(
            uri="https://example.com/sale",
            label="Shop Now",
        ),
        style=FlexButtonStyle.PRIMARY,
        color="#FF6B6B",
    )

    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[title, description, action_button],
        spacing=FlexSpacing.MD,
    )

    bubble = FlexBubble.create(
        hero=hero_image,
        body=body,
    )

    # ✨ THE MAGIC: Only ONE FlexMessage class!
    # No confusion, no need to import from messaging module
    flex_message = FlexMessage.create(
        alt_text="Flash Sale - 70% off all items!",
        contents=bubble,
    )

    print("\n📦 Created FlexMessage using unified API")
    print("✅ No confusion between different FlexMessage classes")
    print("✅ Direct usage with messaging client")

    try:
        async with LineMessagingClient(config) as client:
            # Direct usage - no conversion needed!
            success = await client.push_message(
                user_id=user_id,
                messages=[flex_message],
            )

            if success:
                print("\n🎉 SUCCESS!")
                print(f"✅ FlexMessage sent to user: {user_id}")
                print("✅ Used unified line_api.FlexMessage class")
                print("✅ No manual conversion or confusion!")
            else:
                print("\n❌ Failed to send message")

    except Exception as e:
        print(f"\n❌ Error: {e}")


async def demonstrate_before_after() -> None:
    """Show the difference between old confusing approach and new unified approach."""
    print("\n📊 Before vs After Comparison")
    print("=" * 50)
    
    print("\n❌ OLD CONFUSING APPROACH:")
    print("```python")
    print("# Users had to import TWO different FlexMessage classes")
    print("from line_api import FlexBubble, FlexBox, FlexText")
    print("from line_api.messaging import FlexMessage as MessagingFlexMessage")
    print("")
    print("# Create components")
    print("bubble = FlexBubble.create(...)")
    print("")
    print("# CONFUSING: Different FlexMessage for API")
    print("message = MessagingFlexMessage.create(")
    print("    alt_text='Hello',")
    print("    contents=bubble.model_dump()  # Manual conversion needed!")
    print(")")
    print("```")

    print("\n✅ NEW UNIFIED APPROACH:")
    print("```python")
    print("# Users import only ONE FlexMessage class")
    print("from line_api import FlexBubble, FlexBox, FlexText, FlexMessage")
    print("")
    print("# Create components")
    print("bubble = FlexBubble.create(...)")
    print("")
    print("# SIMPLE: Same FlexMessage for everything!")
    print("message = FlexMessage.create(")
    print("    altText='Hello',")
    print("    contents=bubble  # Auto-conversion handled internally!")
    print(")")
    print("```")

    print("\n🎯 BENEFITS:")
    print("• Only ONE FlexMessage class to remember")
    print("• No confusion about which import to use")
    print("• No manual .model_dump() calls needed")
    print("• Seamless integration with messaging API")
    print("• Better developer experience")
    print("• Less cognitive load")


async def main() -> None:
    """Run the unified FlexMessage demonstration."""
    print("🚀 LINE API Unified FlexMessage Example")
    print("This demonstrates the new simplified developer experience\n")

    # Show the conceptual improvement
    await demonstrate_before_after()

    # Ask if user wants to send a real message
    send_real = input("\n📤 Send a real FlexMessage? (y/n): ").strip().lower()
    if send_real in ("y", "yes"):
        await send_unified_flex_message()
    else:
        print("\n✅ Example completed without sending messages")

    print("\n🎉 Unified FlexMessage Example Complete!")
    print("\nKey takeaways:")
    print("• Import only 'line_api.FlexMessage' - no confusion!")
    print("• Same class for building AND sending messages")
    print("• Automatic conversion handled internally")
    print("• Much better developer experience")


if __name__ == "__main__":
    asyncio.run(main())
