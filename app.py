"""
 ██████╗ █████╗ ███████╗ █████╗ ██████╗  ██████╗ ██████╗
██╔════╝██╔══██╗╚══███╔╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
██║     ███████║  ███╔╝ ███████║██║  ██║██║   ██║██████╔╝
██║     ██╔══██║ ███╔╝  ██╔══██║██║  ██║██║   ██║██╔══██╗
╚██████╗██║  ██║███████╗██║  ██║██████╔╝╚██████╔╝██║  ██║
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
                                           THE SSH-TUNNEL
"""

import asyncio
import codecs
import hashlib
import os
import sys

import yaml
from asyncssh import create_server, connect, SSHServer, Error
from cerberus import Validator


class ConfigError(Exception):
    pass


class Server(SSHServer):
    def __init__(self, users, allow_empty_passwords=False):
        self.users = users
        self.allow_empty_passwords = allow_empty_passwords

    def begin_auth(self, username):
        return username not in self.users or not (
                self.allow_empty_passwords and self.users[username] is None
        )

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return username in self.users and self.users[username] == hashlib.sha256(password.encode("utf-8")).hexdigest()


async def exec_process(process, connections, commands, routes):
    username = process.get_extra_info("username")

    route = routes.get(username, {})
    conn = connections.get(route.get("connection"), {})
    commands_list = commands.get(route.get("command"), [])

    if not route or not conn:
        # TODO: Say something terrible
        process.stdout.write("Configuration error! Please contact your administrator.")
        process.exit(0)

    async with connect(
            conn["host"], conn["port"],
            username=conn["username"],
            password=conn["password"]) as conn:
        result = await conn.run(
            command=" ; ".join(commands_list) or process.command,
            encoding=None,
            term_type=process.get_terminal_type(),
            term_size=process.get_terminal_size(),
            stdin=process.stdin,
            stdout=process.stdout,
            stderr=process.stderr
        )

        process.exit(result.exit_status)


async def start_server(config):
    params = config["config"]
    users = config["users"]
    connections = config["connections"]
    commands = config["commands"]
    routes = config["routes"]

    server = await create_server(
        lambda: Server(users, params.get("allow_empty_passwords", False)),
        port=params.get("port", 22),
        server_host_keys=params["host_keys"],
        process_factory=lambda process: exec_process(process, connections, commands, routes),
        session_encoding=None
    )

    await server.serve_forever()


if __name__ == "__main__":
    try:
        config_path = os.getenv("CONFIG_PATH")
        if not config_path:
            raise OSError("Parameter \"CONFIG_PATH\" is not set")

        if not os.path.isfile(config_path):
            raise OSError("Invalid config file path")

        config = yaml.load(codecs.open(config_path, encoding="utf-8"))

        str_list_schema = {"type": "list", "schema": {"type": "string"}}
        cfg_validator = Validator({
            "config": {
                "type": "dict",
                "schema": {
                    "port": {"type": "integer", "required": False},
                    "allow_empty_passwords": {"type": "boolean", "required": False},
                    "host_keys": {**str_list_schema, "required": True}
                },
                "required": True
            },
            "users": {
                "type": "dict",
                "valueschema": {
                    "type": "string", "nullable": True
                },
                "required": True
            },
            "connections": {
                "type": "dict",
                "valueschema": {
                    "type": "dict",
                    "schema": {
                        "host": {"type": "string", "required": True},
                        "port": {"type": "integer", "required": False},
                        "username": {"type": "string", "required": True},
                        "password": {"type": "string", "required": False}
                    }
                },
                "required": True},
            "commands": {
                "type": "dict",
                "valueschema": str_list_schema,
                "required": True
            },
            "routes": {
                "type": "dict",
                "valueschema": {
                    "type": "dict",
                    "schema": {
                        "connection": {"type": "string", "required": True},
                        "command": {"type": "string", "required": False}
                    }
                },
                "required": True},
        }, allow_unknown=True)

        if not cfg_validator.validate(config):
            raise ConfigError(f"Config error: {cfg_validator.errors}")

        asyncio.run(start_server(config))
    except (OSError, ConfigError, Error) as exc:
        sys.exit(f"Could not start server. \r\n {exc}")
