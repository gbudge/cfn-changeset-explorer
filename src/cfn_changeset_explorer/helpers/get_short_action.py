#!/usr/bin/env python3

def get_short_action(resource_change: dict) -> str:
    """Converts a full action string to a single-letter abbreviation, or full word with replacement info."""
    action = resource_change["Action"]
    if action == "Add":
        return "ADD"
    elif action == "Remove":
        return "REMOVE"
    elif action == "Modify":
        if "Replacement" in resource_change and resource_change["Replacement"] in ["True", "Conditional"]:
            return "MODIFY-REPLACE"
        return "MODIFY"
    else:
        # Fallback for unexpected actions or if action is empty
        return action.upper() if action else ""
