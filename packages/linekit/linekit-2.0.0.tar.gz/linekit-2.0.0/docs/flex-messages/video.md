# FlexMessage Video Integration

Comprehensive guide to using video components in FlexMessages for rich multimedia experiences.

## Overview

The video component allows you to display videos within FlexMessage bubbles, providing an engaging way to share multimedia content with users. Videos appear in the hero block and support interactive playback with custom actions.

## Requirements

To include videos in FlexMessages, you must meet these requirements:

### Mandatory Requirements

1. **Hero Block Only**: Video components can only be used in the hero block
2. **Bubble Size**: Bubble must be sized as `kilo`, `mega`, or `giga`
3. **No Carousel**: The bubble cannot be a child of a carousel container

```python
from line_api.flex_messages import FlexBubble, FlexVideo, FlexBubbleSize

# Correct usage
bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,  # Required: kilo, mega, or giga
    hero=FlexVideo.create(
        url="https://example.com/video.mp4",
        previewUrl="https://example.com/preview.jpg",
        aspectRatio="16:9"
    )
)
```

## Video Component Properties

### Required Properties

```python
from line_api.flex_messages import FlexVideo, FlexImage

video = FlexVideo.create(
    url="https://example.com/video.mp4",           # Video file URL
    previewUrl="https://example.com/preview.jpg",  # Preview image URL
    altContent=FlexImage.create(                   # Fallback content
        url="https://example.com/fallback.jpg",
        size="full",
        aspectRatio="16:9"
    ),
    aspectRatio="16:9"                             # Video aspect ratio
)
```

### Optional Properties

```python
from line_api.flex_messages import FlexUriAction

video = FlexVideo.create(
    url="https://example.com/video.mp4",
    previewUrl="https://example.com/preview.jpg",
    altContent=fallback_image,
    aspectRatio="16:9",
    action=FlexUriAction(                          # Custom action
        uri="https://example.com/more-info",
        label="More Information"
    )
)
```

## Video Aspect Ratios

Maintaining consistent aspect ratios is crucial for proper video display:

### Aspect Ratio Consistency

All three elements must have the same aspect ratio:

1. **Video File** (`url` property)
2. **Preview Image** (`previewUrl` property)
3. **Aspect Ratio Setting** (`aspectRatio` property)

```python
# ✅ Correct: All have 16:9 ratio
video = FlexVideo.create(
    url="https://example.com/video_16x9.mp4",      # 16:9 video file
    previewUrl="https://example.com/preview_16x9.jpg",  # 16:9 preview image
    aspectRatio="16:9"                             # 16:9 aspect ratio
)

# ❌ Incorrect: Mismatched ratios will cause cropping
video = FlexVideo.create(
    url="https://example.com/video_16x9.mp4",      # 16:9 video
    previewUrl="https://example.com/preview_1x1.jpg",   # 1:1 preview - WRONG
    aspectRatio="4:3"                              # 4:3 ratio - WRONG
)
```

### Common Aspect Ratios

| Aspect Ratio | Use Case | Description |
|--------------|----------|-------------|
| `"16:9"` | Widescreen | Standard video format |
| `"4:3"` | Traditional | Classic TV format |
| `"1:1"` | Square | Social media format |
| `"9:16"` | Vertical | Mobile/story format |
| `"21:9"` | Ultrawide | Cinematic format |

## Alternative Content

Alternative content displays when:

- LINE version doesn't support video components
- Video fails to load
- Testing in Flex Message Simulator

### Image Alternative

```python
from line_api.flex_messages import FlexVideo, FlexImage, FlexImageAspectMode

alt_image = FlexImage.create(
    url="https://example.com/fallback.jpg",
    size="full",
    aspectRatio="16:9",
    aspectMode=FlexImageAspectMode.COVER
)

video = FlexVideo.create(
    url="https://example.com/video.mp4",
    previewUrl="https://example.com/preview.jpg",
    altContent=alt_image,
    aspectRatio="16:9"
)
```

### Box Alternative

```python
from line_api.flex_messages import FlexBox, FlexText, FlexLayout

alt_box = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[
        FlexText.create(
            "Video not supported",
            align="center",
            color="#666666"
        )
    ],
    backgroundColor="#f0f0f0",
    height="200px",
    justifyContent="center"
)

video = FlexVideo.create(
    url="https://example.com/video.mp4",
    previewUrl="https://example.com/preview.jpg",
    altContent=alt_box,
    aspectRatio="16:9"
)
```

## URI Actions

Add interactive elements to videos using URI actions:

### Action Configuration

