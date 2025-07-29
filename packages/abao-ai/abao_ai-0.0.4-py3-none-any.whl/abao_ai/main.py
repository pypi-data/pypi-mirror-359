from abao_ai.parser import Parser
from abao_ai.discord_bot import Discord
from abao_ai.info import print_info
import os
from huggingface_hub import snapshot_download, hf_hub_download
from polygraphy.backend.trt import (
    CreateConfig,
    Profile,
    ShapeTuple,
    NetworkFromOnnxPath,
    EngineFromNetwork,
    SaveEngine,
    EngineFromPath,
)


def install(model: str):
    match model:
        case "flux":
            onnx_repo = "black-forest-labs/FLUX.1-dev-onnx"
            assert os.getenv("HF_HOME") == "/mnt/huggingface"
            assert os.getenv("HF_TOKEN")
            snapshot_download(onnx_repo)
            models = ["clip", "t5", "transformer", "vae"]
            clip_file = hf_hub_download(onnx_repo, f"clip.opt/model.onnx")
            t5_file = hf_hub_download(onnx_repo, f"t5.opt/model.onnx")
            transformer_file = hf_hub_download(
                onnx_repo, f"transformer.opt/bf16/model.onnx"
            )
            vae_file = hf_hub_download(onnx_repo, f"vae.opt/model.onnx")

            print(clip_file)
            print(t5_file)
            print(transformer_file)
            print(vae_file)
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
