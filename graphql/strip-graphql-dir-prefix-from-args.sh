#!/usr/bin/env bash
# Transform file paths passed as arguments by removing the leading 'graphql/'.
# Prints each rebased path followed by a NUL byte so callers can safely pass
# them as arguments using `xargs -0` (handles spaces, newlines, and quotes).
set -euo pipefail

removable_prefix='graphql/'

# Iterate over all arguments
for arg in "$@"; do
  case "$arg" in
    # Does the argument start with the given removable prefix?
    ${removable_prefix}*)
      # Remove the shortest match of $removable_prefix from the start of $arg
      printf '%s\0' "${arg#"$removable_prefix"}"
      ;;
  esac
done
