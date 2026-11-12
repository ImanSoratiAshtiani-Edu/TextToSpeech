# iman-vllm-omni

A small text-to-speech demo for Kaspar. The server is vLLM-Omni running the
Qwen3-TTS model in Docker. The client is a console script that sends it a line of
text, saves the returned audio and plays it.

It has been run end to end on Windows with Docker Desktop (WSL2) and an NVIDIA GPU:
the server comes up with `docker compose`, and the client writes `output/speech.wav`.

```
iman-vllm-omni/
├── client/   console client (main.py wrapper, src/demo_tts/app.py, pyproject.toml)
└── server/   compose.yaml and the patched file for the container
```

## How it fits together

```mermaid
flowchart TB
    USER["User types text"]

    subgraph CLIENT["Client (Windows): client/"]
        MAIN["src/demo_tts/app.py<br/>main(): input loop"]
        GEN["generate_and_play(text)"]
        SDK["OpenAI SDK client<br/>base_url 127.0.0.1:TTS_PORT/v1<br/>timeout 300 s"]
        REQ["Speech request<br/>voice: ryan, format: wav"]
        SAVE["response.stream_to_file(OUTPUT)"]
        WAV[("output/speech.wav")]
        PLAY["winsound.PlaySound(...)<br/>Windows only"]
        SPEAKER["Speaker"]

        CONFIG["Shared .env<br/>TTS_MODEL, TTS_PORT"]
        DEPS["pyproject.toml + uv.lock<br/>openai dependency<br/>.python-version 3.13"]

        MAIN --> GEN --> SDK --> REQ
        SAVE --> WAV --> PLAY --> SPEAKER
        CONFIG -.-> GEN
        DEPS -.-> SDK
    end

    subgraph SERVER["Server (WSL2 + Docker, NVIDIA GPU): server/, container kaspar-tts"]
        API["vLLM-Omni speech API<br/>container port TTS_SERVER_PORT"]
        ENGINE["OmniGPUModelRunner<br/>(other internals omitted)"]
        MODEL[("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice<br/>HuggingFace cache volume")]
        AUDIO["Generated audio<br/>WAV response"]
        PATCH["server/patches/gpu_model_runner.py<br/>bind-mounted read-only<br/>casts embeds to matching dtype"]

        API --> ENGINE
        MODEL -.-> ENGINE
        PATCH -.-> ENGINE
        ENGINE --> AUDIO
    end

    USER --> MAIN
    REQ -->|"POST /v1/audio/speech<br/>127.0.0.1:TTS_PORT to :TTS_SERVER_PORT"| API
    AUDIO -->|"HTTP response bytes"| SAVE
```

The server side is deliberately rough. Only the patched `OmniGPUModelRunner` was
looked at, the rest of vLLM-Omni is not drawn.

## Running it

From `iman-vllm-omni/`, copy `.env.example` to `.env` once (`Copy-Item .env.example .env` in PowerShell, or `cp .env.example .env` on Linux).

Edit `TTS_MODEL` and `TTS_PORT` in this shared file to configure both client and server. `TTS_SERVER_PORT` controls the container's listening port; `TTS_PORT` is the host port the client connects to. The client resolves `.env` relative to its source location, not the current directory. Shell environment variables override `.env` in both tools. Restart the server and client after changing settings. `.env` is ignored by Git; `.env.example` documents the initial values.

Start the server (needs Docker and an NVIDIA GPU):

```
cd server
docker compose --env-file ../.env up -d
docker compose --env-file ../.env logs -f
```

The first start downloads the model, so give it a few minutes. When the log says the
server is listening, check it with `curl http://127.0.0.1:8091/v1/models` (replace `8091` if you changed `TTS_PORT`). Stop it with
`docker compose --env-file ../.env down`.

The port is only bound to 127.0.0.1. If you already have a HuggingFace cache you can
reuse it instead of the named volume:
`HF_CACHE=$HOME/.cache/huggingface docker compose --env-file ../.env up -d`.

The image is pinned by digest, it was the `omni-cuda` tag when this was set up:
`public.ecr.aws/deep-learning-containers/vllm@sha256:7e1f0b3cce437c5d857824de2c47716302143102ce18314acb70e3f9409a19d3`

Then the client:

```
cd client
uv sync
uv run demo-tts
```

`uv run python main.py` also works through the root wrapper; both commands run the same client implementation.

Type a sentence, the audio is saved to `output/speech.wav` and played.

## The patch

Without it the server failed in `OmniGPUModelRunner` because `req_embeds` and
`inputs_embeds` had different dtypes before `index_copy_` (around line 1740 of
`gpu_model_runner.py`). The fix casts `req_embeds` to the dtype of `inputs_embeds`.

`server/patches/gpu_model_runner-dtype.patch` is the diff. `gpu_model_runner.py` next to
it is the whole patched file, which `compose.yaml` mounts over the one in the image.
The patch applies cleanly to the original file and gives the patched file back exactly.
The original is the same size as the file in the image (109257 bytes); I have not
compared hashes.

## Things that are not done

- The client uses `winsound`, so it only plays audio on Windows.
- Mounting a whole file ties this to one image. A Dockerfile that applies the `.patch`
  at build time would fail loudly when the image changes instead of silently
  overriding newer code.
- No authentication on the server, and it is only reachable from the same machine.
