import click

from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from typing import Dict, Optional
from arkitekt_next.bloks.secret import SecretBlok
from arkitekt_next.bloks.services.admin import AdminService
from arkitekt_next.bloks.services.db import DBService
from arkitekt_next.bloks.services.s3 import S3Service
from arkitekt_next.bloks.services.gateway import GatewayService
from arkitekt_next.bloks.services.livekit import LivekitService
from arkitekt_next.bloks.services.lok import LokCredentials, LokService
import yaml
import secrets
from dataclasses import asdict

from arkitekt_next.bloks.services.redis import RedisService
from blok import blok, InitContext, ExecutionContext, Option
from blok.bloks.services.dns import DnsService
from blok.tree import YamlFile, Repo
from blok import blok, InitContext


DEFAULT_ARKITEKT_URL = "http://localhost:8000"


# Define a custom user type that will parse and validate the user input
class UserParamType(click.ParamType):
    name = "user"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            name, password = value.split(":")
            return {"username": name, "password": password}
        except ValueError:
            self.fail(
                f"User '{value}' is not in the correct format. It should be 'name:password'.",
                param,
                ctx,
            )


USER = UserParamType()


# Define a custom user type that will parse and validate the user input
class GroupParamType(click.ParamType):
    name = "group"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            name, description = value.split(":")
            return {"name": name, "description": description}
        except ValueError:
            self.fail(
                f"User '{value}' is not in the correct format. It should be 'name:password'.",
                param,
                ctx,
            )


GROUP = GroupParamType()


class RedeemTokenParamType(click.ParamType):
    name = "redeem_token"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            assert "user" in value, f"scope is required {value}"
            assert "token" in value, f"description is required {value}"
            return value

        try:
            user, token = value.split(":")
            return {"user": user, "token": token}
        except ValueError:
            self.fail(
                f"RedeemToken '{value}' is not in the correct format. It should be 'username:token'.",
                param,
                ctx,
            )


TOKEN = RedeemTokenParamType()


class ScopeParamType(click.ParamType):
    name = "scope"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            assert "scope" in value, f"scope is required {value}"
            assert "description" in value, f"description is required {value}"
            return value

        try:
            name, description = value.split(":")
            return {"scope": name, "description": description}
        except ValueError:
            self.fail(
                f"Scopes '{value}' is not in the correct format. It should be 'scope:description'.",
                param,
                ctx,
            )


SCOPE = ScopeParamType()


