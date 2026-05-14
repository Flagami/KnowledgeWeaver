"""Insight generation from synthesis results using Claude."""

from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from knowledgeweaver.config import settings
from knowledgeweaver.processing.synthesizer import SynthesisResult
from knowledgeweaver.utils.errors import SynthesisError
from knowledgeweaver.utils.logger import logger


@dataclass
class GeneratedInsights:
    """Generated insights from synthesis."""

    insights: list[str]
    future_directions: list[str]
    open_questions: list[str]


class InsightGenerator:
    """Generates high-level insights from synthesis results using Claude."""

    def __init__(self, model: Optional[str] = None):
        """Initialize insight generator.

        Args:
            model: Claude model to use (default: from config)
        """
        self.model = model or settings.anthropic_model
        self.client = Anthropic(
            api_key=settings.anthropic_api_key,
            base_url=settings.anthropic_base_url,
        )
        self.logger = logger

    async def generate(
        self,
        synthesis: SynthesisResult,
        query: str,
    ) -> GeneratedInsights:
        """Generate insights from synthesis results.

        Args:
            synthesis: Synthesis result
            query: Original user query

        Returns:
            Generated insights
        """
        try:
            synthesis_len = len(synthesis.synthesis)
            self.logger.info(
                f"Generating insights | synthesis_chars={synthesis_len}"
                f" | model={self.model}"
            )
            prompt = self._build_insight_prompt(synthesis, query)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            insights = self._parse_insight_response(response_text)
            self.logger.info(
                f"Insights generated"
                f" | insights={len(insights.insights)}"
                f" | future_directions={len(insights.future_directions)}"
                f" | open_questions={len(insights.open_questions)}"
            )
            return insights

        except Exception as e:
            self.logger.warning(
                f"Insight generation FAILED: {type(e).__name__}: {e}"
            )
            # Fallback: extract insights from synthesis
            return self._create_fallback_insights(synthesis)

    def _build_insight_prompt(self, synthesis: SynthesisResult, query: str) -> str:
        """Build insight generation prompt for Claude.

        Args:
            synthesis: Synthesis result
            query: Original user query

        Returns:
            Prompt for Claude
        """
        synthesis_text = f"""Synthesis: {synthesis.synthesis}

Key Insights: {', '.join(synthesis.insights)}

Connections: {', '.join(synthesis.connections)}"""

        return f"""Based on this research synthesis about "{query}":

{synthesis_text}

Generate:
1. 3-5 actionable insights that synthesize the research
2. 2-3 future research directions
3. 2-3 open questions that remain unanswered

Insights should be specific, actionable, and grounded in the research.
Future directions should suggest next steps for research.
Open questions should highlight gaps in current knowledge.

Format your response as JSON with these fields:
- insights: list of insights (strings)
- future_directions: list of future research directions (strings)
- open_questions: list of open questions (strings)

Return ONLY valid JSON, no other text."""

    def _parse_insight_response(self, response_text: str) -> GeneratedInsights:
        """Parse Claude's insight response.

        Args:
            response_text: Claude's response

        Returns:
            Generated insights
        """
        import json

        try:
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            return GeneratedInsights(
                insights=data.get("insights", []),
                future_directions=data.get("future_directions", []),
                open_questions=data.get("open_questions", []),
            )

        except Exception as e:
            self.logger.debug(f"Error parsing insight response: {e}")
            raise SynthesisError(f"Failed to parse insight response: {e}")

    def _create_fallback_insights(self, synthesis: SynthesisResult) -> GeneratedInsights:
        """Create fallback insights from synthesis.

        Args:
            synthesis: Synthesis result

        Returns:
            Generated insights
        """
        return GeneratedInsights(
            insights=synthesis.insights[:5],
            future_directions=[
                "Further research needed to validate findings",
                "Explore applications in related domains",
            ],
            open_questions=[
                "What are the practical implications?",
                "How do these findings scale?",
            ],
        )
