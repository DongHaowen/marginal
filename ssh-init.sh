# ssh连接指令
source ./tidb.env
eval "$(ssh-agent -s)"
ssh-add "$KEY_SAVE_PATH"
ssh-add -l

# 路由检测指令
sudo haproxy -c -f ./haproxy.cfg