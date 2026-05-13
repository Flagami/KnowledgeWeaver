"""Domain detection for research queries.

Detects the research domain from user queries and maps to prioritized sources.
"""

from dataclasses import dataclass
from typing import Optional

from knowledgeweaver.utils.logger import logger


@dataclass
class DomainDetectionResult:
    """Result of domain detection."""

    domain: str
    confidence: float
    sources: list[str]


class DomainDetector:
    """Detects research domain from query text."""

    # Domain keywords mapping
    DOMAIN_KEYWORDS = {
        "AI/ML": {
            "keywords": [
                "machine learning",
                "deep learning",
                "neural network",
                "artificial intelligence",
                "ai",
                "ml",
                "nlp",
                "computer vision",
                "transformer",
                "llm",
                "language model",
                "classification",
                "regression",
                "clustering",
                "reinforcement learning",
                "algorithm",
                "model",
                "training",
                "optimization",
            ],
            "sources": ["arxiv", "semantic_scholar", "crossref"],
        },
        "Biology": {
            "keywords": [
                "biology",
                "protein",
                "gene",
                "dna",
                "rna",
                "cell",
                "molecular",
                "genetics",
                "genomics",
                "bioinformatics",
                "enzyme",
                "mutation",
                "evolution",
                "organism",
                "species",
                "biomedical",
                "pharmaceutical",
                "drug",
            ],
            "sources": ["pubmed", "crossref", "semantic_scholar"],
        },
        "Physics": {
            "keywords": [
                "physics",
                "quantum",
                "relativity",
                "particle",
                "photon",
                "electron",
                "atom",
                "molecule",
                "force",
                "energy",
                "wave",
                "field",
                "mechanics",
                "thermodynamics",
                "electromagnetism",
                "gravity",
                "cosmology",
            ],
            "sources": ["arxiv", "crossref", "semantic_scholar"],
        },
        "Chemistry": {
            "keywords": [
                "chemistry",
                "chemical",
                "compound",
                "reaction",
                "molecule",
                "atom",
                "element",
                "bond",
                "catalyst",
                "synthesis",
                "organic",
                "inorganic",
                "polymer",
                "material",
            ],
            "sources": ["crossref", "semantic_scholar", "arxiv"],
        },
        "Medicine": {
            "keywords": [
                "medicine",
                "medical",
                "disease",
                "treatment",
                "therapy",
                "clinical",
                "patient",
                "diagnosis",
                "symptom",
                "drug",
                "vaccine",
                "surgery",
                "health",
            ],
            "sources": ["pubmed", "crossref", "semantic_scholar"],
        },
    }

    # Default sources for unknown domains
    DEFAULT_SOURCES = ["semantic_scholar", "crossref", "arxiv"]

    def __init__(self):
        """Initialize domain detector."""
        self.logger = logger

    def detect(self, query: str) -> DomainDetectionResult:
        """Detect domain from query text.

        Args:
            query: User query text

        Returns:
            DomainDetectionResult with detected domain, confidence, and sources
        """
        query_lower = query.lower()
        scores = {}

        # Score each domain based on keyword matches
        for domain, config in self.DOMAIN_KEYWORDS.items():
            keyword_matches = sum(
                1 for keyword in config["keywords"] if keyword in query_lower
            )
            if keyword_matches > 0:
                scores[domain] = keyword_matches

        if not scores:
            # No domain detected, use defaults
            self.logger.debug(f"No domain detected for query: {query}")
            return DomainDetectionResult(
                domain="General",
                confidence=0.0,
                sources=self.DEFAULT_SOURCES,
            )

        # Find best matching domain
        best_domain = max(scores, key=scores.get)
        best_score = scores[best_domain]

        # Calculate confidence (0-1)
        max_possible_score = len(self.DOMAIN_KEYWORDS[best_domain]["keywords"])
        confidence = min(best_score / max_possible_score, 1.0)

        sources = self.DOMAIN_KEYWORDS[best_domain]["sources"]

        self.logger.debug(
            f"Detected domain: {best_domain} (confidence: {confidence:.2f}) for query: {query}"
        )

        return DomainDetectionResult(
            domain=best_domain,
            confidence=confidence,
            sources=sources,
        )

    def get_sources(self, domain: str) -> list[str]:
        """Get prioritized sources for a domain.

        Args:
            domain: Domain name

        Returns:
            List of source names in priority order
        """
        if domain in self.DOMAIN_KEYWORDS:
            return self.DOMAIN_KEYWORDS[domain]["sources"]
        return self.DEFAULT_SOURCES

    def get_supported_domains(self) -> list[str]:
        """Get list of supported domains.

        Returns:
            List of domain names
        """
        return list(self.DOMAIN_KEYWORDS.keys())
