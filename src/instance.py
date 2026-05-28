import csv
import numpy as np
import os

class Instance:
    RESOURCE_TYPES = ["cpu", "memory", "network", "disk"]
    
    DEFAULT_PRICE = 1
    DEFAULT_PERFORMANCE = {
        "cpu": 1,
        "memory": 1,
        "network": 0,
        "disk": 0
    }
    # ROOT_DIR设置为src目录的绝对路径，以便后续读取ec2_price.csv和ec2_performance.csv文件
    ROOT_DIR = os.path.dirname("./")
    # 从csv文件去读取EC2实例的价格和性能数据，并存储在PRICE_TABLE和PERFORMANCE_TABLE中
    PRICE_TABLE = csv.DictReader(open(os.path.join(ROOT_DIR, "ec2_price.csv"), "r", encoding="utf-8"))
    PERFORMANCE_TABLE = csv.DictReader(open(os.path.join(ROOT_DIR, "ec2_performance.csv"), "r", encoding="utf-8"))
    
    def __init__(self, name: str, typo: str, ip: str):
        self.name = name
        self.typo = typo
        self.ip = ip
        
        self.price = self.search_price(typo)
        
        # 性能序列
        # 指标 (CPU, MEM, ...)
        # 单位 (Cores, GB, ...)
        self.performance = self.search_performance(typo)
    
    
    def search_performance(self, typo: str) -> dict:
        for row in self.PERFORMANCE_TABLE:
            if row["instance_type"] == typo:
                return row
        return self.DEFAULT_PERFORMANCE
    
    def search_price(self, typo: str) -> float:
        for row in self.PRICE_TABLE:
            if row["instance_type"] == typo:
                return float(row["price"])
        return self.DEFAULT_PRICE
    
    def to_array(self) -> list:
        return np.array([self.price, self.performance["cpu"], self.performance["memory"], self.performance["network"], self.performance["disk"]])
    
    def real_capacity(self) -> tuple[dict[str, float], dict[str, float]]:
        # 读取Remote Server的监控数据，计算实际使用的资源均值和波动幅度
        real_usage = None
        real_flunc = None
        return real_usage, real_flunc
        
