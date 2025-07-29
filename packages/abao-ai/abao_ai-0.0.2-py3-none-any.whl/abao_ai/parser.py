import argparse
import os


class Parser:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="abao_ai",
            description="abao.ai discord bot",
        )
        parsers = parser.add_subparsers(title="action", dest="action")
        install_parser = parsers.add_parser("install", help="install models")
        install_parser.add_argument("model", choices=["flux"])
        install_parser.add_argument("--hf-home", default=os.getenv("HF_HOME"))
        discord_parser = parsers.add_parser("discord", help="start discord bot")
        discord_parser.add_argument(
            "--discord-token",
            default=os.getenv("DISCORD_TOKEN"),
        )

        self.parser = parser

    def parse_args(self) -> argparse.Namespace:
        return self.parser.parse_args()
