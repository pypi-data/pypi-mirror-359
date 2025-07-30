#!/usr/bin/env python3
"""
Command-line interface for spliit_client.
"""

import argparse
import sys
from datetime import datetime
from .client import Spliit, SplitMode, CATEGORIES


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spliit Client - A Python client for the Spliit API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new group
  python -m spliit_client create-group "Trip to Paris" --currency "$" --participants Alice Bob Charlie

  # List categories
  python -m spliit_client list-categories

  # Show help for a specific command
  python -m spliit_client create-group --help
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create group command
    create_parser = subparsers.add_parser('create-group', help='Create a new group')
    create_parser.add_argument('name', help='Name of the group')
    create_parser.add_argument('--currency', default='$', help='Currency symbol (default: $)')
    create_parser.add_argument('--participants', nargs='+', default=['You'], 
                              help='List of participant names (default: ["You"])')
    
    # List categories command
    list_categories_parser = subparsers.add_parser('list-categories', help='List all available categories')
    
    # Show version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'create-group':
        participants = [{"name": name} for name in args.participants]
        try:
            group = Spliit.create_group(
                name=args.name,
                currency=args.currency,
                participants=participants
            )
            print(f"✅ Group '{args.name}' created successfully!")
            print(f"Group ID: {group.group_id}")
            print(f"Participants: {', '.join(args.participants)}")
            print(f"Currency: {args.currency}")
        except Exception as e:
            print(f"❌ Error creating group: {e}")
            sys.exit(1)
    
    elif args.command == 'list-categories':
        print("📋 Available Categories:")
        print("=" * 50)
        for category_group, categories in CATEGORIES.items():
            print(f"\n{category_group}:")
            for category_name, category_id in categories.items():
                print(f"  {category_id:2d}: {category_name}")
    
    elif args.command == 'version':
        from . import __version__
        print(f"spliit_client version {__version__}")


if __name__ == "__main__":
    main() 