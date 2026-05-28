import yaml
from pathlib import Path
from typing import Any

"""_summary_
数据准备的流程:
1. 基于数据库的连接参数设置数据库连接
2. 根据测试类型设置规模参数
3. 基于连接和规模参数生成prepare.sh脚本
4. 根据测试启动时间和持续时间参数生成run.sh脚本
5. 整合prepare.sh和run.sh脚本,生成最终的执行脚本execute.sh

参数的配置如bench/sample.yaml所示
每一组测试均以tenant为单位进行配置
其中name用于标记租户,不起到参数作用
db,port,user,password分别用于数据库连接参数
workload和集合中的参数用于设置测试类型(tpcc,tpch,ch)和规模参数
runtime参数用于设置启动时间和结束时间,可以包含多组(start,end)参数,每组参数表示一次测试的启动时间和结束时间,单位为秒

其中部分参数可以缺省设置，包括如下
数据库连接参数:
- db: 默认为test
- port: 默认为4000
- user: 默认为root
- password: 默认为空字符串
测试规模参数:
- tpcc类型下的warehouses参数默认为1
- tpcc类型下的parts参数默认为1
- tpch类型下的sf参数默认为1
- ch类型下的warehouses参数默认为1
"""


def _tenant_value(tenant: dict[str, Any], key: str, default: Any) -> Any:
	value = tenant.get(key)
	if value is None:
		return default
	return value


def _render_prepare_commands(workload: dict[str, Any]) -> list[str]:
	workload_type = str(workload.get("type", "")).strip().lower()
	lines: list[str] = []

	if workload_type == "tpcc":
		warehouses = int(workload.get("tpcc_warehouses", 1))
		parts = int(workload.get("tpcc_parts", 1))
		lines.extend(
			[
				"# TPC-C data prepare",
				(
					"tiup bench tpcc prepare -h "
					"--db \"$DB\" --port \"$PORT\" --user \"$USER\" --password \"$PASSWORD\" "
					f"--warehouses {warehouses} --parts {parts}"
				),
				"",
			]
		)
	elif workload_type == "tpch":
		sf = int(workload.get("tpch_sf", 1))
		lines.extend(
			[
				"# TPC-H data prepare",
				(
					"tiup bench tpch prepare "
					"--db \"$DB\" --port \"$PORT\" --user \"$USER\" --password \"$PASSWORD\" "
					f"--sf {sf}"
				),
				"",
			]
		)
	elif workload_type == "ch":
		warehouses = int(workload.get("ch_warehouses", 1))
		lines.extend(
			[
				"# CH data prepare",
				(
					"tiup bench ch prepare "
					"--db \"$DB\" --port \"$PORT\" --user \"$USER\" --password \"$PASSWORD\" "
					f"--warehouses {warehouses}"
				),
				"",
			]
		)

	return lines


def _render_run_command(workload: dict[str, Any], duration: int) -> str | None:
	workload_type = str(workload.get("type", "")).strip().lower()

	if workload_type == "tpcc":
		warehouses = int(workload.get("tpcc_warehouses", 1))
		return (
			"tiup bench tpcc run "
			"--db \"$DB\" --port \"$PORT\" --user \"$USER\" --password \"$PASSWORD\" "
			f"--warehouses {warehouses} --time {duration}"
		)

	if workload_type == "tpch":
		sf = int(workload.get("tpch_sf", 1))
		return (
			"tiup bench tpch run -h "
			"--db \"$DB\" --port \"$PORT\" --user \"$USER\" --password \"$PASSWORD\" "
			f"--sf {sf} --time {duration}"
		)

	if workload_type == "ch":
		warehouses = int(workload.get("ch_warehouses", 1))
		return (
			"tiup bench ch run -h "
			"--db \"$DB\" --port \"$PORT\" --user \"$USER\" --password \"$PASSWORD\" "
			f"--warehouses {warehouses} --time {duration}"
		)

	return None


