from instance import Instance
from tenant import Tenant

class Allocator:
    def __init__(self, servers: list[Instance], tenants: list[Tenant]):
        self.servers = servers
        self.tenants = tenants
        
        # dict[resource_type, server_id -> map[tenant_id -> allocated_resource]]
        # 记录预期分配的资源量
        self.alloc_exception = {resource: {} for resource in Instance.RESOURCE_TYPES}
        self._init_alloc()
        
    def _init_alloc(self):
        for resource in Instance.RESOURCE_TYPES:
            for server in self.servers:
                self.alloc_exception[resource][server.name] = {}
    
    def capacity(self, server_id: str):
        # 计算服务器实际使用的资源均值和波动幅度
        real_usage = None
        real_flunc = None 
        return real_usage, real_flunc
    
    def requirement(self, tenant_id: str) -> dict[str, dict[str, float]]:
        # 计算租户工作负载实际的资源需求与误差
        real_req = None
        real_err = None 
        return real_req, real_err
    
    def allocate(self) -> dict[str, list[str]]:
        # 
        pass
    
    