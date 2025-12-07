#!/usr/bin/env python3

import re
import json
import yaml

from rich.table import Table
from rich.tree import Tree

from rich.console import Console
from .get_short_action import get_short_action

def _format_pretty_recursive(change_set, tree_node):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("A/M/R")
    table.add_column("Logical ID")
    table.add_column("Physical ID")
    table.add_column("Type")
    table.add_column("Replacement")
    table.add_column("Details")

    nested_stack_changes = []

    for change in change_set.get("Changes", []):
        resource_change = change["ResourceChange"]
    
        # Defer nested stacks to be processed recursively
        if resource_change.get("ResourceType") == "AWS::CloudFormation::Stack" and "NestedChanges" in change_set:
            nested_change = next((nc for nc in change_set["NestedChanges"] if nc["LogicalResourceId"] == resource_change["LogicalResourceId"]), None)
            if nested_change:
                nested_stack_changes.append((resource_change, nested_change))
                continue

        action = get_short_action(resource_change)
        logical_id = resource_change["LogicalResourceId"]
        physical_id = resource_change.get("PhysicalResourceId", "N/A")
        resource_type = resource_change["ResourceType"]
        replacement = str(resource_change.get("Replacement", "N/A"))
        details = ", ".join(
            [
                f"{d.get('Target', {}).get('Attribute', 'N/A')}: {d.get('Evaluation', 'N/A')}"
                for d in resource_change.get("Details", [])
            ]
        )
        table.add_row(action, logical_id, physical_id, resource_type, replacement, details)

    if len(table.rows) > 0:
        tree_node.add(table)

    for resource_change, nested_change in nested_stack_changes:
        nested_change_set = nested_change["ChangeSet"]
        nested_stack_name = nested_change_set['StackName']
        nested_logical_id = nested_change['LogicalResourceId']
        action = get_short_action(resource_change)

        child_node = tree_node.add(f"[bold cyan]Nested Stack:[/bold cyan] {nested_logical_id} ([italic]{nested_stack_name}[/italic]) {action}")
        _format_pretty_recursive(nested_change_set, child_node)

def format_pretty(changes):
    _console = Console()
    stack_name = changes['StackName']
    change_set_name = changes['ChangeSetName']

    tree = Tree(f"[bold cyan]Stack:[/bold cyan] {stack_name}\n[bold cyan]Change Set:[/bold cyan] {change_set_name}")

    _format_pretty_recursive(changes, tree)

    _console.print(tree)

def _format_ascii_tree_recursive(change_set, parent_node):
    nested_stack_changes = change_set.get("NestedChanges", [])

    for change in change_set.get("Changes", []):
        resource_change = change["ResourceChange"]
        action = get_short_action(resource_change)
        logical_id = resource_change["LogicalResourceId"]
        resource_type = resource_change["ResourceType"]

        nested_change_details = None
        if resource_type == "AWS::CloudFormation::Stack":
            nested_change_details = next((nc for nc in nested_stack_changes if nc["LogicalResourceId"] == logical_id), None)

        if nested_change_details:
            nested_set = nested_change_details["ChangeSet"]
            child_node = parent_node.add(f"{action} [green]{logical_id}[/green] ({resource_type})")
            if "Replacement" in resource_change:
                child_node.add(f"Replacement: {resource_change['Replacement']}")
            _format_ascii_tree_recursive(nested_set, child_node)
        else:
            node = parent_node.add(f"{action} [green]{logical_id}[/green] ({resource_type})")
            if "Replacement" in resource_change:
                node.add(f"Replacement: {resource_change['Replacement']}")

def format_ascii_tree(changes):
    _console = Console()
    stack_name = changes['StackName']
    change_set_name = changes['ChangeSetName']
    tree = Tree(f"[bold cyan]Stack:[/bold cyan] {stack_name} ([italic]{change_set_name}[/italic])")
    _format_ascii_tree_recursive(changes, tree)
    _console.print(tree)

def _format_aws_text_recursive(change_set, indent=""):
    print(f"{indent}CHANGESET\t{change_set['ChangeSetId']}\t{change_set['StackId']}")

    nested_stack_changes = change_set.get("NestedChanges", [])

    for change in change_set["Changes"]:
        rc = change["ResourceChange"]

        print(f"{indent}RESOURCECHANGE\t{get_short_action(rc)}\t{rc['LogicalResourceId']}\t{rc['ResourceType']}\t{rc.get('Replacement', 'None')}")
        for detail in rc.get("Details", []):
            target = detail.get("Target", {})
            print(f"{indent}RESOURCETARGET\t{target.get('Attribute')}\t{target.get('Name')}\t{detail.get('Evaluation')}")

        if rc['ResourceType'] == 'AWS::CloudFormation::Stack':
            nested_change_details = next((nc for nc in nested_stack_changes if nc["LogicalResourceId"] == rc['LogicalResourceId']), None)
            if nested_change_details:
                _format_aws_text_recursive(nested_change_details["ChangeSet"], indent + "  ")

def format_aws_text(changes):
    _format_aws_text_recursive(changes)

def format_json(changes):
    print(json.dumps(changes, indent=2, default=str))

def format_yaml(changes):
    print(yaml.dump(changes, default_flow_style=False))

