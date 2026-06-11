import os

script_dir = os.path.dirname(os.path.abspath(__file__))
control_dir = os.path.dirname(script_dir)
output_dir = os.path.join(control_dir, "bench")
ru_limit_sql = os.path.join(output_dir, "ru_limit.sql")


# CALIBRATE RESOURCE;
DEFAULT_RU_AMOUNT = 34434

DEFAULT_TENANT_LIST = [
    f"tenant_w{i}" for i in range(1, 9)
]

def average_alloc(tenant_list: list[str]) -> dict [str, float]:
    if not tenant_list:
        return {}
    average_ru = DEFAULT_RU_AMOUNT / len(tenant_list)
    return {tenant: average_ru for tenant in tenant_list}

def generate_ru_limit_sql(tenant_list: list[str], output_file: str = ru_limit_sql) -> str:
    alloc = average_alloc(tenant_list)
    lines = []
    for tenant, ru in alloc.items():
        line1 = f"CREATE RESOURCE GROUP {tenant} RU_PER_SEC = {int(ru)};"
        line2 = f"ALTER USER '{tenant}'@'%' RESOURCE GROUP {tenant};"
        lines.append(line1)
        lines.append(line2)
    sql_content = "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sql_content)
    return sql_content


if __name__ == "__main__":
    sql = generate_ru_limit_sql(DEFAULT_TENANT_LIST)