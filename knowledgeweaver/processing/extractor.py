"""Key findings extraction from research papers using Claude."""

from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from knowledgeweaver.config import settings
from knowledgeweaver.sources.base import PaperMetadata
from knowledgeweaver.utils.errors import ExtractionError
from knowledgeweaver.utils.logger import logger


@dataclass
class ExtractedFindings:
    """Extracted findings from a paper."""

    key_findings: list[str]
    methodology: str
    conclusions: str
    limitations: str


class KeyFindingsExtractor:
    """Extracts key findings from research papers using Claude."""

    def __init__(self, model: Optional[str] = None):
        """Initialize extractor.

        Args:
            model: Claude model to use (default: from config)
        """
        self.model = model or settings.llm_model
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.logger = logger

    async def extract(
        self,
        paper: PaperMetadata,
        text: str,
        depth: str = "medium",
    ) -> ExtractedFindings:
        """Extract key findings from paper text.

        Args:
            paper: Paper metadata
            text: Paper text content
            depth: Extraction depth ('shallow', 'medium', 'deep')

        Returns:
            Extracted findings
        """
        try:
            # Limit text to first 8000 characters to avoid token limits
            text_excerpt = text[:8000]

            prompt = self._build_extraction_prompt(paper, text_excerpt, depth)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            findings = self._parse_extraction_response(response.content[0].text)
            self.logger.debug(
                f"Extracted findings from {paper.source}:{paper.source_id}"
            )
            return findings

        except Exception as e:
            self.logger.error(
                f"Error extracting findings from {paper.source}:{paper.source_id}: {e}"
            )
            # Fallback: return basic extraction from abstract
            return self._extract_from_abstract(paper)

    def _build_extraction_prompt(
        self,
        paper: PaperMetadata,
        text: str,
        depth: str,
    ) -> str:
        """Build extraction prompt for Claude.

        Args:
            paper: Paper metadata
            text: Paper text
            depth: Extraction depth

        Returns:
            Prompt for Claude
        """
        depth_instructions = {
            "shallow": "Extract 2-3 key findings only. Keep methodology and conclusions brief.",
            "medium": "Extract 3-5 key findings. Include moderate detail on methodology and conclusions.",
            "deep": "Extract 5-7 key findings with detailed methodology and conclusions. Include limitations.",
        }

        instruction = depth_instructions.get(depth, depth_instructions["medium"])

        return f"""Extract key findings from this research paper:

Title: {paper.title}
Authors: {paper.authors}

Paper Content:
{text}

{instruction}

Format your response as JSON with these fields:
- key_findings: list of 2-7 key findings (strings)
- methodology: brief description of research methodology
- conclusions: main conclusions of the research
- limitations: limitations and future work (can be empty for shallow)

Return ONLY valid JSON, no other text."""

    def _parse_extraction_response(self, response_text: str) -> ExtractedFindings:
        """Parse Claude's extraction response.

        Args:
            response_text: Claude's response

        Returns:
            Extracted findings
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

            return ExtractedFindings(
                key_findings=data.get("key_findings", []),
                methodology=data.get("methodology", ""),
                conclusions=data.get("conclusions", ""),
                limitations=data.get("limitations", ""),
            )

        except Exception as e:
            self.logger.debug(f"Error parsing extraction response: {e}")
            raise ExtractionError(f"Failed to parse extraction response: {e}")

    def _extract_from_abstract(self, paper: PaperMetadata) -> ExtractedFindings:
        """Fallback extraction from abstract.

        Args:
            paper: Paper metadata

        Returns:
            Basic extracted findings
        """
        abstract = paper.abstract or ""
        sentences = abstract.split(". ")

        # Simple extraction: first 3 sentences as findings
        key_findings = [s.strip() for s in sentences[:3] if s.strip()]

        return ExtractedFindings(
            key_findings=key_findings,
            methodology="See abstract",
            conclusions="See abstract",
            limitations="",
        )
