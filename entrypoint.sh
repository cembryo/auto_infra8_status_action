#!/bin/sh -l

echo "Hello"
export token_github=$1
status_result=`python scripts/check_scope.py`

echo "::set-output name=scope_check_output::$status_result"