def _format_mermaid_recursive(change_set, stack_id_prefix="stack"):
    stack_name = change_set['StackName']
    safe_stack_name = "".join(filter(str.isalnum, stack_name))
    stack_id = f"{stack_id_prefix}_{safe_stack_name}"

    print(f"  subgraph {stack_id} [\"{stack_name}\"]")

    links = []

    nested_stack_changes = change_set.get("NestedChanges", [])

    for _, change in enumerate(change_set.get("Changes", [])):
        rc = change["ResourceChange"]
        action_str = get_short_action(rc)
        logical_id = rc['LogicalResourceId']
        safe_logical_id = "".join(filter(str.isalnum, logical_id))

        node_id = f"{stack_id}_{safe_logical_id}"

        print(f"    {node_id}[\"{logical_id}<br/>({rc['ResourceType']})<br/>{action_str}\"]")

        if rc['ResourceType'] == 'AWS::CloudFormation::Stack':
            nested_change_details = next((nc for nc in nested_stack_changes if nc["LogicalResourceId"] == logical_id), None)
            if nested_change_details:
                nested_set = nested_change_details["ChangeSet"]
                nested_stack_prefix = f"{stack_id}_{safe_logical_id}"

                # Create links from the parent stack resource to the resources in the nested stack
                for nested_change_item in nested_set["Changes"]:
                    nested_logical_id = nested_change_item["ResourceChange"]["LogicalResourceId"]
                    safe_nested_logical_id = "".join(filter(str.isalnum, nested_logical_id))
                    nested_node_id = f"{nested_stack_prefix}_{''.join(filter(str.isalnum, nested_set['StackName']))}_{safe_nested_logical_id}"
                    links.append(f"    {node_id} --> {nested_node_id}")

    print("  end")

    # Print links after the subgraph definition
    for link in links:
        print(link)

    # Recurse for nested stacks
    for _, nested_change in enumerate(nested_stack_changes):
        nested_set = nested_change["ChangeSet"]
        logical_id = nested_change["LogicalResourceId"]
        safe_logical_id = "".join(filter(str.isalnum, logical_id))
        nested_stack_prefix = f"{stack_id}_{safe_logical_id}"
        _format_mermaid_recursive(nested_set, stack_id_prefix=nested_stack_prefix)

def format_mermaid(changes):
    print("graph LR")
    _format_mermaid_recursive(changes)


def _format_markdown_recursive(change_set, level=2, parent_stack_name=None, root_stack_name=None):
    stack_name = change_set['StackName']
    change_set_name = change_set['ChangeSetName']

    sanitized_stack_name = re.sub(r'[^a-z0-9-]', '', stack_name.lower().replace(' ', '-'))

    if level == 2: # Root stack
        current_stack_header_text = f"## Stack: {stack_name}"
        current_stack_anchor_id = f"stack-{sanitized_stack_name}"
    else: # Nested stack
        current_stack_header_text = f"### Nested Stack: {stack_name}"
        current_stack_anchor_id = f"nested-stack-{sanitized_stack_name}"

    print(current_stack_header_text)
    print("") # Blank line after header

    # Update Change Set Link - This links to the current stack's section
    print(f"- **Change set:** [`{change_set_name}`](#{current_stack_anchor_id})")
    print("") # Blank line after change set details

    if level > 2: # Only print for nested stacks
        if parent_stack_name:
            sanitized_parent_stack_name = re.sub(r'[^a-z0-9-]', '', parent_stack_name.lower().replace(' ', '-'))
            # The parent of a nested stack is also a stack, but could be root or nested itself.
            # A parent of a level 3 stack is a level 2 stack (root).
            # A parent of a level 4 stack is a level 3 stack (nested).
            parent_anchor_prefix = "stack" if (level - 1) == 2 else "nested-stack"
            parent_anchor_id = f"{parent_anchor_prefix}-{sanitized_parent_stack_name}"
            print(f"- **Parent stack:** [{parent_stack_name}](#{parent_anchor_id})")

        if root_stack_name:
            sanitized_root_stack_name = re.sub(r'[^a-z0-9-]', '', root_stack_name.lower().replace(' ', '-'))
            root_anchor_id = f"stack-{sanitized_root_stack_name}" # Root is always a 'stack-' type anchor
            print(f"- **Root stack:** [{root_stack_name}](#{root_anchor_id})")
        print("") # Blank line after parent/root details

    print("| Action | Logical ID | Physical ID | Type | Replacement | Details |")
    print("|---|---|---|---|---|---|")

    nested_stack_changes = [] # Store nested changes to process after current level's table

    for change in change_set["Changes"]:
        rc = change["ResourceChange"]

        details = ", ".join(
            [
                f"{d.get('Target', {}).get('Attribute', 'N/A')}: {d.get('Evaluation', 'N/A')}"
                for d in rc.get("Details", [])
            ]
        )
        print(f"| {get_short_action(rc)} | {rc['LogicalResourceId']} | {rc.get('PhysicalResourceId', 'N/A')} | {rc['ResourceType']} | {rc.get('Replacement', 'None')} | {details} |")

        # If it's a nested stack, also store it for recursive processing later
        if rc.get("ResourceType") == "AWS::CloudFormation::Stack":
            nested_change = next((nc for nc in change_set.get("NestedChanges", []) if nc["LogicalResourceId"] == rc["LogicalResourceId"]), None)
            if nested_change:
                nested_stack_changes.append((rc, nested_change))

    print("") # Empty line after table for better markdown rendering

    # Process nested changes
    for rc, nested_change_details in nested_stack_changes:
        # Pass current stack name as parent and original root
        _format_markdown_recursive(nested_change_details["ChangeSet"], level=level+1, parent_stack_name=stack_name, root_stack_name=root_stack_name or stack_name)

def format_markdown(changes):
    _format_markdown_recursive(changes, level=2, root_stack_name=changes['StackName'])
