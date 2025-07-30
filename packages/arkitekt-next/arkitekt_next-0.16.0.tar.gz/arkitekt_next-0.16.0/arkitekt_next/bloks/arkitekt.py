from typing import Any, Dict, Optional

from pydantic import BaseModel

from arkitekt_next.bloks.kraph import KraphBlok
from arkitekt_next.bloks.lok import LokBlok
from arkitekt_next.bloks.tailscale import TailscaleBlok
from blok import InitContext, Panel, Renderer, blok

from .fluss import FlussBlok
from .internal_docker import InternalDockerBlok
from .kabinet import KabinetBlok
from .mikro import MikroBlok
from .orkestrator import OrkestratorBlok
from .rekuest import RekuestBlok
from .ollama import OllamaBlok
from .elektro import ElektroBlok
from .alpaka import AlpakaBlok
from .lovekit import LovekitBlok


class AdminCredentials(BaseModel):
    password: str
    username: str
    email: str


@blok(
    "live.arkitekt",
    dependencies=[
        LokBlok.as_dependency(True, True),
        MikroBlok.as_dependency(True, True),
        KabinetBlok.as_dependency(True, True),
        RekuestBlok.as_dependency(True, True),
        FlussBlok.as_dependency(True, True),
        InternalDockerBlok.as_dependency(True, True),
        KraphBlok.as_dependency(True, True),
        AlpakaBlok.as_dependency(True, True),
        ElektroBlok.as_dependency(True, True),
        LovekitBlok.as_dependency(True, True),
    ],
)
class ArkitektBlok:
    def entry(self, renderer: Renderer):
        renderer.render(
            Panel(
                f"""This is the arkitekt build that allows you to setup a full stack arkitekt application. You can use this to setup a full stack application with the following services""",
                expand=False,
                title="Welcome to Arkitekt!",
                style="bold magenta",
            )
        )

    def build(self, cwd):
        pass
