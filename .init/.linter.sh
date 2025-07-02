#!/bin/bash
cd /home/kavia/workspace/code-generation/bookexchange-hub-118396-118405/bookswap_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

