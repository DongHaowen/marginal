from abc import abstractmethod

from instance import Instance
from tenant import Tenant

class Allocator:
    def __init__(self, servers: list[Instance], tenants: list[Tenant]):
        self.server_map = {server.name: server for server in servers}
        self.tenant_map = {tenant.name: tenant for tenant in tenants}
        
        # dict[resource_type, server_id -> map[tenant_id -> allocated_resource]]
        # 记录预期分配的资源量
        self.alloc_exception = {resource: {} for resource in Instance.RESOURCE_TYPES}
        self._init_alloc()
        
    def _init_alloc(self):
        for resource in Instance.RESOURCE_TYPES:
            for server in self.server_map.values():
                self.alloc_exception[resource][server.name] = {}
    
    def capacity(self, server_id: str):
        # 计算服务器实际使用的资源均值和波动幅度
        server: Instance = self.server_map.get(server_id, None)
        if server is None:
            return None, None
        return server.real_capacity()
    
    def requirement(self, tenant_id: str):
        # 计算租户工作负载实际的资源需求与误差
        tenant: Tenant = self.tenant_map.get(tenant_id, None)
        if tenant is None:
            return None, None
        return tenant.real_require()
    
    @abstractmethod
    def allocate(self) -> dict[str, list[str]]:
        # 
        pass


class SimpleAllocator(Allocator):
    def allocate(self) -> dict[str, list[str]]:
        # 简单的分配算法：将租户平均分配到服务器上
        allocation = {server_id: [] for server_id in self.server_map.keys()}
        tenant_ids = list(self.tenant_map.keys())
        num_servers = len(self.server_map)
        
        for i, tenant_id in enumerate(tenant_ids):
            server_id = list(self.server_map.keys())[i % num_servers]
            allocation[server_id].append(tenant_id)
        
        return allocation

class SkewAllocator(Allocator):
    def allocate(self) -> dict[str, list[str]]:
        # 负载不均衡的分配算法：将所有租户分配到第一个服务器上
        allocation = {server_id: [] for server_id in self.server_map.keys()}
        tenant_ids = list(self.tenant_map.keys())
        
        if tenant_ids:
            first_server_id = list(self.server_map.keys())[0]
            allocation[first_server_id] = tenant_ids
        
        return allocation


    
class MyAllocator(Allocator):
    def allocate(self) -> dict[str, list[str]]:
        pass
    