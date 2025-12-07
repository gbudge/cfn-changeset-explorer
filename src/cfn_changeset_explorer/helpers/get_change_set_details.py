#!/usr/bin/env python3

import os
import glob
import json
import boto3

def get_change_set_details(
    stack_name: str,
    change_set_name: str,
    include_nested: bool = True,
    region: str = "ap-southeast-2",
    mocked_json_path: str = "",
):
    """
    Recursively describes a CloudFormation change set, including nested stacks.
    Can use mocked local JSON files instead of calling AWS APIs.
    """
    
    response = None

    if mocked_json_path:
        parsed_stack_name = stack_name.split('/')[1] if stack_name.startswith('arn:') else stack_name
        parsed_change_set_name = change_set_name.split('/')[1] if change_set_name.startswith('arn:') else change_set_name

        filename = f"stack.{parsed_stack_name}.changeset.{parsed_change_set_name}.json"
        filepaths = glob.glob(os.path.join(mocked_json_path, '**', filename), recursive=True)

        if not filepaths:
            print(f"Error: Mock file not found for stack '{stack_name}' and change set '{change_set_name}'. Searched for '{filename}' in '{mocked_json_path}'.")
            return None

        try:
            with open(filepaths[0], 'r', encoding='utf-8') as f:
                response = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading or parsing mock file '{filepaths[0]}': {e}")
            return None
    else:
        # Create Boto3 CloudFormation client
        session = boto3.Session(region_name=region)
        cfn_client = session.client("cloudformation")

        try:
            response = cfn_client.describe_change_set(
                ChangeSetName=change_set_name, StackName=stack_name
            )
        except cfn_client.exceptions.ChangeSetNotFoundException:
            print(f"Error: Change set '{change_set_name}' not found for stack '{stack_name}'.")
            return None
        except RuntimeError as e:
            print(f"An unexpected error occurred: {e}")
            return None

    if not response:
        return None

    if include_nested and response.get("Changes"):
        nested_changes_list = []
        for change in response.get("Changes", []):
            resource_change = change.get("ResourceChange", {})
            if resource_change.get("ResourceType") == "AWS::CloudFormation::Stack":
                nested_stack_id = resource_change.get("PhysicalResourceId")
                nested_change_set_id = resource_change.get("ChangeSetId")
                logical_id = resource_change.get("LogicalResourceId")

                if nested_stack_id and nested_change_set_id:
                    nested_changes = get_change_set_details(
                        nested_stack_id,
                        nested_change_set_id,
                        include_nested,
                        region,
                        mocked_json_path
                    )
                    if nested_changes:
                        nested_changes_list.append({
                            "LogicalResourceId": logical_id,
                            "ChangeSet": nested_changes
                        })
        if nested_changes_list:
            response["NestedChanges"] = nested_changes_list

    return response
