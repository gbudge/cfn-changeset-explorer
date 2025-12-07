#!/usr/bin/env bash
#
# Demo script to run the complex nesting example
#

# get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#
# default (pretty) output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"

#
# ascii-tree output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --output ascii-tree \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"

#
# aws-text output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --output aws-text \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"

#
# json output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --output json \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"

#
# yaml output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --output yaml \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"

#
# markdown output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --output markdown \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"

#
# mermaid output
#
"$SCRIPT_DIR"/cfn_changeset_explorer.sh \
    --output mermaid \
    --mocked-json tests/fixtures/aws-cli/describe-change-set/complex-nesting/ \
    --stack-name complex-root \
    --cs-name complex-root-cs \
    "$@"
