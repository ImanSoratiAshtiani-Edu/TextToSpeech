"""Apply the local embedding dtype fix to the pinned upstream image."""
from pathlib import Path
import importlib.util


def patch_text(text: str) -> str:
    target = "                inputs_embeds.index_copy_(0, offsets_t, req_embeds)"
    fixed = (
        "                if req_embeds.dtype != inputs_embeds.dtype:\n"
        "                    req_embeds = req_embeds.to(dtype=inputs_embeds.dtype)\n"
        + target
    )
    if text.count(fixed) == 1:
        return text
    if text.count(target) != 1:
        raise RuntimeError("Unexpected upstream runner: expected exactly one patch location")
    return text.replace(target, fixed, 1)


def main() -> None:
    spec = importlib.util.find_spec("vllm_omni")
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError("vllm_omni package not found")
    path = Path(next(iter(spec.submodule_search_locations))) / "worker/gpu_model_runner.py"
    original = path.read_text(encoding="utf-8")
    updated = patch_text(original)
    compile(updated, str(path), "exec")
    path.write_text(updated, encoding="utf-8")
    print("Embedding dtype compatibility patch installed:", path)


if __name__ == "__main__":
    main()
