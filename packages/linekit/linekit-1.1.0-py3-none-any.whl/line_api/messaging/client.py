"""LINE Messaging API client implementation."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from line_api.core import (
    LineAPIConfig,
    LineMessageError,
    LineRateLimitError,
    LineTimeoutError,
)
from line_api.messaging.models import (
    MulticastMessageRequest,
    PushMessageRequest,
    ReplyMessageRequest,
)

logger = logging.getLogger(__name__)


class LineMessagingClient:
    """
    LINE Messaging API client.

    Provides methods for sending messages via LINE's Messaging API including
    push messages, multicast messages, and reply messages.
    """

    def __init__(self, config: LineAPIConfig) -> None:
        """
        Initialize the messaging client.

        Args:
            config: LINE API configuration

        """
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> LineMessagingClient:
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.config.get_auth_headers(),
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        retry_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the LINE API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            retry_key: Optional retry key for idempotent requests

        Returns:
            Response data

        Raises:
            LineMessageError: If the request fails
            LineRateLimitError: If rate limit is exceeded
            LineTimeoutError: If request times out

        """
        await self._ensure_client()
        url = f"{self.config.api_base_url}/{endpoint}"

        # Prepare headers
        headers: dict[str, str] = {}
        if retry_key:
            headers["X-Line-Retry-Key"] = retry_key

        for attempt in range(self.config.max_retries + 1):
            try:
                if self._client is None:
                    msg = "HTTP client not initialized"
                    raise LineMessageError(msg)

                if method.upper() == "POST":
                    response = await self._client.post(url, json=data, headers=headers)
                else:
                    response = await self._client.request(
                        method, url, json=data, headers=headers
                    )

                # Handle successful responses
                if response.status_code == 200:
                    if self.config.debug:
                        logger.info("Request successful: %s %s", method, endpoint)
                    return response.json() if response.content else {}

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("retry-after", 60))
                    if attempt < self.config.max_retries:
                        if self.config.debug:
                            logger.warning(
                                "Rate limited, retrying in %d seconds (attempt %d/%d)",
                                retry_after,
                                attempt + 1,
                                self.config.max_retries,
                            )
                        await asyncio.sleep(retry_after)
                        continue
                    raise LineRateLimitError(
                        "Rate limit exceeded",
                        retry_after=retry_after,
                    )

                # Handle other errors
                error_data = {}
                try:
                    error_data = response.json()
                except Exception:
                    pass

                error_msg = (
                    f"Request failed: {method} {endpoint} - "
                    f"Status: {response.status_code}"
                )

                if error_data:
                    error_msg += f", Error: {error_data}"

                raise LineMessageError(
                    error_msg,
                    status_code=response.status_code,
                    response_body=response.text,
                )

            except httpx.TimeoutException as e:
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2**attempt)
                    if self.config.debug:
                        logger.warning(
                            "Request timeout, retrying in %.2f seconds (attempt %d/%d)",
                            delay,
                            attempt + 1,
                            self.config.max_retries,
                        )
                    await asyncio.sleep(delay)
                    continue
                raise LineTimeoutError(
                    f"Request timeout after {self.config.max_retries} retries",
                ) from e

            except httpx.RequestError as e:
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2**attempt)
                    if self.config.debug:
                        logger.warning(
                            "Request error: %s, retrying in %.2f seconds (attempt %d/%d)",
                            str(e),
                            delay,
                            attempt + 1,
                            self.config.max_retries,
                        )
                    await asyncio.sleep(delay)
                    continue
                raise LineMessageError(f"Request error: {e}") from e

        # This should never be reached, but just in case
        raise LineMessageError("Max retries exceeded")

    async def push_message(
        self,
        user_id: str,
        messages: list[Any],  # Accept any list of message-like objects
        notification_disabled: bool | None = None,
        custom_aggregation_units: list[str] | None = None,
        retry_key: str | None = None,
    ) -> bool:
        """
        Send push message to a user, group, or room.

        Args:
            user_id: User ID, group ID, or room ID
            messages: List of message objects (max 5)
            notification_disabled: Whether to disable push notifications
            custom_aggregation_units: Custom aggregation unit names (max 1)
            retry_key: Optional retry key for idempotent requests

        Returns:
            True if successful

        Raises:
            LineMessageError: If message sending fails
            LineRateLimitError: If rate limit is exceeded
            LineTimeoutError: If request times out

        """
        if not messages:
            msg = "At least one message is required"
            raise LineMessageError(msg)

        if len(messages) > 5:
            msg = "Maximum 5 messages allowed"
            raise LineMessageError(msg)

        if custom_aggregation_units and len(custom_aggregation_units) > 1:
            msg = "Maximum 1 custom aggregation unit allowed"
            raise LineMessageError(msg)

        request = PushMessageRequest(
            to=user_id,
            messages=messages,
            notificationDisabled=notification_disabled,
            customAggregationUnits=custom_aggregation_units,
        )

        await self._make_request(
            "POST",
            "message/push",
            data=request.model_dump(exclude_none=True),
            retry_key=retry_key,
        )

        if self.config.debug:
            logger.info("Push message sent successfully to: %s", user_id)

        return True

    async def multicast_message(
        self,
        user_ids: list[str],
        messages: list[Any],  # Accept any list of message-like objects
        notification_disabled: bool | None = None,
        custom_aggregation_units: list[str] | None = None,
        retry_key: str | None = None,
    ) -> bool:
        """
        Send multicast message to multiple users.

        Efficiently sends the same message to multiple user IDs. You can't
        send messages to group chats or multi-person chats with this method.

        Rate limit: 200 requests per second

        Args:
            user_ids: List of user IDs (max 500)
            messages: List of message objects (max 5)
            notification_disabled: Whether to disable push notifications
            custom_aggregation_units: Custom aggregation unit names (max 1)
            retry_key: Optional retry key for idempotent requests

        Returns:
            True if successful

        Raises:
            LineMessageError: If message sending fails
            LineRateLimitError: If rate limit is exceeded
            LineTimeoutError: If request times out

        """
        if not user_ids:
            msg = "At least one user ID is required"
            raise LineMessageError(msg)

        if len(user_ids) > 500:
            msg = "Maximum 500 recipients allowed"
            raise LineMessageError(msg)

        if not messages:
            msg = "At least one message is required"
            raise LineMessageError(msg)

        if len(messages) > 5:
            msg = "Maximum 5 messages allowed"
            raise LineMessageError(msg)

        if custom_aggregation_units and len(custom_aggregation_units) > 1:
            msg = "Maximum 1 custom aggregation unit allowed"
            raise LineMessageError(msg)

        request = MulticastMessageRequest(
            to=user_ids,
            messages=messages,
            notificationDisabled=notification_disabled,
            customAggregationUnits=custom_aggregation_units,
        )

        await self._make_request(
            "POST",
            "message/multicast",
            data=request.model_dump(exclude_none=True),
            retry_key=retry_key,
        )

        if self.config.debug:
            logger.info(
                "Multicast message sent successfully to %d users",
                len(user_ids),
            )

        return True

    async def reply_message(
        self,
        reply_token: str,
        messages: list[Any],  # Accept any list of message-like objects
        notification_disabled: bool | None = None,
    ) -> bool:
        """
        Send reply message using reply token from webhook.

        Args:
            reply_token: Reply token from webhook event
            messages: List of message objects (max 5)
            notification_disabled: Whether to disable push notifications

        Returns:
            True if successful

        Raises:
            LineMessageError: If message sending fails
            LineRateLimitError: If rate limit is exceeded
            LineTimeoutError: If request times out

        """
        if not messages:
            msg = "At least one message is required"
            raise LineMessageError(msg)

        if len(messages) > 5:
            msg = "Maximum 5 messages allowed"
            raise LineMessageError(msg)

        request = ReplyMessageRequest(
            replyToken=reply_token,
            messages=messages,
            notificationDisabled=notification_disabled,
        )

        await self._make_request(
            "POST",
            "message/reply",
            data=request.model_dump(exclude_none=True),
        )

        if self.config.debug:
            logger.info("Reply message sent successfully")

        return True
