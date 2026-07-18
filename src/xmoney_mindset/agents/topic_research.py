from __future__ import annotations

from xmoney_mindset.models import TopicCandidate, TopicScore
from xmoney_mindset.services.openai_service import OpenAIService


class TopicResearchAgent:
    """Finds high-retention documentary topics with heuristic scoring."""

    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service

    def _candidates(self) -> list[tuple[str, str, str]]:
        return [
            (
                "The Success Industry Is Selling You an Expensive Illusion",
                "The market rewards leverage, not constant motivation.",
                "People are exhausted by hustle culture but still want financial freedom.",
            ),
            (
                "Why Most People Stay Broke Even With Better Information",
                "Information overload hides system-level constraints and behavioral traps.",
                "Audiences want clarity on why advice does not translate into wealth.",
            ),
            (
                "The Psychology of Wealth: Why Rich Thinking Is Not What You Expect",
                "Wealth behavior is mostly emotional regulation and long-term systems.",
                "Viewers are curious about mindset but distrust generic self-help claims.",
            ),
            (
                "The Dark Economics of Get-Rich Gurus",
                "Many guru business models monetize hope rather than outcomes.",
                "The audience seeks investigative breakdowns with hard tradeoffs.",
            ),
            (
                "Leverage: The Hidden Rule Behind Modern Wealth",
                "Capital, code, media, and networks scale effort asymmetrically.",
                "People care because this reframes success from hustle to structure.",
            ),
        ]

    def _score(self, title: str) -> TopicScore:
        lowered = title.lower()
        curiosity = 7.0
        virality = 7.0
        audience = 7.0
        storytelling = 7.0

        curiosity_terms = ["hidden", "dark", "why", "psychology", "illusion"]
        virality_terms = ["most people", "broke", "success", "wealth", "gurus"]
        storytelling_terms = ["economics", "psychology", "rule", "industry"]

        curiosity += sum(0.5 for term in curiosity_terms if term in lowered)
        virality += sum(0.45 for term in virality_terms if term in lowered)
        storytelling += sum(0.4 for term in storytelling_terms if term in lowered)
        audience += 0.6 if "wealth" in lowered or "success" in lowered else 0.2

        return TopicScore(
            curiosity=min(curiosity, 10),
            virality=min(virality, 10),
            audience_interest=min(audience, 10),
            storytelling_depth=min(storytelling, 10),
        )

    def choose_topic(self) -> TopicCandidate:
        candidates: list[TopicCandidate] = []
        for title, hidden_truth, why_people_care in self._candidates():
            candidates.append(
                TopicCandidate(
                    title=title,
                    hidden_truth=hidden_truth,
                    why_people_care=why_people_care,
                    score=self._score(title),
                )
            )

        candidates.sort(key=lambda c: c.score.total, reverse=True)
        top = candidates[0]

        if self.openai_service.available:
            try:
                system = "You are a YouTube documentary strategist. Improve topic titles for retention and precision."
                user = (
                    "Rewrite this title to be sharper but keep meaning. "
                    "Return only the rewritten title.\n"
                    f"Title: {top.title}"
                )
                improved = self.openai_service.generate_text(system, user)
                if improved and len(improved.split()) >= 5:
                    top.title = improved.strip().strip('"')
            except Exception:
                pass

        return top
