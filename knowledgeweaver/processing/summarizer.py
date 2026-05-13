"""Paper summarization using Claude."""

from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from knowledgeweaver.config import settings
from knowledgeweaver.sources.base import PaperMetadata
from knowledgeweaver.utils.errors import SynthesisError
from knowledgeweaver.utils.logger import logger


@dataclass
class PaperSummary:
    """Summary of a research paper."""

    title: str
    authors: str
    summary: str
    key_points: list[str]
    citations: list[str]


class PaperSummarizer:
    """Summarizes individual papers using Claude."""

    def __init__(self, model: Optional[str] = None):
        """Initialize summarizer.

        Args:
            model: Claude model to use (default: from config)
        """
        self.model = model or settings.anthropic_model
        self.client = Anthropic(
            api_key=settings.anthropic_api_key,
            base_url=settings.anthropic_base_url,
        )
        self.logger = logger

    async def summarize(
        self,
        paper: PaperMetadata,
        text: str,
        depth: str = "medium",
    ) -> PaperSummary:
        """Summarize a paper.

        Args:
            paper: Paper metadata
            text: Paper text content
            depth: Summary depth ('shallow', 'medium', 'deep')

        Returns:
            Paper summary
        """
        try:
            # Limit text to first 8000 characters
            text_excerpt = text[:8000]

            prompt = self._build_summary_prompt(paper, text_excerpt, depth)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            summary = self._parse_summary_response(response.content[0].text, paper)
            self.logger.debug(f"Summarized paper: {paper.source}:{paper.source_id}")
            return summary

        except Exception as e:
            self.logger.error(f"Error summarizing paper: {e}")
            # Fallback: use abstract as summary
            return self._create_fallback_summary(paper)

    def _build_summary_prompt(
        self,
        paper: PaperMetadata,
        text: str,
        depth: str,
    ) -> str:
        """Build summary prompt for Claude.

        Args:
            paper: Paper metadata
            text: Paper text
            depth: Summary depth

        Returns:
            Prompt for Claude
        """
        depth_instructions = {
            "shallow": "Create a brief 1-2 paragraph summary. Extract 2-3 key points.",
            "medium": "Create a 2-3 paragraph summary. Extract 3-5 key points.",
            "deep": "Create a detailed 3-4 paragraph summary. Extract 5-7 key points.",
        }

        instruction = depth_instructions.get(depth, depth_instructions["medium"])

        return f"""Summarize this research paper:

Title: {paper.title}
Authors: {paper.authors}

Content:
{text}

{instruction}

Format your response as JSON with these fields:
- summary: the summary text
- key_points: list of key points (strings)
- citations: list of important citations or references mentioned (strings, can be empty)

Return ONLY valid JSON, no other text."""

    def _parse_summary_response(self, response_text: str, paper: PaperMetadata) -> PaperSummary:
        """Parse Claude's summary response.

        Args:
            response_text: Claude's response
            paper: Paper metadata

        Returns:
            Paper summary
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

            return PaperSummary(
                title=paper.title,
                authors=paper.authors,
                summary=data.get("summary", ""),
                key_points=data.get("key_points", []),
                citations=data.get("citations", []),
            )

        except Exception as e:
            self.logger.debug(f"Error parsing summary response: {e}")
            return self._create_fallback_summary(paper)

    def _create_fallback_summary(self, paper: PaperMetadata) -> PaperSummary:
        """Create fallback summary from abstract.

        Args:
            paper: Paper metadata

        Returns:
            Paper summary
        """
        return PaperSummary(
            title=paper.title,
            authors=paper.authors,
            summary=paper.abstract or "No summary available",
            key_points=[],
            citations=[],
        )
