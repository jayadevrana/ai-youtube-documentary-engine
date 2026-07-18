from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

from xmoney_mindset.config import Settings
from xmoney_mindset.utils.retry import api_retry


class OpenAIService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None
        if settings.openai_api_key:
            try:
                from openai import OpenAI  # type: ignore

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    @api_retry()
    def generate_text(self, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
        if not self._client:
            raise RuntimeError("OpenAI client unavailable")
        response = self._client.responses.create(
            model=model or self.settings.openai_text_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = getattr(response, "output_text", None)
        if not text:
            raise RuntimeError("Empty text response from OpenAI")
        return text.strip()

    @api_retry()
    def generate_tts(self, text: str, output_path: Path) -> Path:
        if not self._client:
            raise RuntimeError("OpenAI client unavailable")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self._client.audio.speech.with_streaming_response.create(
            model=self.settings.openai_tts_model,
            voice=self.settings.openai_tts_voice,
            input=text,
            format="mp3",
        ) as response:
            response.stream_to_file(str(output_path))

        return output_path

    @api_retry()
    def generate_image(self, prompt: str, output_path: Path) -> Path:
        if not self._client:
            raise RuntimeError("OpenAI client unavailable")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        response = self._client.images.generate(
            model=self.settings.openai_image_model,
            prompt=prompt,
            size="1792x1024",
        )
        data = response.data[0]
        b64_data = getattr(data, "b64_json", None)
        if not b64_data:
            raise RuntimeError("OpenAI image response missing b64 payload")

        image_bytes = base64.b64decode(b64_data)
        output_path.write_bytes(image_bytes)
        return output_path