def generate_prepare_script(tenant: dict[str, Any], output_path: str) -> Path:
	tenant_name = str(tenant.get("name", "tenant")).strip() or "tenant"
	db = str(_tenant_value(tenant, "db", _tenant_value(tenant, "database", "test")))
	port = int(_tenant_value(tenant, "port", 4000))
	user = str(_tenant_value(tenant, "user", "root"))
	password = str(_tenant_value(tenant, "password", ""))
	workloads = tenant.get("workload", []) or []

	lines = [
		"#!/usr/bin/env bash",
		"set -euo pipefail",
		"",
		f'echo "[${{0##*/}}] prepare tenant {tenant_name} start"',
		f"DB=\"{db}\"",
		f"PORT={port}",
		f"USER=\"{user}\"",
		f"PASSWORD=\"{password}\"",
		"",
	]

	for workload in workloads:
		lines.append(f'echo "[${{0##*/}}] tenant {tenant_name} prepare workload: {workload.get("type", "unknown")}"')
		lines.extend(_render_prepare_commands(workload))

	lines.append(f'echo "[${{0##*/}}] prepare tenant {tenant_name} done"')
	lines.append("")

	if lines[-1] != "":
		lines.append("")

	out_dir = Path(output_path)
	out_dir.mkdir(parents=True, exist_ok=True)
	script_path = out_dir / f"{tenant_name}_prepare.sh"
	script_path.write_text("\n".join(lines), encoding="utf-8")
	script_path.chmod(0o755)
	return script_path


def generate_run_script(tenant: dict[str, Any], output_path: str) -> Path:
	tenant_name = str(tenant.get("name", "tenant")).strip() or "tenant"
	db = str(_tenant_value(tenant, "db", _tenant_value(tenant, "database", "test")))
	port = int(_tenant_value(tenant, "port", 4000))
	user = str(_tenant_value(tenant, "user", "root"))
	password = str(_tenant_value(tenant, "password", ""))
	workloads = tenant.get("workload", []) or []
	runtimes = tenant.get("runtime", []) or []

	lines = [
		"#!/usr/bin/env bash",
		"set -euo pipefail",
		"",
		f"DB=\"{db}\"",
		f"PORT={port}",
		f"USER=\"{user}\"",
		f"PASSWORD=\"{password}\"",
		"",
		"current_time=0",
		"",
	]

	for idx, runtime in enumerate(runtimes, start=1):
		start = int(runtime.get("start", 0))
		end = int(runtime.get("end", start))
		duration = end - start

		if duration <= 0:
			continue

		lines.extend(
			[
				f"# Runtime window {idx}: [{start}, {end}]",
				f"if (( {start} > current_time )); then sleep $(({start} - current_time)); fi",
				f"current_time={start}",
			]
		)

		for workload in workloads:
			run_cmd = _render_run_command(workload, duration)
			if run_cmd:
				lines.append(f"{run_cmd} &")

		lines.extend(["wait", f"current_time={end}", ""])

	if lines[-1] != "":
		lines.append("")

	out_dir = Path(output_path)
	out_dir.mkdir(parents=True, exist_ok=True)
	script_path = out_dir / f"{tenant_name}_run.sh"
	script_path.write_text("\n".join(lines), encoding="utf-8")
	script_path.chmod(0o755)
	return script_path


def generate_execute_script(tenant: dict[str, Any], output_path: str) -> Path:
	tenant_name = str(tenant.get("name", "tenant")).strip() or "tenant"
	prepare_script = f"{tenant_name}_prepare.sh"
	run_script = f"{tenant_name}_run.sh"

	lines = [
		"#!/usr/bin/env bash",
		"set -euo pipefail",
		"",
		"SCRIPT_DIR=$(cd -- \"$(dirname -- \"$0\")\" && pwd)",
		"",
		f"bash \"$SCRIPT_DIR/{prepare_script}\"",
		f"bash \"$SCRIPT_DIR/{run_script}\"",
		"",
	]

	out_dir = Path(output_path)
	out_dir.mkdir(parents=True, exist_ok=True)
	script_path = out_dir / f"{tenant_name}_execute.sh"
	script_path.write_text("\n".join(lines), encoding="utf-8")
	script_path.chmod(0o755)
	return script_path


