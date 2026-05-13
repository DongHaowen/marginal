import os
import yaml

class Cluster:
    def __init__(self):
        self.tidb_servers: list[dict] = []
        self.tikv_servers: list[dict] = []
        self.pd_servers: list[dict] = []

    def load_topology(self, topology_file: str = "./cluster.yaml") -> dict:
        # 读取集群拓扑配置
        # 解析tidb_servers的IP地址，更新haproxy.cfg中的后端服务器列表
        # 解析tikv_servers和pd_servers的IP地址，但是目前仅用于记录
        if not os.path.exists(topology_file):
            return {}
        with open(topology_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    def generate_haproxy_cfg(self, tidb_servers: list[dict]) -> str:
        # 生成haproxy.cfg内容
        backend_servers = "\n".join(
            f"    server tidb{i+1} {server['host']}:{server['port']} check weight 1"
            for i, server in enumerate(tidb_servers)
        )
        

def load_topology():
    status_file = os.path.join(os.path.dirname(__file__), "status.yaml")
    if not os.path.exists(status_file):
        return {}
    with open(status_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}