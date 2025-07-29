from abao_ai.parser import Parser
from abao_ai.discord_bot import Discord
from abao_ai.info import print_info
import os
from huggingface_hub import snapshot_download
from dotenv import load_dotenv


def install(model: str):
    match model:
        case "flux":
            assert os.getenv("HF_HOME") == "/mnt/huggingface"
            assert os.getenv("HF_TOKEN")
            snapshot_download("black-forest-labs/FLUX.1-dev")
            snapshot_download("black-forest-labs/FLUX.1-dev-onnx")
        case _:
            print(model)


def main():
    load_dotenv()
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
    load_dotenv()
    install("flux")
