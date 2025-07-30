#!/usr/bin/env python3
"""
Core client implementation for the Spliit API.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, Any
from urllib.parse import urljoin
from enum import Enum
import requests
import uuid
from datetime import datetime, timezone


class SplitMode(str, Enum):
    """Split modes available in Spliit."""
    EVENLY = "EVENLY"
    BY_SHARES = "BY_SHARES"
    BY_PERCENTAGE = "BY_PERCENTAGE"
    BY_AMOUNT = "BY_AMOUNT"


OFFICIAL_INSTANCE = "https://spliit.app"

CATEGORIES = {
    "Uncategorized": {
        "General": 0,
        "Payment": 1
    },
    "Entertainment": {
        "Entertainment": 2,
        "Games": 3,
        "Movies": 4,
        "Music": 5,
        "Sports": 6
    },
    "Food and Drink": {
        "Food and Drink": 7,
        "Dining Out": 8,
        "Groceries": 9,
        "Liquor": 10
    },
    "Home": {
        "Home": 11,
        "Electronics": 12,
        "Furniture": 13,
        "Household Supplies": 14,
        "Maintenance": 15,
        "Mortgage": 16,
        "Pets": 17,
        "Rent": 18,
        "Services": 19
    },
    "Life": {
        "Childcare": 20,
        "Clothing": 21,
        "Education": 22,
        "Gifts": 23,
        "Insurance": 24,
        "Medical Expenses": 25,
        "Taxes": 26
    },
    "Transportation": {
        "Transportation": 27,
        "Bicycle": 28,
        "Bus/Train": 29,
        "Car": 30,
        "Gas/Fuel": 31,
        "Hotel": 32,
        "Parking": 33,
        "Plane": 34,
        "Taxi": 35
    },
    "Utilities": {
        "Utilities": 36,
        "Cleaning": 37,
        "Electricity": 38,
        "Heat/Gas": 39,
        "Trash": 40,
        "TV/Phone/Internet": 41,
        "Water": 42
    }
}


def format_expense_payload(
        group_id: str,
        title: str,
        amount: int,
        paid_by: str,
        paid_for: List[Tuple[str, int]],
        split_mode: SplitMode,
        expense_date: datetime,
        notes: str = "",
        category: int = 0,
) -> Dict[str, Any]:
    """Format the expense payload according to the API requirements."""
    # Convert paid_for to the expected format
    formatted_paid_for = []

    for participant_id, shares in paid_for:
        formatted_paid_for.append({
            "participant": participant_id,
            "shares": shares
        })

    # Format the expense date
    formatted_date = expense_date.strftime('%Y-%m-%dT%H:%M:%S.') + f"{expense_date.microsecond // 10000:03d}Z"

    # Create the expense form values
    expense_form_values = {
        "expenseDate": formatted_date,
        "title": title,
        "category": category,
        "amount": amount,
        "paidBy": paid_by,
        "paidFor": formatted_paid_for,
        "splitMode": split_mode.value,
        "saveDefaultSplittingOptions": False,
        "isReimbursement": False,
        "documents": [],
        "notes": notes
    }

    return {
        "0": {
            "json": {
                "groupId": group_id,
                "expenseFormValues": expense_form_values,
                "participantId": "None"
            },
            "meta": {
                "values": {
                    "expenseFormValues.expenseDate": ["Date"]
                }
            }
        }
    }


def get_current_timestamp() -> str:
    """Get current timestamp in Spliit format."""
    now = datetime.now(timezone.utc)
    return now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 10000:03d}Z"


@dataclass
class Spliit:
    """Client for interacting with the Spliit API."""

    group_id: str
    server_url: str = OFFICIAL_INSTANCE

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        return urljoin(self.server_url, "/api/trpc")

    @classmethod
    def create_group(cls, name: str, currency: str = "$", server_url: str = OFFICIAL_INSTANCE,
                     participants: List[Dict[str, str]] = None) -> "Spliit":
        """Create a new group and return a client instance for it."""
        if participants is None:
            participants = [{"name": "You"}]

        # Add UUIDs to participants
        for participant in participants:
            participant["id"] = str(uuid.uuid4())

        json_data = {
            "0": {
                "json": {
                    "groupFormValues": {
                        "name": name,
                        "currency": currency,
                        "information": "",
                        "participants": participants
                    }
                }
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        url = f"{urljoin(server_url, '/api/trpc/groups.create')}"

        response = requests.post(
            url,
            json=json_data,
            headers=headers,
            params={"batch": "1"}
        )

        response.raise_for_status()
        group_id = response.json()[0]["result"]["data"]["json"]["groupId"]
        return cls(group_id=group_id, server_url=server_url)

    def get_group(self) -> Dict:
        """Get group details."""
        params_input = {
            "0": {"json": {"groupId": self.group_id}},
            "1": {"json": {"groupId": self.group_id}}
        }

        params = {
            "batch": "1",
            "input": json.dumps(params_input)
        }

        response = requests.get(
            f"{self.base_url}/groups.get,groups.getDetails",
            params=params
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]["group"]

    def get_username_id(self, name: str) -> Optional[str]:
        """Get participant ID by name."""
        group = self.get_group()
        for participant in group["participants"]:
            if name == participant["name"]:
                return participant["id"]
        return None

    def get_participants(self) -> Dict[str, str]:
        """Get all participants with their IDs."""
        group = self.get_group()
        return {
            participant["name"]: participant["id"]
            for participant in group["participants"]
        }

    def get_expenses(self) -> List[Dict]:
        """Get all expenses in the group."""
        params_input = {
            "0": {"json": {"groupId": self.group_id}}
        }

        params = {
            "batch": "1",
            "input": json.dumps(params_input)
        }

        response = requests.get(
            f"{self.base_url}/groups.expenses.list",
            params=params
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]["expenses"]

    def get_expense(self, expense_id: str) -> Dict:
        """
        Get details of a specific expense.

        Args:
            expense_id: The ID of the expense to retrieve

        Returns:
            Dict containing the expense details
        """
        params_input = {
            "0": {
                "json": {
                    "groupId": self.group_id,
                    "expenseId": expense_id
                }
            }
        }

        params = {
            "batch": "1",
            "input": json.dumps(params_input)
        }

        response = requests.get(
            f"{self.base_url}/groups.expenses.get",
            params=params
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]["expense"]

    def add_expense(
            self,
            title: str,
            amount: int,
            paid_by: str,
            paid_for: List[Tuple[str, int]],
            split_mode: SplitMode = SplitMode.EVENLY,
            expense_date: Optional[datetime] = None,
            notes: str = "",
            category: int = 0
    ) -> str:
        """
        Add a new expense to the group.

        Args:
            title: Title of the expense
            amount: Amount in cents (e.g., 1350 for $13.50)
            paid_by: ID of the participant who paid
            paid_for: List of (participant_id, shares) tuples
            split_mode: How to split the expense (EVENLY, BY_SHARES, BY_PERCENTAGE, BY_AMOUNT)
            expense_date: Optional datetime for the expense (defaults to current UTC time)
            notes: Optional notes for the expense
            category: Expense category ID

        Returns:
            The expense ID as a string
        """
        if expense_date is None:
            expense_date = datetime.now(timezone.utc)

        params = {"batch": "1"}

        json_data = format_expense_payload(
            self.group_id,
            title,
            amount,
            paid_by,
            paid_for,
            split_mode,
            expense_date,
            notes,
            category
        )

        response = requests.post(
            f"{self.base_url}/groups.expenses.create",
            params=params,
            json=json_data
        )

        response.raise_for_status()
        return response.content.decode()

    def remove_expense(self, expense_id: str) -> Dict:
        """
        Remove an expense from the group.

        Args:
            expense_id: The ID of the expense to remove

        Returns:
            Dict containing the response data
        """
        params = {"batch": "1"}
        json_data = {
            "0": {
                "json": {
                    "groupId": self.group_id,
                    "expenseId": expense_id
                }
            }
        }

        response = requests.post(
            f"{self.base_url}/groups.expenses.delete",
            params=params,
            json=json_data
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"] 