def _generate_execute_script_for_all_tenants(tenants: list[dict[str, Any]], output_path: str) -> Path:
	lines = [
		"#!/usr/bin/env bash",
		"set -euo pipefail",
		"",
		"SCRIPT_DIR=$(cd -- \"$(dirname -- \"$0\")\" && pwd)",
		"prepare=false",
		"for arg in \"$@\"; do",
		"  case \"$arg\" in",
		"    --prepare) prepare=true ;;",
		"    *) echo \"Unknown argument: $arg\" >&2; exit 1 ;;",
		"  esac",
		"done",
		"",
		"if $prepare; then",
	]

	for tenant in tenants:
		tenant_name = str(tenant.get("name", "tenant")).strip() or "tenant"
		lines.append(f"bash \"$SCRIPT_DIR/{tenant_name}_prepare.sh\"")

	lines.extend(["fi", "", "# Start all run scripts concurrently"])

	for tenant in tenants:
		tenant_name = str(tenant.get("name", "tenant")).strip() or "tenant"
		lines.append(f"bash \"$SCRIPT_DIR/{tenant_name}_run.sh\" &")

	lines.extend(["wait", ""])

	out_dir = Path(output_path)
	out_dir.mkdir(parents=True, exist_ok=True)
	script_path = out_dir / "execute.sh"
	script_path.write_text("\n".join(lines), encoding="utf-8")
	script_path.chmod(0o755)
	return script_path


def _split_tenant_blocks(raw_text: str) -> list[str]:
	blocks: list[str] = []
	current: list[str] = []

	for line in raw_text.splitlines():
		if line.strip() == "tenant:" and current:
			blocks.append("\n".join(current).strip())
			current = []
		current.append(line)

	if current:
		blocks.append("\n".join(current).strip())

	return [block for block in blocks if block]


def _extract_tenants_from_doc(doc: Any) -> list[dict[str, Any]]:
	tenants: list[dict[str, Any]] = []

	if isinstance(doc, dict):
		tenant = doc.get("tenant")
		if isinstance(tenant, dict):
			tenants.append(tenant)

		tenant_list = doc.get("tenants")
		if isinstance(tenant_list, list):
			for item in tenant_list:
				if isinstance(item, dict):
					tenants.append(item)

	if isinstance(doc, list):
		for item in doc:
			if isinstance(item, dict):
				tenants.extend(_extract_tenants_from_doc(item))

	return tenants


def _load_tenants_from_config(config_path: str) -> list[dict[str, Any]]:
	raw_text = Path(config_path).read_text(encoding="utf-8")
	tenant_key_count = sum(1 for line in raw_text.splitlines() if line.strip() == "tenant:")

	docs: list[Any] = []
	if "\n---" in raw_text or raw_text.lstrip().startswith("---"):
		docs = [doc for doc in yaml.safe_load_all(raw_text) if doc is not None]
	elif tenant_key_count <= 1:
		doc = yaml.safe_load(raw_text)
		if doc is not None:
			docs = [doc]
	else:
		for block in _split_tenant_blocks(raw_text):
			doc = yaml.safe_load(block)
			if doc is not None:
				docs.append(doc)

	tenants: list[dict[str, Any]] = []
	for doc in docs:
		tenants.extend(_extract_tenants_from_doc(doc))

	return tenants


def generate_all_scripts_from_config(config_path: str, output_path: str | None = None) -> list[Path]:
	config_file = Path(config_path)
	out_dir = Path(output_path) if output_path else config_file.parent
	tenants = _load_tenants_from_config(str(config_file))

	generated_scripts: list[Path] = []
	for tenant in tenants:
		generated_scripts.append(generate_prepare_script(tenant, str(out_dir)))
		generated_scripts.append(generate_run_script(tenant, str(out_dir)))

	generated_scripts.append(_generate_execute_script_for_all_tenants(tenants, str(out_dir)))

	return generated_scripts


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate benchmark scripts from YAML configuration")
    parser.add_argument("config", help="Path to the YAML configuration file")
    parser.add_argument("-o", "--output", help="Directory to save generated scripts (default: same as config file)")
    args = parser.parse_args()

    generated_files = generate_all_scripts_from_config(args.config, args.output)
    print("Generated scripts:")
    for file in generated_files:
        print(f" - {file}")

