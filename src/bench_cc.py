import os

# Get script directory and set output_dir relative to control folder
script_dir = os.path.dirname(os.path.abspath(__file__))
control_dir = os.path.dirname(script_dir)
output_dir = os.path.join(control_dir, "bench")
output_log = os.path.join(output_dir, "tpcc.log")
prepare_sh = os.path.join(output_dir, "tpcc_prepare.sh")
run_sh = os.path.join(output_dir, "tpcc_run.sh")
ddl_sql = os.path.join(output_dir, "tpcc_tenants.sql")

db_params = [10,10,20,50,100]
db_list = [
    {"db": f"db{i+1}", "warehouses": db_params[i]} for i in range(len(db_params))
]

begin_port = 5000
workload_params = [
    1,1,2,2,2,3,4,5
]
workload_list = [
    {"workload": f"w{i+1}", "threads": 50, "time":"3m", "db": f"db{workload_params[i]}", "port": begin_port + i, "warehouses": db_params[workload_params[i]-1]} for i in range(len(workload_params))
]

def generate_prepare_script():
    prepare_threads = 16
    # 函数需要根据db_list生成tpcc_prepare.sh脚本
    # 单条指令同bench.py中的prepare_script中tpcc部分
    # 此处仅需要生成整体的prepare脚本，不需要生成每个数据库的单独脚本
    # 各条指令按照顺序执行，不输出日志
    
    os.makedirs(output_dir, exist_ok=True)
    
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"PREPARE_THREADS={prepare_threads}",
        "",
    ]
    
    for db_info in db_list:
        db_name = db_info["db"]
        warehouses = db_info["warehouses"]
        
        lines.extend([
            f"# Prepare {db_name}",
            (
                f"tiup bench tpcc prepare "
                f"--db \"{db_name}\" --port 4000 --user root --password \"\" "
                f"--warehouses {warehouses} --parts 1"
            ),
            "",
        ])
    
    with open(prepare_sh, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    os.chmod(prepare_sh, 0o755)

def generate_run_script():
    # 函数需要根据db_list生成tpcc_run.sh脚本
    # 脚本格式同bench.py中的run_script中tpcc部分
    # 规则类似于generate_prepare_script
    # 不同之处在于各条指令同时启动，后台执行
    # 同时单条指令根据workload_list中的参数进行生成
    
    os.makedirs(output_dir, exist_ok=True)
    
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
    ]
    
    for workload_info in workload_list:
        workload_name = workload_info["workload"]
        tenant_user = f"tenant_{workload_name}"
        db_name = workload_info["db"]
        port = workload_info["port"]
        threads = workload_info["threads"]
        time_str = workload_info["time"]
        warehouses = workload_info["warehouses"]
        workload_log = os.path.join(output_dir, f"{workload_name}.log")
        
        lines.extend([
            f"# Run {workload_name} on {db_name}",
            (
                f"tiup bench tpcc run "
                f"--db \"{db_name}\" --port {port} --user \"{tenant_user}\" --password \"\" "
                f"--warehouses {warehouses} --time {time_str} --threads {threads} >> \"{workload_log}\" 2>&1 &"
            ),
            "",
        ])
    
    lines.extend([
        "# Wait for all background jobs to complete",
        "wait",
        "",
    ])
    
    with open(run_sh, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    os.chmod(run_sh, 0o755)

def generate_ddl_sqls():
    # 函数需要根据workload_list生成sql文件
    # sql文件包含创建租户、对应数据库授权的DDL语句
    # 租户名称使用workload名称，例如w1对应的租户为w1，当其使用的数据库为db1时，授权语句为GRANT ALL ON db1.* TO 'tenant_w1'@'%';
    os.makedirs(output_dir, exist_ok=True)

    lines = [
        "-- Auto-generated tenant DDL statements",
        "",
    ]

    for workload_info in workload_list:
        workload_name = workload_info["workload"]
        db_name = workload_info["db"]
        tenant_user = f"tenant_{workload_name}"

        lines.extend([
            f"-- {workload_name} uses {db_name}",
            f"CREATE USER IF NOT EXISTS '{tenant_user}'@'%' IDENTIFIED BY '';",
            f"GRANT ALL ON {db_name}.* TO '{tenant_user}'@'%';",
            "",
        ])

    lines.append("FLUSH PRIVILEGES;")

    with open(ddl_sql, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    generate_prepare_script()
    generate_run_script()
    generate_ddl_sqls()