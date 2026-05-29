"""Run the configured vLLM OpenAI-compatible server."""

import os

from backend.core.config import get_settings
from backend.services.vllm.runtime import build_vllm_serve_command, command_to_shell


def main() -> None:
    settings = get_settings()
    command = build_vllm_serve_command(settings)
    print(command_to_shell(command), flush=True)
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