@blok(LokService, description="Lok is an authentication and authorization service")
class LokBlok:
    db_name: str

    def __init__(self) -> None:
        self.db_name = "lok_db"
        self.mount_repo = False
        self.build_repo = False
        self.private_key = None
        self.public_key = None
        self.host = "lok"
        self.dev = False
        self.with_repo = False
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/lok-server-next"
        self.image = "jhnnsrs/lok_next:nightly"
        self.users = []
        self.tokens = []
        self.groups = []
        self.secret_key = secrets.token_hex(16)
        self.scopes = {
            "openid": "The open id connect scope",
            "read": "A generic read access",
            "write": "A generic write access",
        }
        self.email_service: str = "smtp"
        self.email_host: str = "NOT_SET"
        self.email_port: int = 587
        self.email_user: str = "NOT_SET"
        self.email_password: str = "NOT_SET"
        self.email_from: str = "NOT_SET"

        self.buckets = ["media"]
        self.key = None
        self.deployment_name = "default"
        self.token_expiry_seconds = 700000
        self.preformed_redeem_tokens = [secrets.token_hex(16) for i in range(80)]
        self.registered_tokens = {}
        self.local_access = None
        self.registered_instances = [
            {
                "identifier": "local-lok",
                "service": "live.arkitekt.lok",
                "aliases": [
                    {
                        "layer": "public",
                        "kind": "relative",
                        "path": "lok",
                        "challenge": "ht",
                    }
                ],
            },
            {
                "identifier": "local-datalayer",
                "service": "live.arkitekt.s3",
                "aliases": [
                    {
                        "layer": "public",
                        "kind": "relative",
                        "challenge": "minio/health/live",
                    }
                ],
            },
        ]

    def retrieve_credentials(self) -> LokCredentials:
        return LokCredentials(
            public_key=self.public_key, key_type="RS256", issuer="lok"
        )

    def retrieve_labels(self, service_name: str, builder_name: str) -> list[str]:
        return [
            f"fakts.service={service_name}",
            f"fakts.builder={builder_name}",
        ]

    def retrieve_token(self, user: str = "admin") -> str:
        new_token = self.secret_blok.retrieve_secret()
        self.registered_tokens[user] = new_token

        return new_token

    def register_scopes(self, scopes_dict: Dict[str, str]) -> LokCredentials:
        self.scopes = self.scopes | scopes_dict

    def register_service_on_subpath(self, service_name: str, subpath: str, htpath: str):
        registered_instance = {
            "identifier": f"local-{service_name}",
            "service": service_name,
            "aliases": [
                {
                    "layer": "public",
                    "kind": "relative",
                    "path": subpath,
                    "challenge": htpath,
                }
            ],
        }
        self.registered_instances.append(registered_instance)

    def preflight(
        self,
        init: InitContext,
        gateway: GatewayService,
        db: DBService,
        redis: RedisService,
        admin: AdminService,
        secrets: SecretBlok,
        s3: S3Service,
    ):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        assert self.public_key, "Public key is required"
        assert self.private_key, "Private key is required"

        self.exposed_path = gateway.expose_service(
            "lok", 80, self.host, strip_prefix=False
        )
        self.exposed_services = {"live.arkitekt.lok": {}}

        gateway.expose_mapped(".well-known", 80, self.host, "lok")

        self.secret_blok = secrets
        self.postgress_access = db.register_db(self.host)
        self.redis_access = redis.register()
        self.admin_access = admin.retrieve()
        self.s3_access = s3.create_buckets(self.buckets)
        self.initialized = True

    def build(self, context: ExecutionContext):
        depends_on = []

        if self.redis_access.dependency:
            depends_on.append(self.redis_access.dependency)

        if self.postgress_access.dependency:
            depends_on.append(self.postgress_access.dependency)

        if self.s3_access.dependency:
            depends_on.append(self.s3_access.dependency)

        db_service = {
            "depends_on": depends_on,
            "volumes": [
                "./configs/lok.yaml:/workspace/config.yaml",
            ],
        }

        if self.mount_repo or self.dev:
            context.file_tree.set_nested("mounts", "lok", Repo(self.repo))
            db_service["volumes"].append("./mounts/lok:/workspace")

        if self.build_repo or self.dev:
            context.file_tree.set_nested("mounts", "lok", Repo(self.repo))
            db_service["build"] = "./mounts/lok"
        else:
            db_service["image"] = self.image

        db_service["command"] = self.command

        trusted_origins = []

        configuration = YamlFile(
            **{
                "db": asdict(self.postgress_access),
                "users": [user for user in self.users],
                "django": {
                    "admin": asdict(self.admin_access),
                    "debug": True,
                    "hosts": ["*"],
                    "secret_key": self.secret_key,
                },
                "redis": asdict(self.redis_access),
                "lok": asdict(self.retrieve_credentials()),
                "private_key": self.private_key,
                "public_key": self.public_key,
                "scopes": self.scopes,
                "redeem_tokens": [
                    {"user": name, "token": token}
                    for name, token in self.registered_tokens.items()
                ],
                "groups": [group for group in self.groups],
                "deployment": {"name": self.deployment_name},
                "s3": asdict(self.s3_access),
                "token_expire_seconds": self.token_expiry_seconds,
                "force_script_name": "lok",
                "layers": [
                    {
                        "identifier": "public",
                        "kind": "public",
                    }
                ],
                "instances": self.registered_instances,
                "csrf_trusted_origins": trusted_origins,
                "email": {
                    "service": self.email_service,
                    "host": self.email_host,
                    "port": self.email_port,
                    "user": self.email_user,
                    "password": self.email_password,
                    "from": self.email_from,
                },
            }
        )

        context.file_tree.set_nested("configs", "lok.yaml", configuration)

        context.docker_compose.set_nested("services", self.host, db_service)

    def get_options(self):
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=crypto_default_backend()
        )

        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption(),
        ).decode()

        public_key = (
            key.public_key()
            .public_bytes(
                crypto_serialization.Encoding.OpenSSH,
                crypto_serialization.PublicFormat.OpenSSH,
            )
            .decode()
        )

        with_dev = Option(
            subcommand="dev",
            help="Run the service in development mode",
            type=bool,
            default=self.dev,
            show_default=True,
        )

        with_fakts_url = Option(
            subcommand="db_name",
            help="The name of the database",
            default="db_name",
            show_default=True,
        )
        with_users = Option(
            subcommand="users",
            help="Users that should be greated by default. Format is name:password",
            default=["admin:admin"],
            multiple=True,
            type=USER,
            show_default=True,
        )
        with_groups = Option(
            subcommand="groups",
            help="Groups that should be greated by default. Format is name:description",
            default=["admin:admin_group"],
            multiple=True,
            type=GROUP,
            show_default=True,
        )
        with_public_key = Option(
            subcommand="public_key",
            help="The public key for the JWT creation",
            default=public_key,
            required=True,
            callback=validate_public_key,
        )
        with_private_key = Option(
            subcommand="private_key",
            help="The corresponding private key for the JWT creation",
            default=private_key,
            callback=validate_private_key,
            required=True,
        )

        return [
            with_dev,
            with_fakts_url,
            with_users,
            with_groups,
            with_private_key,
            with_public_key,
        ]


def validate_public_key(ctx, param, value):
    if not value.startswith("ssh-rsa"):
        raise click.BadParameter(
            f"Public key must be in ssh-rsa format. Started with {value}"
        )
    return value


def validate_private_key(ctx, param, value):
    if not value.startswith("-----BEGIN PRIVATE KEY-----"):
        raise click.BadParameter(
            f"Private key must be in PEM format. Started with {value}"
        )
    return value