```python
from line_api.flex_messages import FlexUriAction

# Web URL action
web_action = FlexUriAction(
    uri="https://example.com/product-page",
    label="View Product"
)

# Phone call action
call_action = FlexUriAction(
    uri="tel:+1234567890",
    label="Call Now"
)

video = FlexVideo.create(
    url="https://example.com/video.mp4",
    previewUrl="https://example.com/preview.jpg",
    altContent=fallback_content,
    aspectRatio="16:9",
    action=web_action
)
```

### Action Display Locations

The action label appears in three locations:

1. **Chat Room**: After video playback completes
2. **Video Player**: During video playback
3. **Video Player**: After video playback completes

## Playback Behavior

### Chat Room Playback

Video playback in chat rooms depends on user settings:

| Setting | Behavior |
|---------|----------|
| "On mobile & Wi-Fi" | Auto-play always |
| "On Wi-Fi only" | Auto-play on Wi-Fi only |
| "Never" | Manual play only |

**Note**: Auto-play is not supported on LINE for PC (macOS/Windows).

#### After Playback

When video finishes, up to two buttons appear:

1. **Play Button**: Always present, launches video player
2. **Action Button**: Present if URI action is specified

### Video Player Playback

#### During Playback

Two buttons appear at the top:

1. **Done Button**: Always present, returns to chat room
2. **Action Button**: Present if URI action is specified

#### After Playback

Two buttons appear over the video:

1. **Replay Button**: Always present, restarts video
2. **Action Button**: Present if URI action is specified

## Complete Video Examples

### Basic Video Message

```python
from line_api.flex_messages import (
    FlexMessage, FlexBubble, FlexVideo, FlexImage,
    FlexBubbleSize, FlexImageAspectMode
)

# Create fallback image
fallback = FlexImage.create(
    url="https://example.com/fallback.jpg",
    size="full",
    aspectRatio="16:9",
    aspectMode=FlexImageAspectMode.COVER
)

# Create video component
video = FlexVideo.create(
    url="https://example.com/promotional.mp4",
    previewUrl="https://example.com/promotional_preview.jpg",
    altContent=fallback,
    aspectRatio="16:9"
)

# Create bubble with video
bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,
    hero=video
)

# Create complete message
message = FlexMessage.create(
    altText="Promotional Video",
    contents=bubble
)
```

### Video with Content and Actions

```python
from line_api.flex_messages import (
    FlexMessage, FlexBubble, FlexVideo, FlexBox, FlexText, FlexButton,
    FlexBubbleSize, FlexLayout, FlexWeight, FlexTextSize, FlexUriAction
)

# Create video with action
video_action = FlexUriAction(
    uri="https://example.com/product",
    label="Learn More"
)

video = FlexVideo.create(
    url="https://example.com/product_demo.mp4",
    previewUrl="https://example.com/demo_preview.jpg",
    altContent=fallback_image,
    aspectRatio="16:9",
    action=video_action
)

# Create body content
body = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="md",
    contents=[
        FlexText.create(
            "New Product Launch",
            weight=FlexWeight.BOLD,
            size=FlexTextSize.EXTRA_LARGE
        ),
        FlexText.create(
            "Watch our latest product demonstration and discover amazing new features.",
            wrap=True,
            color="#666666"
        )
    ]
)

# Create footer with action buttons
footer = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="sm",
    contents=[
        FlexButton.create(
            action=FlexUriAction(
                uri="https://example.com/buy",
                label="Buy Now",
            ),
            style="primary"
        ),
        FlexButton.create(
            action=FlexUriAction(
                uri="https://example.com/info",
                label="More Info",
            ),
            style="secondary"
        )
    ]
)

# Create complete bubble
bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,
    hero=video,
    body=body,
    footer=footer
)

message = FlexMessage.create(
    altText="Product Launch Video",
    contents=bubble
)
```

### Restaurant Video Card

