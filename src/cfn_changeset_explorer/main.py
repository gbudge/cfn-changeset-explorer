#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CloudFormation Change Set Explorer v1.0.0
# Visualise AWS CloudFormation change sets in various formats.
#
# Written by Gareth Budge
#

from argparse import Namespace

from .helpers.formatters import (
    format_pretty,
    format_ascii_tree,
    format_aws_text,
    format_json,
    format_yaml,
    format_markdown,
    format_mermaid,
)
from .helpers.parse_args import parse_args
from .helpers.get_change_set_details import get_change_set_details

FORMATTERS = {
    "pretty": format_pretty,
    "ascii-tree": format_ascii_tree,
    "aws-text": format_aws_text,
    "json": format_json,
    "yaml": format_yaml,
    "markdown": format_markdown,
    "mermaid": format_mermaid,
}

def main():
    #
    # Parse command-line arguments
    #
    args: Namespace
    try:
        args = parse_args()
    except RuntimeError as e:
        print(f"Error parsing arguments: {e}")
        return 1

    #
    # Get change set details
    #
    changes = get_change_set_details(
        args.stack_name, args.change_set_name, not args.no_nested, args.region, args.mocked_json_path
    )
    if not changes:
        return 0

    #
    # Determine the formatter to use and then execute it to display the changes
    #
    try:
        formatter = FORMATTERS.get(args.output, format_pretty)
        formatter(changes)
    except RuntimeError as e:
        print(f"Error formatting output: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
    