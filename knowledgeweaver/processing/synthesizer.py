"""Cross-reference synthesis of multiple papers using Claude."""

from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from knowledgeweaver.config import settings
from knowledgeweaver.processing.summarizer import PaperSummary
from knowledgeweaver.utils.errors import SynthesisError
from knowledgeweaver.utils.logger import logger


@dataclass
class SynthesisResult:
    """Result of synthesizing multiple papers."""

    synthesis: str
    insights: list[str]
    connections: list[str]
    citations: list[str]


class PaperSynthesizer:
    """Synthesizes findings across multiple papers using Claude."""

    def __init__(self, model: Optional[str] = None):
        """Initialize synthesizer.

        Args:
            model: Claude model to use (default: from config)
        """
        self.model = model or settings.llm_model
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.logger = logger

    async def synthesize(
        self,
        papers: list[PaperSummary],
        depth: str = "medium",
        max_retries: int = 2,
    ) -> SynthesisResult:
        """Synthesize findings across papers.

        Args:
            papers: List of paper summaries
            depth: Synthesis depth ('shallow', 'medium', 'deep')
            max_retries: Maximum retry attempts on failure

        Returns:
            Synthesis result
        """
        if not papers:
            raise ValueError("No papers to synthesize")

        try:
            prompt = self._build_synthesis_prompt(papers, depth)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            result = self._parse_synthesis_response(response.content[0].text)
            self.logger.debug(f"Synthesized {len(papers)} papers")
            return result

        except Exception as e:
            self.logger.error(f"Error synthesizing papers: {e}")

            # Retry with simpler prompt
            if max_retries > 0:
                self.logger.info("Retrying synthesis with simpler prompt")
                return await self._synthesize_simple(papers)

            raise SynthesisError(f"Synthesis failed: {e}")

    async def _synthesize_simple(self, papers: list[PaperSummary]) -> SynthesisResult:
        """Fallback simple synthesis.

        Args:
            papers: List of paper summaries

        Returns:
            Synthesis result
        """
        try:
            prompt = self._build_simple_synthesis_prompt(papers)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            result = self._parse_synthesis_response(response.content[0].text)
            return result

        except Exception as e:
            self.logger.error(f"Simple synthesis also failed: {e}")
            # Return basic synthesis from summaries
            return self._create_fallback_synthesis(papers)

    def _build_synthesis_prompt(self, papers: list[PaperSummary], depth: str) -> str:
        """Build synthesis prompt for Claude.

        Args:
            papers: Paper summaries
            depth: Synthesis depth

        Returns:
            Prompt for Claude
        """
        depth_instructions = {
            "shallow": "Provide a brief 1-2 paragraph synthesis. Extract 2-3 key insights.",
            "medium": "Provide a 2-3 paragraph synthesis. Extract 3-5 key insights and connections.",
            "deep": "Provide a detailed 3-4 paragraph synthesis. Extract 5-7 insights and connections.",
        }

        instruction = depth_instructions.get(depth, depth_instructions["medium"])

        papers_text = "\n\n".join(
            [
                f"Paper {i+1}: {paper.title}\nAuthors: {paper.authors}\nSummary: {paper.summary}"
                for i, paper in enumerate(papers)
            ]
        )

        return f"""Synthesize findings from these research papers:

{papers_text}

{instruction}

Identify connections between papers and cross-cutting themes.

Format your response as JSON with these fields:
- synthesis: the synthesis text
- insights: list of key insights across papers (strings)
- connections: list of connections between papers (strings)
- citations: list of important citations (strings)

Return ONLY valid JSON, no other text."""

    def _build_simple_synthesis_prompt(self, papers: list[PaperSummary]) -> str:
        """Build simple synthesis prompt.

        Args:
            papers: Paper summaries

        Returns:
            Prompt for Claude
        """
        papers_text = "\n".join(
            [f"- {paper.title}: {paper.summary[:200]}" for paper in papers]
        )

        return f"""Summarize the main themes from these papers:

{papers_text}

Provide a brief synthesis and list key themes.

Format as JSON with: synthesis (string), insights (list), connections (list), citations (list)"""

    def _parse_synthesis_response(self, response_text: str) -> SynthesisResult:
        """Parse Claude's synthesis response.

        Args:
            response_text: Claude's response

        Returns:
            Synthesis result
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

            return SynthesisResult(
                synthesis=data.get("synthesis", ""),
                insights=data.get("insights", []),
                connections=data.get("connections", []),
                citations=data.get("citations", []),
            )

        except Exception as e:
            self.logger.debug(f"Error parsing synthesis response: {e}")
            raise SynthesisError(f"Failed to parse synthesis response: {e}")

    def _create_fallback_synthesis(self, papers: list[PaperSummary]) -> SynthesisResult:
        """Create fallback synthesis from paper summaries.

        Args:
            papers: Paper summaries

        Returns:
            Synthesis result
        """
        synthesis = f"Synthesis of {len(papers)} papers:\n\n"
        synthesis += "\n\n".join([f"- {p.title}: {p.summary[:100]}" for p in papers])

        all_insights = []
        for paper in papers:
            all_insights.extend(paper.key_points[:2])

        all_citations = []
        for paper in papers:
            all_citations.extend(paper.citations[:2])

        return SynthesisResult(
            synthesis=synthesis,
            insights=all_insights[:5],
            connections=[],
            citations=all_citations[:5],
        )
