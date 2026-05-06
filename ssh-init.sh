# !/bin/bash
set -euo pipefail

KEY_PAIR_NAME="${KEY_PAIR_NAME:-${NAME_PREFIX}-key}"

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/${KEY_PAIR_NAME}.pem