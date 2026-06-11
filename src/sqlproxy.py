#!/usr/bin/env python3
import argparse
import asyncio
import contextlib
import logging
from dataclasses import dataclass


BACKEND_BLOCK_THRESHOLD = 3
CONNECT_TIMEOUT_SEC = 3.0


class GlobalAllocationBlocked(RuntimeError):
	pass


@dataclass
class Backend:
	name: str
	host: str
	port: int
	weight: int
	sql_count: int = 0
	block_count: int = 0
	blocked: bool = False


class WeightedSQLBalancer:
	def __init__(self, backends: list[Backend], block_threshold: int = BACKEND_BLOCK_THRESHOLD):
		if not backends:
			raise ValueError("at least one backend is required")

		for backend in backends:
			if backend.weight <= 0:
				raise ValueError(f"backend {backend.name} has invalid weight {backend.weight}")

		self.backends: dict[str, Backend] = {backend.name: backend for backend in backends}
		self.block_threshold = block_threshold
		self.global_blocked = False

	def mark_backend_healthy(self, backend_name: str) -> None:
		backend = self.backends[backend_name]
		backend.blocked = False
		backend.block_count = 0

		if self.global_blocked:
			self.global_blocked = any(item.block_count >= self.block_threshold for item in self.backends.values())

	def mark_backend_blocked(self, backend_name: str) -> None:
		backend = self.backends[backend_name]
		backend.blocked = True
		backend.block_count += 1

		logging.warning(
			"backend %s blocked (%d/%d)",
			backend.name,
			backend.block_count,
			self.block_threshold,
		)

		if backend.block_count >= self.block_threshold:
			self.global_blocked = True
			logging.error(
				"backend %s reached block threshold, enable global allocation block",
				backend.name,
			)

	def record_sql(self, backend_name: str, count: int = 1) -> None:
		self.backends[backend_name].sql_count += count

	def choose_backend(self) -> Backend:
		if self.global_blocked:
			raise GlobalAllocationBlocked("global allocation blocked")

		candidates = [backend for backend in self.backends.values() if not backend.blocked]
		if not candidates:
			raise GlobalAllocationBlocked("all backends are blocked")

		# Weighted SQL allocation by minimizing (assigned_sql / weight).
		return min(candidates, key=lambda item: item.sql_count / item.weight)


class SQLTransparentProxy:
	def __init__(self, listen_host: str, listen_port: int, balancer: WeightedSQLBalancer):
		self.listen_host = listen_host
		self.listen_port = listen_port
		self.balancer = balancer

	async def start(self) -> None:
		server = await asyncio.start_server(self.handle_client, self.listen_host, self.listen_port)
		addr = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
		logging.info("sql proxy listening on %s", addr)

		async with server:
			await server.serve_forever()

	async def handle_client(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
		peer = client_writer.get_extra_info("peername")
		backend: Backend | None = None
		backend_reader: asyncio.StreamReader | None = None
		backend_writer: asyncio.StreamWriter | None = None

		try:
			backend = self.balancer.choose_backend()
			logging.info("accept client %s -> backend %s", peer, backend.name)

			backend_reader, backend_writer = await asyncio.wait_for(
				asyncio.open_connection(backend.host, backend.port),
				timeout=CONNECT_TIMEOUT_SEC,
			)
			self.balancer.mark_backend_healthy(backend.name)

			tasks = [
				asyncio.create_task(self.relay_client_to_backend(client_reader, backend_writer, backend.name)),
				asyncio.create_task(self.relay_plain(backend_reader, client_writer)),
			]

			done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
			for task in pending:
				task.cancel()
			for task in done:
				with contextlib.suppress(asyncio.CancelledError):
					await task

		except GlobalAllocationBlocked:
			logging.warning("reject client %s due to global allocation block", peer)
		except (TimeoutError, OSError, ConnectionError) as exc:
			if backend is not None:
				self.balancer.mark_backend_blocked(backend.name)
			logging.error("backend connect/relay error: %s", exc)
		finally:
			if backend_writer is not None:
				backend_writer.close()
				with contextlib.suppress(Exception):
					await backend_writer.wait_closed()

			client_writer.close()
			with contextlib.suppress(Exception):
				await client_writer.wait_closed()

	async def relay_plain(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
		while True:
			data = await reader.read(65536)
			if not data:
				break
			writer.write(data)
			await writer.drain()

	async def relay_client_to_backend(
		self,
		client_reader: asyncio.StreamReader,
		backend_writer: asyncio.StreamWriter,
		backend_name: str,
	) -> None:
		buffer = b""
		while True:
			chunk = await client_reader.read(65536)
			if not chunk:
				break

			buffer += chunk
			packet_count, consumed = self.count_mysql_query_packets(buffer)
			if packet_count > 0:
				self.balancer.record_sql(backend_name, packet_count)
			if consumed > 0:
				buffer = buffer[consumed:]

			backend_writer.write(chunk)
			await backend_writer.drain()

	@staticmethod
	def count_mysql_query_packets(data: bytes) -> tuple[int, int]:
		idx = 0
		packet_count = 0
		total = len(data)

		while idx + 4 <= total:
			payload_len = int.from_bytes(data[idx:idx + 3], "little")
			packet_end = idx + 4 + payload_len
			if packet_end > total:
				break

			# MySQL command phase: COM_QUERY = 0x03
			if payload_len >= 1 and data[idx + 4] == 0x03:
				packet_count += 1

			idx = packet_end

		return packet_count, idx


def parse_backend(definition: str) -> Backend:
	# Format: name,host,port,weight
	parts = [item.strip() for item in definition.split(",")]
	if len(parts) != 4:
		raise ValueError(f"invalid backend definition: {definition}")

	name, host, port_text, weight_text = parts
	return Backend(name=name, host=host, port=int(port_text), weight=int(weight_text))


def build_arg_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="SQL transparent proxy with weighted allocation")
	parser.add_argument("--listen-host", default="0.0.0.0")
	parser.add_argument("--listen-port", type=int, default=4000)
	parser.add_argument(
		"--backend",
		action="append",
		required=True,
		help="backend in name,host,port,weight format; can be repeated",
	)
	parser.add_argument("--block-threshold", type=int, default=BACKEND_BLOCK_THRESHOLD)
	parser.add_argument("--log-level", default="INFO")
	return parser


async def main_async() -> None:
	parser = build_arg_parser()
	args = parser.parse_args()

	logging.basicConfig(
		level=getattr(logging, args.log_level.upper(), logging.INFO),
		format="%(asctime)s %(levelname)s %(message)s",
	)

	backends = [parse_backend(item) for item in args.backend]
	balancer = WeightedSQLBalancer(backends=backends, block_threshold=args.block_threshold)
	proxy = SQLTransparentProxy(args.listen_host, args.listen_port, balancer)
	await proxy.start()


def main() -> None:
	asyncio.run(main_async())


if __name__ == "__main__":
	main()