```python
from line_api.flex_messages import (
    FlexMessage, FlexBubble, FlexVideo, FlexBox, FlexText, FlexIcon,
    FlexSeparator, FlexButton, FlexBubbleSize, FlexLayout
)

# Create restaurant video card
video = FlexVideo.create(
    url="https://example.com/restaurant_tour.mp4",
    previewUrl="https://example.com/restaurant_preview.jpg",
    altContent=fallback_image,
    aspectRatio="20:13",
    action=FlexUriAction(
        uri="https://example.com/menu",
        label="View Menu",
    )
)

# Rating stars
stars = FlexBox.create(
    layout=FlexLayout.BASELINE,
    spacing="sm",
    contents=[
        FlexIcon.create(url="https://example.com/star.png", size="sm"),
        FlexIcon.create(url="https://example.com/star.png", size="sm"),
        FlexIcon.create(url="https://example.com/star.png", size="sm"),
        FlexIcon.create(url="https://example.com/star.png", size="sm"),
        FlexIcon.create(url="https://example.com/star_gray.png", size="sm"),
        FlexText.create("4.0", size="sm", color="#999999", margin="md", flex=0)
    ]
)

# Restaurant details
details = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="sm",
    contents=[
        FlexBox.create(
            layout=FlexLayout.BASELINE,
            spacing="sm",
            contents=[
                FlexText.create("Location", color="#aaaaaa", size="sm", flex=1),
                FlexText.create("Tokyo, Japan", wrap=True, color="#666666", size="sm", flex=5)
            ]
        ),
        FlexBox.create(
            layout=FlexLayout.BASELINE,
            spacing="sm",
            contents=[
                FlexText.create("Hours", color="#aaaaaa", size="sm", flex=1),
                FlexText.create("10:00 - 23:00", color="#666666", size="sm", flex=5)
            ]
        )
    ]
)

body = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    contents=[
        FlexText.create("Sakura Restaurant", weight=FlexWeight.BOLD, size=FlexTextSize.EXTRA_LARGE),
        stars,
        FlexSeparator.create(margin="lg"),
        details
    ]
)

footer = FlexBox.create(
    layout=FlexLayout.VERTICAL,
    spacing="sm",
    contents=[
        FlexButton.create(
            action=FlexUriAction(uri="tel:+81312345678", label="Call"),
            style="primary"
        ),
        FlexButton.create(
            action=FlexUriAction(uri="https://example.com/reserve", label="Reserve"),
            style="secondary"
        )
    ]
)

bubble = FlexBubble.create(
    size=FlexBubbleSize.GIGA,
    hero=video,
    body=body,
    footer=footer
)

message = FlexMessage.create(
    altText="Sakura Restaurant Video Tour",
    contents=bubble
)
```

## Testing Videos

### Flex Message Simulator

The Flex Message Simulator cannot preview videos:

- Alternative content is displayed instead
- Use the "Send..." button to test on actual LINE
- Test video playback behavior on mobile devices

### Testing Checklist

- [ ] Video file loads correctly
- [ ] Preview image displays properly
- [ ] Aspect ratios match exactly
- [ ] Alternative content works for older LINE versions
- [ ] URI actions function as expected
- [ ] Video plays on different devices
- [ ] Auto-play behavior respects user settings

## Best Practices

### Video Optimization

- **File Size**: Keep videos under 10MB for better loading
- **Duration**: Aim for 15-60 seconds for engagement
- **Format**: Use MP4 with H.264 encoding
- **Resolution**: Match intended display size
- **Compression**: Balance quality and file size

### Preview Images

- **Quality**: Use high-quality preview images
- **Relevance**: Show representative video content
- **Aspect Ratio**: Match video exactly
- **File Size**: Optimize for web delivery

### User Experience

- **Auto-play**: Consider user data usage preferences
- **Actions**: Provide meaningful next steps
- **Fallbacks**: Always include alternative content
- **Context**: Ensure videos add value to the conversation

### Accessibility

- **Alt Text**: Provide descriptive alternative text
- **Captions**: Include captions for accessibility
- **Audio**: Don't rely solely on audio content
- **Controls**: Allow users to control playback

## Troubleshooting

### Common Issues

**Video Not Playing**:
- Check video URL accessibility
- Verify file format compatibility
- Test on different devices
- Check user's auto-play settings

**Aspect Ratio Problems**:
- Ensure video, preview, and aspectRatio match
- Test on various screen sizes
- Use consistent ratios throughout

**Alternative Content Not Showing**:
- Verify alternative content configuration
- Test with older LINE versions
- Check Flex Message Simulator preview

### Error Handling

```python
try:
    # Create video message
    message = create_video_message()

    # Send message
    await client.push_message(user_id, [message])

except Exception as e:
    # Fallback to text message
    fallback_message = TextMessage.create("Video content available at: https://example.com/video")
    await client.push_message(user_id, [fallback_message])
```

## Integration with Other Components

Videos work well with other FlexMessage components:

### Video + Text Content

```python
bubble = FlexBubble.create(
    size=FlexBubbleSize.MEGA,
    hero=video_component,
    body=text_content,
    footer=action_buttons
)
```

### Video Carousel

```python
# Note: Videos cannot be in carousel containers
# Use multiple separate video messages instead

messages = [
    FlexMessage.create(altText="Video 1", contents=video_bubble_1),
    FlexMessage.create(altText="Video 2", contents=video_bubble_2),
    FlexMessage.create(altText="Video 3", contents=video_bubble_3)
]

await client.push_message(user_id, messages)
```

This comprehensive video documentation covers all aspects of integrating videos into FlexMessages, from basic requirements to advanced use cases and best practices.
