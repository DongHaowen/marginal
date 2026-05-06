# !/bin/bash
NAME_PREFIX="${NAME_PREFIX:-tidb}"
KEY_PAIR_NAME="${KEY_PAIR_NAME:-${NAME_PREFIX}-key}"

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/${KEY_PAIR_NAME}.pem
