## Mock cloudformation describe-change-set 

The files are named using the following pattern:

stack.{StackName}.changeset.{ChangeSetName}.json

Here are the rules for your application:

To find a file from StackName and ChangeSetName:

1. Start with the literal string stack..
2. Append the value of the StackName.
3. Append the literal string .changeset..
4. Append the value of the ChangeSetName.
5. End with the .json extension.

Example:
If StackName is complex-root and ChangeSetName is complex-root-cs, the filename is stack.complex-root.changeset.complex-root-cs.json.

To get StackName and ChangeSetName from a filename:

You can parse the filename using a regular expression or by splitting the string.

Using a regular expression:
The pattern ^stack\.(.+)\.changeset\.(.+)\.json$ will capture the names.
- Group 1: StackName
- Group 2: ChangeSetName

By splitting the string:
1. Remove the stack. prefix and .json suffix.
2. Split the remaining string by .changeset..
3. The first part is the StackName.
4. The second part is the ChangeSetName.
