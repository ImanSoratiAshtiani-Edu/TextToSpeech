
from pathlib import Path
import winsound

from openai import OpenAI

MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
OUTPUT = Path(__file__).parent / "output" / "speech.wav"

client = OpenAI(
    base_url="http://localhost:8091/v1",
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
