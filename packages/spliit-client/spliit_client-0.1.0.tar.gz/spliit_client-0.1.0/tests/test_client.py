#!/usr/bin/env python3
"""
Tests for the Spliit client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import json

from spliit_client.client import (
    Spliit,
    SplitMode,
    CATEGORIES,
    format_expense_payload,
    get_current_timestamp,
    OFFICIAL_INSTANCE,
)


class TestSplitMode:
    """Test SplitMode enum."""

    def test_split_mode_values(self):
        """Test that SplitMode has correct values."""
        assert SplitMode.EVENLY == "EVENLY"
        assert SplitMode.BY_SHARES == "BY_SHARES"
        assert SplitMode.BY_PERCENTAGE == "BY_PERCENTAGE"
        assert SplitMode.BY_AMOUNT == "BY_AMOUNT"


class TestCategories:
    """Test CATEGORIES dictionary."""

    def test_categories_structure(self):
        """Test that CATEGORIES has the expected structure."""
        assert isinstance(CATEGORIES, dict)
        assert "Uncategorized" in CATEGORIES
        assert "Food and Drink" in CATEGORIES
        assert "Transportation" in CATEGORIES

    def test_category_ids(self):
        """Test that category IDs are integers."""
        for category_group in CATEGORIES.values():
            for category_id in category_group.values():
                assert isinstance(category_id, int)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_current_timestamp(self):
        """Test get_current_timestamp returns proper format."""
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, str)
        # Should match format: YYYY-MM-DDTHH:MM:SS.mmmZ
        assert "T" in timestamp
        assert timestamp.endswith("Z")

    def test_format_expense_payload(self):
        """Test format_expense_payload creates correct structure."""
        group_id = "test-group-id"
        title = "Test Expense"
        amount = 1000
        paid_by = "user-id-1"
        paid_for = [("user-id-1", 1), ("user-id-2", 1)]
        split_mode = SplitMode.EVENLY
        expense_date = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        notes = "Test notes"
        category = 8

        payload = format_expense_payload(
            group_id, title, amount, paid_by, paid_for, split_mode, expense_date, notes, category
        )

        assert isinstance(payload, dict)
        assert "0" in payload
        assert "json" in payload["0"]
        assert "groupId" in payload["0"]["json"]
        assert payload["0"]["json"]["groupId"] == group_id

        expense_form = payload["0"]["json"]["expenseFormValues"]
        assert expense_form["title"] == title
        assert expense_form["amount"] == amount
        assert expense_form["paidBy"] == paid_by
        assert expense_form["splitMode"] == split_mode.value
        assert expense_form["notes"] == notes
        assert expense_form["category"] == category


class TestSpliitClient:
    """Test Spliit client class."""

    def test_client_initialization(self):
        """Test Spliit client initialization."""
        group_id = "test-group-id"
        client = Spliit(group_id)
        assert client.group_id == group_id
        assert client.server_url == OFFICIAL_INSTANCE

    def test_client_initialization_custom_server(self):
        """Test Spliit client initialization with custom server."""
        group_id = "test-group-id"
        custom_server = "https://custom.spliit.app"
        client = Spliit(group_id, server_url=custom_server)
        assert client.group_id == group_id
        assert client.server_url == custom_server

    def test_base_url_property(self):
        """Test base_url property."""
        client = Spliit("test-group-id")
        expected_url = f"{OFFICIAL_INSTANCE}/api/trpc"
        assert client.base_url == expected_url

    @patch("spliit_client.client.requests.post")
    def test_create_group_success(self, mock_post):
        """Test successful group creation."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "groupId": "new-group-id"
                        }
                    }
                }
            }
        ]
        mock_post.return_value = mock_response

        # Test group creation
        group = Spliit.create_group(
            name="Test Group",
            currency="$",
            participants=[{"name": "Alice"}, {"name": "Bob"}]
        )

        assert isinstance(group, Spliit)
        assert group.group_id == "new-group-id"
        assert group.server_url == OFFICIAL_INSTANCE

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "groups.create" in call_args[0][0]

    @patch("spliit_client.client.requests.post")
    def test_create_group_with_default_participants(self, mock_post):
        """Test group creation with default participants."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "groupId": "new-group-id"
                        }
                    }
                }
            }
        ]
        mock_post.return_value = mock_response

        group = Spliit.create_group("Test Group")
        assert isinstance(group, Spliit)

    @patch("spliit_client.client.requests.post")
    def test_create_group_http_error(self, mock_post):
        """Test group creation with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("Bad Request")
        mock_post.return_value = mock_response

        with pytest.raises(Exception):
            Spliit.create_group("Test Group")

    @patch("spliit_client.client.requests.get")
    def test_get_group_success(self, mock_get):
        """Test successful group retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "group": {
                                "id": "test-group-id",
                                "name": "Test Group",
                                "currency": "$",
                                "participants": [
                                    {"id": "user-1", "name": "Alice"},
                                    {"id": "user-2", "name": "Bob"}
                                ]
                            }
                        }
                    }
                }
            }
        ]
        mock_get.return_value = mock_response

        client = Spliit("test-group-id")
        group_data = client.get_group()

        assert group_data["id"] == "test-group-id"
        assert group_data["name"] == "Test Group"
        assert group_data["currency"] == "$"
        assert len(group_data["participants"]) == 2

    @patch("spliit_client.client.requests.get")
    def test_get_participants(self, mock_get):
        """Test getting participants mapping."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "group": {
                                "participants": [
                                    {"id": "user-1", "name": "Alice"},
                                    {"id": "user-2", "name": "Bob"}
                                ]
                            }
                        }
                    }
                }
            }
        ]
        mock_get.return_value = mock_response

        client = Spliit("test-group-id")
        participants = client.get_participants()

        expected = {"Alice": "user-1", "Bob": "user-2"}
        assert participants == expected

    @patch("spliit_client.client.requests.get")
    def test_get_username_id(self, mock_get):
        """Test getting participant ID by name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "group": {
                                "participants": [
                                    {"id": "user-1", "name": "Alice"},
                                    {"id": "user-2", "name": "Bob"}
                                ]
                            }
                        }
                    }
                }
            }
        ]
        mock_get.return_value = mock_response

        client = Spliit("test-group-id")
        
        # Test existing participant
        alice_id = client.get_username_id("Alice")
        assert alice_id == "user-1"

        # Test non-existing participant
        charlie_id = client.get_username_id("Charlie")
        assert charlie_id is None

    @patch("spliit_client.client.requests.get")
    def test_get_expenses(self, mock_get):
        """Test getting all expenses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "expenses": [
                                {
                                    "id": "expense-1",
                                    "title": "Dinner",
                                    "amount": 5000
                                },
                                {
                                    "id": "expense-2",
                                    "title": "Gas",
                                    "amount": 3000
                                }
                            ]
                        }
                    }
                }
            }
        ]
        mock_get.return_value = mock_response

        client = Spliit("test-group-id")
        expenses = client.get_expenses()

        assert len(expenses) == 2
        assert expenses[0]["title"] == "Dinner"
        assert expenses[0]["amount"] == 5000
        assert expenses[1]["title"] == "Gas"
        assert expenses[1]["amount"] == 3000

    @patch("spliit_client.client.requests.get")
    def test_get_expense(self, mock_get):
        """Test getting a specific expense."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "expense": {
                                "id": "expense-1",
                                "title": "Dinner",
                                "amount": 5000,
                                "paidBy": "user-1"
                            }
                        }
                    }
                }
            }
        ]
        mock_get.return_value = mock_response

        client = Spliit("test-group-id")
        expense = client.get_expense("expense-1")

        assert expense["id"] == "expense-1"
        assert expense["title"] == "Dinner"
        assert expense["amount"] == 5000
        assert expense["paidBy"] == "user-1"

    @patch("spliit_client.client.requests.post")
    def test_add_expense_success(self, mock_post):
        """Test successful expense addition."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content.decode.return_value = "expense-id-123"
        mock_post.return_value = mock_response

        client = Spliit("test-group-id")
        expense_id = client.add_expense(
            title="Dinner",
            amount=5000,
            paid_by="user-1",
            paid_for=[("user-1", 1), ("user-2", 1)],
            split_mode=SplitMode.EVENLY,
            notes="Test dinner",
            category=8
        )

        assert expense_id == "expense-id-123"
        mock_post.assert_called_once()

    @patch("spliit_client.client.requests.post")
    def test_add_expense_with_defaults(self, mock_post):
        """Test expense addition with default values."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content.decode.return_value = "expense-id-123"
        mock_post.return_value = mock_response

        client = Spliit("test-group-id")
        expense_id = client.add_expense(
            title="Dinner",
            amount=5000,
            paid_by="user-1",
            paid_for=[("user-1", 1)]
        )

        assert expense_id == "expense-id-123"

    @patch("spliit_client.client.requests.post")
    def test_remove_expense_success(self, mock_post):
        """Test successful expense removal."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "success": True
                        }
                    }
                }
            }
        ]
        mock_post.return_value = mock_response

        client = Spliit("test-group-id")
        result = client.remove_expense("expense-id-123")

        assert result["success"] is True
        mock_post.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios."""

    @patch("spliit_client.client.requests.get")
    def test_http_error_handling(self, mock_get):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_get.return_value = mock_response

        client = Spliit("test-group-id")
        with pytest.raises(Exception):
            client.get_group()

    def test_invalid_group_id(self):
        """Test client with invalid group ID."""
        client = Spliit("")
        assert client.group_id == ""

    def test_invalid_server_url(self):
        """Test client with invalid server URL."""
        client = Spliit("test-group-id", server_url="invalid-url")
        assert client.server_url == "invalid-url"


class TestIntegration:
    """Integration tests with mocked API."""

    @patch("spliit_client.client.requests.post")
    @patch("spliit_client.client.requests.get")
    def test_full_workflow(self, mock_get, mock_post):
        """Test a complete workflow: create group, add expense, get expenses."""
        # Mock group creation
        create_response = Mock()
        create_response.status_code = 200
        create_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "groupId": "workflow-group-id"
                        }
                    }
                }
            }
        ]

        # Mock group details
        group_response = Mock()
        group_response.status_code = 200
        group_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "group": {
                                "id": "workflow-group-id",
                                "name": "Workflow Test",
                                "participants": [
                                    {"id": "user-1", "name": "Alice"},
                                    {"id": "user-2", "name": "Bob"}
                                ]
                            }
                        }
                    }
                }
            }
        ]

        # Mock expense addition
        expense_response = Mock()
        expense_response.status_code = 200
        expense_response.content.decode.return_value = "workflow-expense-id"

        # Mock expenses list
        expenses_response = Mock()
        expenses_response.status_code = 200
        expenses_response.json.return_value = [
            {
                "result": {
                    "data": {
                        "json": {
                            "expenses": [
                                {
                                    "id": "workflow-expense-id",
                                    "title": "Test Expense",
                                    "amount": 1000
                                }
                            ]
                        }
                    }
                }
            }
        ]

        # Configure mocks
        mock_post.side_effect = [create_response, expense_response]
        mock_get.side_effect = [group_response, expenses_response]

        # Execute workflow
        group = Spliit.create_group("Workflow Test", participants=[{"name": "Alice"}, {"name": "Bob"}])
        participants = group.get_participants()
        
        expense_id = group.add_expense(
            title="Test Expense",
            amount=1000,
            paid_by=participants["Alice"],
            paid_for=[(participants["Alice"], 1), (participants["Bob"], 1)]
        )
        
        expenses = group.get_expenses()

        # Verify results
        assert group.group_id == "workflow-group-id"
        assert len(participants) == 2
        assert expense_id == "workflow-expense-id"
        assert len(expenses) == 1
        assert expenses[0]["title"] == "Test Expense" 