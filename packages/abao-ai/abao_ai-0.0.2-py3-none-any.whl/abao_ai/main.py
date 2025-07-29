from abao_ai.parser import Parser
from abao_ai.discord_bot import Discord
from abao_ai.info import print_info

from huggingface_hub import snapshot_download


def install(model: str):
    match model:
        case "flux":
            snapshot_download("black-forest-labs/FLUX.1-dev")
        case _:
            print(model)


def main():

    parser = Parser()
    args = parser.parse_args()
    match args.action:
        case "discord":
            discord = Discord()
            discord.run(args.discord_token)
        case "install":
            install(args.model)
        case _:
            print_info()


if __name__ == "__main__":
    install("flux")
