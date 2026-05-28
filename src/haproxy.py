import os
import yaml
import csv
from instance import Instance

class HAProxy:
    def __init__(self, name: str = "cluster"):
        self.name: str = name
        self.instances: dict[str, Instance] = {}
        self.tidb_servers: list[str] = []
        self.tikv_servers: list[str] = []
        self.pd_servers: list[str] = []
    
    def load_instances(self, mapping_file: str = "./cluster.mapping") -> None:
        # 读取集群实例映射配置
        # 将实例名称、类型和IP地址加载到self.instances字典中
        if not os.path.exists(mapping_file):
            return
        
        mapping: dict[str, dict[str, str]] = {}
        with open(mapping_file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                # cluster.mapping 列格式:
                # role, index, instance_type, placeholder_ip, private_ip,
                # public_ip, instance_id, instance_name
                name = (row.get("instance_name") or "").strip()
                if not name:
                    role = (row.get("role") or "").strip()
                    index = (row.get("index") or "").strip()
                    if role and index:
                        name = f"{role}-{index}"
                if not name:
                    continue

                typo = (row.get("instance_type") or "").strip()
                ip = (row.get("private_ip") or "").strip() or (row.get("public_ip") or "").strip()

                mapping[name] = {
                    "type": typo,
                    "ip": ip,
                }

        self.instances.clear()
        for name, info in mapping.items():
            typo = info.get("type", "")
            ip = info.get("ip", "")
            self.instances[name] = Instance(name, typo, ip)
    
    def load_topology(self, topology_file: str = "./cluster.yaml") -> dict:
        # 读取集群拓扑配置
        # 返回一个包含各个组件服务器列表的字典
        if not os.path.exists(topology_file):
            return {}
        with open(topology_file, "r", encoding="utf-8") as f:
            topology = yaml.safe_load(f) or {}
        # 读取其中tidb_servers、tikv_servers、pd_servers等组件的服务器列表
        # 并将对应的IP地址添加到self.tidb_servers、self.tikv_servers、self.pd_servers等列表中
        self.tidb_servers = [server.get("host", "") for server in topology.get("tidb_servers", [])]
        self.tikv_servers = [server.get("host", "") for server in topology.get("tikv_servers", [])]
        self.pd_servers = [server.get("host", "") for server in topology.get("pd_servers", [])]
        
        
    
    def init_haproxy_cfg(self, haproxy_cfg: str = "./haproxy.cfg") -> str:
        # 生成默认的HAProxy配置内容
        # 根据tidb_servers列表中的服务器信息，生成HAProxy的后端服务器配置
        backend_servers = "\n".join([f"    server tidb_{i} {ip}:4000 check" for i, ip in enumerate(self.tidb_servers)])
        haproxy_template = f"""
global
    log /dev/log local0
    log /dev/log local1 notice

    daemon
    maxconn 20000

    stats socket /var/lib/haproxy/stats mode 600 level admin

defaults
    log global
    mode tcp

    option tcplog
    option dontlognull

    timeout connect 5s
    timeout client  1h
    timeout server  1h

    retries 3

frontend tidb_frontend
    bind *:4000
    default_backend tidb_backend

backend tidb_backend
{backend_servers}
"""
        with open(haproxy_cfg, "w", encoding="utf-8") as f:
            f.write(haproxy_template)
        return haproxy_template
    
    def init_cluster(self, root_path: str = "./") -> None:
        # 初始化集群状态
        # 读取mapping文件和topology文件，加载实例信息和拓扑结构
        # 生成HAProxy配置文件
        self.load_instances(os.path.join(root_path, f"{self.name}.mapping"))
        self.load_topology(os.path.join(root_path, f"{self.name}.yaml"))
        self.init_haproxy_cfg(os.path.join(root_path, "haproxy.cfg"))
    
    
    def add_frontend(self, frontend_name: str, bind_port: int, backend_name: str) -> None:
        # 添加一个新的前端配置
        # 在haproxy.cfg中添加一个新的frontend配置，绑定指定的端口，并指定默认的backend
        pass
    
    def add_backend(self, backend_name: str, servers: list[tuple[str, int]]) -> None:
        # 添加一个新的后端配置
        # 在haproxy.cfg中添加一个新的backend配置，包含指定的服务器列表（IP和端口）
        pass


if __name__ == "__main__":
    haproxy = HAProxy()
    haproxy.init_cluster()