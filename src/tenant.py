import csv

class Tenant:
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        
    def real_require(self) -> tuple[dict[str, float], dict[str, float]]:
        # 读取Tenant的监控数据，计算实际需求的均值和误差
        real_req = None
        real_err = None
        return real_req, real_err
        