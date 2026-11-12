# demo-tts client

Windows console client for the vLLM-Omni TTS server. Follow the
[demo setup guide](../README.md) first to create the shared `../.env` and start
the server. The root K.ai application has a separate environment.

From this `client/` directory:

```powershell
uv sync --locked
uv run demo-tts
```

Alternatively, run `uv run python main.py`. Both commands use the same client.
Type text to generate and play `output/speech.wav`; type `exit` to quit.
Model and port settings come from `../.env`, with shell variables taking precedence.
