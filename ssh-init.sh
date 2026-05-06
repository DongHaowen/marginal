source ./tidb.env
eval "$(ssh-agent -s)"
ssh-add "$KEY_SAVE_PATH"
ssh-add -l
