import os
from pathlib import Path
import winsound

from dotenv import load_dotenv
from openai import OpenAI

CLIENT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(CLIENT_ROOT.parent / ".env", override=False)


def required_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Missing {name}; copy .env.example to .env in iman-vllm-omni.")
    return value


MODEL = required_setting("TTS_MODEL")
PORT = int(required_setting("TTS_PORT"))
if not 1 <= PORT <= 65535:
    raise ValueError("TTS_PORT must be between 1 and 65535")
OUTPUT = CLIENT_ROOT / "output" / "speech.wav"

client = OpenAI(
    base_url=f"http://127.0.0.1:{PORT}/v1",
    api_key="EMPTY",
    timeout=300.0,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)


def generate_and_play(text: str) -> None:
    print("Generating speech...")

    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice="ryan",
        input=text,
        response_format="wav",
    ) as response:
        response.stream_to_file(OUTPUT)

    print(f"Audio saved: {OUTPUT}")

    winsound.PlaySound(
        str(OUTPUT),
        winsound.SND_FILENAME,
    )


def main() -> None:
    print("Kaspar TTS Demo")
    print("Type 'exit' to quit.")

    while True:
        text = input("\nEnter text: ").strip()

        if text.lower() == "exit":
            break

        if not text:
            continue

        try:
            generate_and_play(text)
        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
