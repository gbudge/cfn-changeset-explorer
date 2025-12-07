#!/usr/bin/env python3

import os
import argparse

def parse_args() -> argparse.Namespace:
    #
    # Set up the argument parser
    #
    parser = argparse.ArgumentParser(
        description="Visualise AWS CloudFormation change sets in various formats.",
    )
    
    parser.add_argument("--stack-name", metavar="NAME", dest="stack_name", required=True, help="The name or ID of the stack.")
    parser.add_argument("--cs-name", metavar="NAME", dest="change_set_name"  ,required=True, help="The name or ID of the change set.")
    parser.add_argument("--region", default="ap-southeast-2", help="The AWS region (default: ap-southeast-2).")
    parser.add_argument(
        "--output",
        choices=["pretty", "ascii-tree", "aws-text", "json", "yaml", "markdown", "mermaid"],
        default="pretty",
        dest="output",
        metavar="FORMAT",
        help="The output format (default: pretty)"
    )
    parser.add_argument(
        "--no-nested",
        action="store_true",
        help="Disable recursion into nested stacks.",
    )
    parser.add_argument("--mocked-json", metavar="PATH", dest="mocked_json_path", help="Path to a directory with mocked JSON responses.")

    #
    # Parse the arguments
    #
    try:
        args = parser.parse_args()

        # Basic validation
        if not args.stack_name:
            raise argparse.ArgumentError(None, "The --stack-name argument is required.")
        if not args.change_set_name:
            raise argparse.ArgumentError(None, "The --cs-name argument is required.")
        if not args.output:
            raise argparse.ArgumentError(None, "The --output argument is required.")
        
        # Check the output is a valid choice
        valid_outputs = ["pretty", "ascii-tree", "aws-text", "json", "yaml", "markdown", "mermaid"]
        if args.output not in valid_outputs:
            raise argparse.ArgumentError(None, f"Invalid output format '{args.output}'. Valid options are: {', '.join(valid_outputs)}.")

        # Check if mocked_json_path is provided and is a valid directory
        if args.mocked_json_path and not os.path.isdir(args.mocked_json_path):
            raise argparse.ArgumentError(None, f"The path '{args.mocked_json_path}' is not a valid directory.")
    except argparse.ArgumentError as e:
        print(f"Argument parsing error: {e}")
        raise

    return args
