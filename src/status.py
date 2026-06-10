import requests
import json


"""_summary_
该文件用于获取TiDB集群的状态信息,包括CPU使用率、内存使用率、磁盘使用率等.
具体数据的获取方式为通过HTTP请求访问Prometheus的数据接口,获取JSON格式的数据,并进行解析和处理.
具体查询数据采用PromQL语句,查询结果会进行处理和分析,最终返回一个包含TiDB集群状态信息的字典.
需要返回的信息包括各个节点的CPU使用率、内存使用率、磁盘使用率、网络流量.
对应如下PromQL语句
CPU:
curl -G http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
MEM:
curl -G http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=100*(1-node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes)'
DISK:
curl -G http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=rate(node_disk_read_bytes_total[1m])/1024/1024 + rate(node_disk_write_bytes_total[1m])/1024/1024'
"""


def get_cluster_status(servers: list[str]) -> dict[str, dict[str, float]]:
    pass
  
def get_cpu_usage(servers: list[str]) -> dict[str, float]:
    """
    查询指定服务器的CPU使用率
    
    Args:
        servers: 服务器IP地址列表
        
    Returns:
        dict[str, float]: IP地址映射到CPU使用率的字典，数据不存在时值为None
    """
    # Prometheus查询URL
    prometheus_url = "http://127.0.0.1:9090/api/v1/query"
    
    # PromQL查询语句：计算CPU使用率（百分比）
    promql_query = '100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    
    # 初始化结果字典，所有输入的IP都映射到None
    result = {server: None for server in servers}
    
    try:
        # 构建请求参数
        params = {'query': promql_query}
        
        # 发送请求到Prometheus
        response = requests.get(prometheus_url, params=params, timeout=10)
        response.raise_for_status()
        
        # 解析JSON响应
        data = response.json()
        
        # 从响应中提取数据
        if data.get('status') == 'success' and 'result' in data.get('data', {}):
            for item in data['data']['result']:
                # 获取instance字符串（格式：IP:port，例如"10.0.1.3:9100"）
                instance = item.get('metric', {}).get('instance', '')
                
                # 提取IP地址（去掉端口号）
                ip = instance.split(':')[0]
                
                # 如果IP在输入列表中，提取CPU使用率
                if ip in result:
                    # value是一个数组，第二个元素是CPU使用率（字符串格式）
                    cpu_value = item.get('value', [None, None])[1]
                    
                    # 将字符串转换为浮点数
                    if cpu_value is not None:
                        result[ip] = float(cpu_value)
    
    except Exception as e:
        # 发生异常时，返回所有值为None的字典
        print(f"获取CPU使用率失败: {e}")
    
    return result


def get_mem_usage(servers: list[str]) -> dict[str, float]:
    """
    查询指定服务器的内存使用率
    
    Args:
        servers: 服务器IP地址列表
        
    Returns:
        dict[str, float]: IP地址映射到内存使用率的字典，数据不存在时值为None
    """
    # Prometheus查询URL
    prometheus_url = "http://127.0.0.1:9090/api/v1/query"
    
    # PromQL查询语句：计算内存使用率（百分比）
    promql_query = '100*(1-node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes)'
    
    # 初始化结果字典，所有输入的IP都映射到None
    result = {server: None for server in servers}
    
    try:
        # 构建请求参数
        params = {'query': promql_query}
        
        # 发送请求到Prometheus
        response = requests.get(prometheus_url, params=params, timeout=10)
        response.raise_for_status()
        
        # 解析JSON响应
        data = response.json()
        
        # 从响应中提取数据
        if data.get('status') == 'success' and 'result' in data.get('data', {}):
            for item in data['data']['result']:
                # 获取instance字符串（格式：IP:port，例如"10.0.1.3:9100"）
                instance = item.get('metric', {}).get('instance', '')
                
                # 提取IP地址（去掉端口号）
                ip = instance.split(':')[0]
                
                # 如果IP在输入列表中，提取内存使用率
                if ip in result:
                    # value是一个数组，第二个元素是内存使用率（字符串格式）
                    mem_value = item.get('value', [None, None])[1]
                    
                    # 将字符串转换为浮点数
                    if mem_value is not None:
                        result[ip] = float(mem_value)
    
    except Exception as e:
        # 发生异常时，返回所有值为None的字典
        print(f"获取内存使用率失败: {e}")
    
    return result
