#!/usr/bin/env bash
#
# Wraper to execute cfn_changeset_explorer
#
export PYTHONPATH=src

python -m cfn_changeset_explorer.main "$@"
