# Spliit Client

[![PyPI version](https://badge.fury.io/py/spliit_client.svg)](https://badge.fury.io/py/spliit_client)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Spliit Client** is a professional, well-documented Python client for the [Spliit API](https://spliit.app), enabling seamless group expense sharing and management. This package is released under the permissive [MIT License](LICENSE), making it suitable for both personal and commercial projects.

> **Note:** This project is a fix and improvement on the work done in [makp0/spliit-api-client](https://github.com/makp0/spliit-api-client), with enhanced structure, documentation, testing, and packaging.

---

## Features

- Effortlessly create and manage expense groups
- Add and manage participants
- Add, retrieve, and delete expenses
- Multiple split modes: evenly, by shares, by percentage, by amount
- Comprehensive, categorized expense types
- Command-line interface (CLI) for quick operations
- Type hints and robust error handling
- Professional documentation and examples

---

## Installation

### From PyPI (Recommended)

```bash
pip install spliit_client
```

### From Source

```bash
git clone https://github.com/abg0148/spliit_client.git
cd spliit_client
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/abg0148/spliit_client.git
cd spliit_client
pip install -e ".[dev]"
```

---

## Quick Start

### Basic Usage

```python
from spliit_client import Spliit, SplitMode

# Create a new group
group = Spliit.create_group(
    name="Trip to Paris",
    currency="$",
    participants=[
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"}
    ]
)

# Get participant IDs
participants = group.get_participants()
alice_id = participants["Alice"]

# Add an expense
expense_id = group.add_expense(
    title="Dinner",
    amount=6000,  # Amount in cents ($60.00)
    paid_by=alice_id,
    paid_for=[
        (alice_id, 1),
        (participants["Bob"], 1),
        (participants["Charlie"], 1)
    ],
    split_mode=SplitMode.EVENLY,
    notes="Dinner at a restaurant",
    category=8  # Dining Out
)

# Retrieve all expenses
expenses = group.get_expenses()
for expense in expenses:
    print(f"{expense['title']}: ${expense['amount']/100:.2f}")
```

### Command-Line Interface (CLI)

Spliit Client provides a CLI for common operations:

```bash
# Create a new group
spliit create-group "Trip to Paris" --currency "$" --participants Alice Bob Charlie

# List all available categories
spliit list-categories

# Show version
spliit version
```

---

## API Reference

### Spliit Class

#### Class Methods
- `create_group(name, currency="$", server_url=OFFICIAL_INSTANCE, participants=None)`
  - Create a new group and return a client instance.

#### Instance Methods
- `get_group()` — Get group details
- `get_participants()` — Get all participants with their IDs
- `get_username_id(name)` — Get participant ID by name
- `get_expenses()` — Get all expenses in the group
- `get_expense(expense_id)` — Get details of a specific expense
- `add_expense(...)` — Add a new expense to the group
- `remove_expense(expense_id)` — Remove an expense from the group

### SplitMode Enum
- `SplitMode.EVENLY`: Split the expense evenly among participants
- `SplitMode.BY_SHARES`: Split by number of shares per participant
- `SplitMode.BY_PERCENTAGE`: Split by percentage
- `SplitMode.BY_AMOUNT`: Split by specific amounts

### CATEGORIES Dictionary
A comprehensive dictionary of categorized expense types. See the code for details.

---

## Example: Trip Expense Management

```python
from spliit_client import Spliit, SplitMode

group = Spliit.create_group(
    name="Weekend Trip to Mountains",
    currency="$",
    participants=[
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"},
        {"name": "Diana"}
    ]
)

participants = group.get_participants()
alice_id = participants["Alice"]
bob_id = participants["Bob"]
charlie_id = participants["Charlie"]
diana_id = participants["Diana"]

# Add expenses
group.add_expense(
    title="Gas for the trip",
    amount=8000,  # $80.00
    paid_by=alice_id,
    paid_for=[(alice_id, 1), (bob_id, 1), (charlie_id, 1), (diana_id, 1)],
    split_mode=SplitMode.EVENLY,
    category=31  # Gas/Fuel
)

group.add_expense(
    title="Hotel room",
    amount=20000,  # $200.00
    paid_by=bob_id,
    paid_for=[(alice_id, 1), (bob_id, 1), (charlie_id, 1), (diana_id, 1)],
    split_mode=SplitMode.EVENLY,
    category=32  # Hotel
)

# Get all expenses
all_expenses = group.get_expenses()
print(f"Total expenses: {len(all_expenses)}")
for expense in all_expenses:
    print(f"- {expense['title']}: ${expense['amount']/100:.2f}")
```

---

## Development & Contribution

### Setting Up

```bash
git clone https://github.com/abg0148/spliit_client.git
cd spliit_client
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=spliit_client
```

### Code Quality

```bash
black spliit_client tests
flake8 spliit_client tests
mypy spliit_client
```

### Building and Publishing

```bash
python -m build
# Test upload
python -m twine upload --repository testpypi dist/*
# Production upload
python -m twine upload dist/*
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to your branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software for any purpose, including commercial applications, as long as the original copyright and license notice appear in all copies.

---

## Acknowledgments

- [Spliit](https://spliit.app) for the expense sharing platform
- [makp0/spliit-api-client](https://github.com/makp0/spliit-api-client) for the original implementation
- The Python community for excellent tools and libraries

## Support

If you encounter any issues or have questions:
- Check the [documentation](https://github.com/abg0148/spliit_client#readme)
- Search [existing issues](https://github.com/abg0148/spliit_client/issues)
- Create a [new issue](https://github.com/abg0148/spliit_client/issues/new)

---

> **Note:** This is an unofficial client for the Spliit API. It is not affiliated with or endorsed by Spliit. 