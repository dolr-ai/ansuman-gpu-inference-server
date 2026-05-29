"""Tests for vLLM runtime command wiring."""

from backend.core.config import Settings
from backend.services.vllm.runtime import build_vllm_serve_command, command_to_shell


def test_build_vllm_command_binds_localhost_and_sets_capacity_knobs() -> None:
    settings = Settings(
        model_ids_raw="public-model",
        vllm_model_path="/models/qwen",
        vllm_host="127.0.0.1",
        vllm_port=8001,
        vllm_tensor_parallel_size=4,
        vllm_max_model_len=4096,
        vllm_gpu_memory_utilization=0.85,
        vllm_max_num_seqs=32,
        vllm_max_num_batched_tokens=8192,
    )

    command = build_vllm_serve_command(settings)

    assert command[:3] == ["vllm", "serve", "/models/qwen"]
    assert command[command.index("--host") + 1] == "127.0.0.1"
    assert command[command.index("--port") + 1] == "8001"
    assert command[command.index("--served-model-name") + 1] == "public-model"
    assert command[command.index("--tensor-parallel-size") + 1] == "4"
    assert command[command.index("--max-model-len") + 1] == "4096"
    assert command[command.index("--gpu-memory-utilization") + 1] == "0.85"
    assert command[command.index("--max-num-seqs") + 1] == "32"
    assert command[command.index("--max-num-batched-tokens") + 1] == "8192"


def test_command_to_shell_quotes_arguments() -> None:
    rendered = command_to_shell(["vllm", "serve", "/models/qwen fp8"])

    assert rendered == "vllm serve '/models/qwen fp8'"
