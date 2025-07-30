from typing import Dict, Any
import secrets

from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.ollama import OllamaService, OllamaAccess
from blok import blok, InitContext, ExecutionContext, Option
from blok.tree import YamlFile, Repo


@blok(OllamaService, description="a self-hosted Ollama LLM server")
class OllamaBlok:
    def __init__(self) -> None:
        self.host = "ollama"
        self.image = "ollama/ollama:latest"
        self.port = 11434
        self.skip = False
        self.gpu = bool

    def get_access(self) -> OllamaAccess:
        """Get the credentials for the Ollama service."""
        return OllamaAccess(
            api_key="",
            api_secret="",
            api_url=f"http://{self.host}:{self.port}",
            dependency=self.host,
        )

    def preflight(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        if self.skip:
            return

        self.initialized = True

    def build(self, context: ExecutionContext):
        if self.skip:
            return
        db_service = {
            "image": self.image,
            "environment": {
                "OLLAMA_KEEP_ALIVE": "24h",
            },
        }

        if self.gpu:
            db_service["deploy"] = {
                "resources": {
                    "reservations": {
                        "devices": [
                            {
                                "driver": "nvidia",
                                "count": 1,
                                "capabilities": ["gpu"],
                            }
                        ]
                    }
                }
            }

        context.docker_compose.set_nested("services", self.host, db_service)

    def get_options(self):
        with_host = Option(
            subcommand="host",
            help="The fakts url for connection",
            default=self.host,
        )
        with_skip = Option(
            subcommand="skip",
            help="The fakts_next url for connection",
            default=False,
            type=bool,
        )
        with_gpu = Option(
            subcommand="gpu",
            help="Whether to use a gpu",
            default=False,
            type=self.gpu,
        )

        return [
            with_host,
            with_skip,
            with_gpu,
        ]

    def __str__(self) -> str:
        return f"Ollama(host={self.host}, command={self.command}, image={self.image})"
