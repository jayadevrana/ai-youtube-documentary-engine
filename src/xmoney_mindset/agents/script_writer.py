from __future__ import annotations

import math

from xmoney_mindset.config import Settings
from xmoney_mindset.models import ScriptPackage, TopicCandidate
from xmoney_mindset.services.openai_service import OpenAIService


class ScriptWriterAgent:
    """Generates a cinematic documentary script using the James Jani-style formula."""

    def __init__(self, settings: Settings, openai_service: OpenAIService):
        self.settings = settings
        self.openai_service = openai_service

    def _fallback_script(self, topic: TopicCandidate) -> ScriptPackage:
        title = topic.title
        hook = (
            "Everyone wants financial freedom. "
            "But most people are following rules designed for predictability, not wealth."
        )

        sections = {
            "hook": (
                f"{hook} Because the truth about money is rarely loud. "
                "It hides in systems, incentives, and the stories we inherit."
            ),
            "problem": (
                "For years, the public has been sold a clean formula: work hard, stay motivated, and everything will follow. "
                "It sounds fair. It sounds moral. It is also incomplete."
            ),
            "investigation": (
                "When we examine financial history, a pattern appears. "
                "The biggest outcomes usually come from leverage: ownership, distribution, technology, and networks. "
                "Not from motivation alone."
            ),
            "psychology": (
                "Humans are vulnerable to authority bias, status signaling, and social proof. "
                "We trust confidence. We copy visible winners. "
                "And we underestimate quiet systems that compound in the background."
            ),
            "reveal": (
                f"Here is the hidden truth behind {title.lower()}: "
                "wealth is often the byproduct of position, incentives, and repeated high-quality decisions over time."
            ),
            "resolution": (
                "The practical path is less glamorous: increase savings power, buy productive assets, build rare skills, "
                "and design environments that reduce bad decisions."
            ),
            "ending": (
                "Success is not a motivational event. It is a systems outcome. "
                "And once you see the system, you stop chasing noise."
            ),
        }

        # Target ~145 wpm narration to match desired runtime.
        target_words = self.settings.target_duration_minutes * 145
        base_blocks = [
            sections["hook"],
            sections["problem"],
            sections["investigation"],
            sections["psychology"],
            sections["reveal"],
            sections["resolution"],
            sections["ending"],
        ]

        loop_templates = [
            "Insight: the market does not reward effort equally. It rewards effort that can be multiplied.",
            "Question: if hard work alone creates wealth, why do equally hard-working people see radically different outcomes?",
            "Reveal: access to distribution, ownership, and trust changes the speed of progress.",
            "Story: each decade creates a new class of winners by shifting which skills can scale.",
            "Insight: when incentives and psychology align, consistent action becomes easier than willpower alone.",
            "Question: are you optimizing for appearance, or for compounding systems that survive trends?",
            "Reveal: most failures are not moral failures. They are design failures in strategy and environment.",
            "Story: people who win long-term protect downside first, then apply focused risk to asymmetric opportunities.",
        ]

        words_now = sum(len(block.split()) for block in base_blocks)
        needed_words = max(0, target_words - words_now)
        loops = max(10, math.ceil(needed_words / 26))

        expanded: list[str] = []
        for i in range(loops):
            line = loop_templates[i % len(loop_templates)]
            expanded.append(f"Cycle {i + 1}. {line}")

        full_narration = "\n\n".join(base_blocks + expanded)
        return ScriptPackage(title=title, hook=hook, sections=sections, full_narration=full_narration)

    def _llm_script(self, topic: TopicCandidate) -> ScriptPackage:
        system = (
            "You write cinematic investigative YouTube narration in the style of reflective documentary channels. "
            "Output must be plain text using headers: HOOK, PROBLEM, INVESTIGATION, PSYCHOLOGY, REVEAL, RESOLUTION, ENDING."
        )
        user = (
            f"Topic: {topic.title}\n"
            f"Hidden truth: {topic.hidden_truth}\n"
            "Constraints:\n"
            "- tone calm, analytical, slightly mysterious\n"
            "- no hype language\n"
            "- include curiosity loops every 30-40 seconds\n"
            f"- target runtime {self.settings.target_duration_minutes} minutes\n"
            "- topic domain: finance, psychology, success\n"
        )
        text = self.openai_service.generate_text(system, user)

        sections: dict[str, str] = {}
        current = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            upper = line.upper().strip(":")
            if upper in {"HOOK", "PROBLEM", "INVESTIGATION", "PSYCHOLOGY", "REVEAL", "RESOLUTION", "ENDING"}:
                current = upper.lower()
                sections[current] = ""
                continue
            if current:
                sections[current] = (sections[current] + " " + line).strip()

        required = ["hook", "problem", "investigation", "psychology", "reveal", "resolution", "ending"]
        if not all(key in sections and sections[key] for key in required):
            raise RuntimeError("Could not parse script sections from LLM output")

        full_narration = "\n\n".join(sections[key] for key in required)
        return ScriptPackage(
            title=topic.title,
            hook=sections["hook"],
            sections=sections,
            full_narration=full_narration,
        )

    def write(self, topic: TopicCandidate) -> ScriptPackage:
        if self.settings.enable_real_generation and self.openai_service.available:
            try:
                return self._llm_script(topic)
            except Exception:
                pass
        return self._fallback_script(topic)
