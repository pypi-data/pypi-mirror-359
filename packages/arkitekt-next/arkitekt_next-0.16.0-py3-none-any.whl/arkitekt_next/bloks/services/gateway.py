from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo
from dataclasses import dataclass
from typing import Dict, Any, Protocol

from blok import blok, InitContext, service


@service("live.arkitekt.gateway")
class GatewayService(Protocol):
    def expose_service(
        self, path_name: str, port: int, host: str, strip_prefix: bool = True
    ) -> str:
        """
        Expose a service on the gateway.

        :param path_name: The name of the path to expose.
        :param port: The port to expose the service on.
        :param host: The host to expose the service on.
        :param strip_prefix: Whether to strip the prefix from the path.
        :return: The name of the exposed service.
        """
        ...

    def retrieve_gateway_network(self): ...

    def expose_mapped(self, path_name: str, port: int, host: str, to_name: str): ...

    def expose_default(self, port: int, host: str): ...

    def expose_port(self, port: int, host: str, tls: bool = False): ...

    def expose_port_to(self, port: int, host: str, to_port: str, tls: bool = False): ...

    def get_internal_host(self): ...

    def get_https_port(self): ...

    def get_http_port(self): ...
