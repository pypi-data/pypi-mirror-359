"""
Test URI Actions after documentation fix.

Tests that verify:
1. FlexUriAction can be imported correctly
2. URIAction alias works
3. Both direct constructor and create method work
4. Actions work properly in components
"""

from line_api.flex_messages import (
    FlexButton,
    FlexMessageAction,
    FlexPostbackAction,
    FlexUriAction,
    MessageAction,
    PostbackAction,
    URIAction,
)


class TestURIActions:
    """Test URI action functionality after documentation fix."""

    def test_flexuriaction_import(self) -> None:
        """Test importing FlexUriAction directly."""
        action = FlexUriAction(
            uri="https://example.com",
            label="Visit Website",
        )
        assert action.uri == "https://example.com"
        assert action.label == "Visit Website"
        assert action.type == "uri"

    def test_flexuriaction_create_method(self) -> None:
        """Test FlexUriAction.create() method."""
        action = FlexUriAction.create(
            uri="https://example.com/page",
            label="Visit Page",
        )
        assert action.uri == "https://example.com/page"
        assert action.label == "Visit Page"
        assert action.type == "uri"

    def test_uriaction_alias(self) -> None:
        """Test importing URIAction alias."""
        action = URIAction(
            uri="https://example.com",
            label="Visit Website",
        )
        assert action.uri == "https://example.com"
        assert action.label == "Visit Website"
        assert action.type == "uri"

    def test_uriaction_alias_create_method(self) -> None:
        """Test URIAction.create() method."""
        action = URIAction.create(
            uri="https://example.com/page",
            label="Visit Page",
        )
        assert action.uri == "https://example.com/page"
        assert action.label == "Visit Page"
        assert action.type == "uri"

    def test_aliases_are_same_class(self) -> None:
        """Test that FlexUriAction and URIAction are the same class."""
        assert FlexUriAction is URIAction

    def test_with_optional_parameters(self) -> None:
        """Test with optional parameters."""
        action = FlexUriAction.create(
            uri="https://example.com",
            label="Visit Website",
            alt_uri_desktop="https://desktop.example.com",
        )
        assert action.uri == "https://example.com"
        assert action.label == "Visit Website"
        assert action.alt_uri_desktop == "https://desktop.example.com"

    def test_in_flex_button(self) -> None:
        """Test using URI action in a FlexButton."""
        action = FlexUriAction.create(
            uri="https://example.com",
            label="Click Me",
        )

        button = FlexButton.create(action=action)
        assert button.action == action
        assert isinstance(button.action, FlexUriAction)

    def test_all_action_aliases(self) -> None:
        """Test all action type aliases."""
        # URI Action
        uri_action = URIAction.create(
            uri="https://example.com",
            label="Visit",
        )
        assert isinstance(uri_action, FlexUriAction)

        # Message Action
        message_action = MessageAction.create(
            text="Hello",
            label="Say Hello",
        )
        assert isinstance(message_action, FlexMessageAction)

        # Postback Action
        postback_action = PostbackAction.create(
            data="action_data",
            label="Submit",
        )
        assert isinstance(postback_action, FlexPostbackAction)

    def test_create_methods_for_all_actions(self) -> None:
        """Test create methods for all action types."""
        # FlexUriAction
        uri_action = FlexUriAction.create(
            uri="https://example.com",
            label="Visit",
        )
        assert uri_action.type == "uri"

        # FlexMessageAction
        message_action = FlexMessageAction.create(
            text="Hello World",
            label="Say Hello",
        )
        assert message_action.type == "message"

        # FlexPostbackAction
        postback_action = FlexPostbackAction.create(
            data="user_clicked",
            label="Click Me",
            display_text="User clicked the button",
        )
        assert postback_action.type == "postback"
        assert postback_action.display_text == "User clicked the button"

    def test_action_serialization(self) -> None:
        """Test that actions serialize correctly."""
        action = FlexUriAction.create(
            uri="https://example.com",
            label="Visit Website",
            alt_uri_desktop="https://desktop.example.com",
        )

        # Default serialization uses Python field names
        action_dict = action.model_dump()
        expected_python = {
            "type": "uri",
            "label": "Visit Website",
            "uri": "https://example.com",
            "alt_uri_desktop": "https://desktop.example.com",
        }
        assert action_dict == expected_python

        # Serialization with by_alias=True uses JSON field names (LINE API format)
        action_dict_alias = action.model_dump(by_alias=True)
        expected_line_api = {
            "type": "uri",
            "label": "Visit Website",
            "uri": "https://example.com",
            "altUriDesktop": "https://desktop.example.com",
        }
        assert action_dict_alias == expected_line_api

    def test_action_in_different_components(self) -> None:
        """Test actions work in different components that support them."""
        action = FlexUriAction.create(
            uri="https://example.com",
            label="Test Action",
        )

        # In button
        button = FlexButton.create(action=action)
        assert button.action == action

        # Actions can also be used in Image and Video components
        # but we'll test just the basic functionality here
        assert action.uri == "https://example.com"
        assert action.label == "Test Action"
