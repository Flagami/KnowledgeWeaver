"""HTML generation for research synthesis results."""

import html
import math
from datetime import datetime
from pathlib import Path

from knowledgeweaver.config import settings
from knowledgeweaver.processing.insight_generator import GeneratedInsights
from knowledgeweaver.processing.synthesizer import SynthesisResult
from knowledgeweaver.utils.logger import logger


class HTMLGenerator:
    """Generates interactive HTML reports from synthesis results."""

    def __init__(self):
        """Initialize HTML generator."""
        self.logger = logger
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        query: str,
        synthesis: SynthesisResult,
        insights: GeneratedInsights,
        domain: str = "General",
        query_id: str = "",
    ) -> str:
        """Generate HTML report from synthesis results.

        Args:
            query: Original user query
            synthesis: Synthesis result
            insights: Generated insights
            domain: Research domain
            query_id: Optional query identifier for filename and feedback

        Returns:
            Path to generated HTML file
        """
        try:
            html_content = self._build_html(query, synthesis, insights, domain, query_id)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if query_id:
                filename = f"research_{query_id[:8]}_{timestamp}.html"
            else:
                filename = f"research_{timestamp}.html"

            filepath = self.output_dir / filename
            filepath.write_text(html_content, encoding="utf-8")
            self.logger.info(f"Generated HTML report: {filepath}")

            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error generating HTML: {e}")
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _estimate_reading_time(
        self, synthesis: SynthesisResult, insights: GeneratedInsights
    ) -> int:
        """Estimate reading time in minutes (200 wpm)."""
        text = " ".join(
            [synthesis.synthesis]
            + insights.insights
            + synthesis.connections
        )
        words = len(text.split())
        return max(1, math.ceil(words / 200))

    def _build_html(
        self,
        query: str,
        synthesis: SynthesisResult,
        insights: GeneratedInsights,
        domain: str,
        query_id: str = "",
    ) -> str:
        """Assemble the full HTML document."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        safe_query = html.escape(query)
        safe_domain = html.escape(domain)
        safe_query_id = html.escape(query_id)
        citation_count = len(synthesis.citations)
        reading_time = self._estimate_reading_time(synthesis, insights)

        hero = self._build_hero(safe_query, safe_domain, citation_count, timestamp, reading_time)
        toc = self._build_toc()
        summary_section = self._build_summary_section(synthesis.synthesis)
        insights_section = self._build_insights_section(insights.insights)
        connections_section = self._build_connections_section(synthesis.connections)
        future_section = self._build_future_section(
            insights.future_directions, insights.open_questions
        )
        references_section = self._build_references_section(synthesis.citations)
        feedback_section = self._build_feedback_section()
        css = self._get_css()
        js = self._get_javascript(safe_query_id)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Research: {safe_query}</title>
  <style>
{css}
  </style>
</head>
<body>
  <div id="progress-bar"></div>
  {hero}
  <div class="page-layout">
    {toc}
    <main>
      {summary_section}
      {insights_section}
      {connections_section}
      {future_section}
      {references_section}
    </main>
  </div>
  {feedback_section}
  <script>
{js}
  </script>
</body>
</html>"""

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _build_hero(
        self,
        safe_query: str,
        safe_domain: str,
        citation_count: int,
        timestamp: str,
        reading_time: int,
    ) -> str:
        return f"""  <header class="hero">
    <div class="domain-badge">{safe_domain}</div>
    <h1>{safe_query}</h1>
    <div class="meta">
      <span>&#128196; {citation_count} sources analyzed</span>
      <span>&#128336; {timestamp}</span>
      <span>&#9201; ~{reading_time} min read</span>
    </div>
  </header>"""

    def _build_toc(self) -> str:
        items = [
            ("#summary", "Executive Summary"),
            ("#insights", "Key Insights"),
            ("#connections", "Key Connections"),
            ("#future", "Future &amp; Questions"),
            ("#references", "References"),
        ]
        links = "\n".join(
            f'      <li><a href="{href}" class="toc-link">{label}</a></li>'
            for href, label in items
        )
        return f"""  <nav class="toc" aria-label="Table of contents">
    <p class="toc-title">Contents</p>
    <ul>
{links}
    </ul>
  </nav>"""

    def _build_summary_section(self, synthesis_text: str) -> str:
        safe = html.escape(synthesis_text)
        return f"""      <section id="summary">
        <h2>Executive Summary</h2>
        <div class="summary-card">{safe}</div>
      </section>"""

    def _build_insights_section(self, insights: list[str]) -> str:
        if not insights:
            return ""
        cards = ""
        icons = ["&#128161;", "&#128269;", "&#9889;", "&#127919;", "&#128200;",
                 "&#128640;", "&#128300;", "&#9881;", "&#128214;", "&#127775;"]
        for i, insight in enumerate(insights):
            icon = icons[i % len(icons)]
            safe = html.escape(insight)
            cards += f"""        <div class="insight-card">
          <div class="insight-number">{icon} {i + 1}</div>
          <p>{safe}</p>
        </div>\n"""
        return f"""      <section id="insights">
        <h2>Key Insights</h2>
        <div class="insight-grid">
{cards}        </div>
      </section>"""

    def _build_connections_section(self, connections: list[str]) -> str:
        if not connections:
            return ""
        items = "\n".join(
            f'        <li><span class="conn-arrow">&#8594;</span> {html.escape(c)}</li>'
            for c in connections
        )
        return f"""      <section id="connections">
        <h2>Key Connections</h2>
        <ul class="connections-list">
{items}
        </ul>
      </section>"""

    def _build_future_section(
        self, future_directions: list[str], open_questions: list[str]
    ) -> str:
        future_items = "\n".join(
            f"          <li>{html.escape(d)}</li>" for d in future_directions
        )
        question_items = "\n".join(
            f"          <li>{html.escape(q)}</li>" for q in open_questions
        )
        return f"""      <section id="future">
        <div class="two-col">
          <div>
            <h2>Future Directions</h2>
            <ul class="future-list">
{future_items}
            </ul>
          </div>
          <div>
            <h2>Open Questions</h2>
            <ul class="questions-list">
{question_items}
            </ul>
          </div>
        </div>
      </section>"""

    def _build_references_section(self, citations: list[str]) -> str:
        if not citations:
            return ""
        items = "\n".join(
            f"        <li>{html.escape(c)}</li>" for c in citations
        )
        return f"""      <section id="references">
        <h2>References</h2>
        <ol class="citations">
{items}
        </ol>
      </section>"""

    def _build_feedback_section(self) -> str:
        return """  <footer class="feedback-section">
    <div id="feedback-form">
      <h3>Help improve future research</h3>
      <p>How useful was this synthesis?</p>
      <div class="stars" id="star-container">
        <span class="star" data-rating="1">&#9733;</span>
        <span class="star" data-rating="2">&#9733;</span>
        <span class="star" data-rating="3">&#9733;</span>
        <span class="star" data-rating="4">&#9733;</span>
        <span class="star" data-rating="5">&#9733;</span>
      </div>
      <textarea id="feedback-text" placeholder="What could be improved? (optional)"></textarea>
      <button onclick="submitFeedback()">Submit Feedback</button>
    </div>
    <p class="footer-brand">Generated by KnowledgeWeaver</p>
  </footer>"""

    # ------------------------------------------------------------------
    # CSS
    # ------------------------------------------------------------------

    def _get_css(self) -> str:
        return """
    /* Reset & base */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f8fafc;
      color: #1e293b;
      line-height: 1.7;
    }

    /* Reading progress bar */
    #progress-bar {
      position: fixed;
      top: 0; left: 0;
      height: 3px;
      width: 0%;
      background: linear-gradient(135deg, #4f46e5, #7c3aed);
      z-index: 1000;
      transition: width 0.1s linear;
    }

    /* Hero */
    .hero {
      background: linear-gradient(135deg, #4f46e5, #7c3aed);
      color: #fff;
      padding: 56px 40px 48px;
    }
    .domain-badge {
      display: inline-block;
      background: rgba(255,255,255,0.2);
      border: 1px solid rgba(255,255,255,0.35);
      border-radius: 20px;
      padding: 4px 14px;
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 16px;
    }
    .hero h1 {
      font-size: clamp(1.6rem, 4vw, 2.6rem);
      font-weight: 700;
      line-height: 1.25;
      margin-bottom: 20px;
      max-width: 820px;
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      font-size: 0.88rem;
      opacity: 0.88;
    }

    /* Page layout: TOC sidebar + main */
    .page-layout {
      display: flex;
      align-items: flex-start;
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 24px;
      gap: 36px;
    }

    /* TOC */
    .toc {
      position: sticky;
      top: 20px;
      flex: 0 0 200px;
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 20px;
      font-size: 0.85rem;
    }
    .toc-title {
      font-weight: 700;
      font-size: 0.75rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #64748b;
      margin-bottom: 12px;
    }
    .toc ul { list-style: none; }
    .toc li { margin: 6px 0; }
    .toc-link {
      color: #4f46e5;
      text-decoration: none;
      display: block;
      padding: 4px 8px;
      border-radius: 6px;
      transition: background 0.15s, color 0.15s;
    }
    .toc-link:hover { background: #ede9fe; color: #3730a3; }

    /* Main content */
    main { flex: 1; min-width: 0; }
    section { margin-bottom: 48px; }
    section h2 {
      font-size: 1.35rem;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid #e2e8f0;
    }

    /* Summary card */
    .summary-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #4f46e5;
      border-radius: 10px;
      padding: 28px 32px;
      font-size: 1.05rem;
      line-height: 1.8;
      box-shadow: 0 2px 8px rgba(79,70,229,0.06);
    }

    /* Insight grid */
    .insight-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }
    .insight-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #4f46e5;
      border-radius: 10px;
      padding: 20px 22px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
      transition: transform 0.15s, box-shadow 0.15s;
    }
    .insight-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(79,70,229,0.1);
    }
    .insight-number {
      font-size: 0.8rem;
      font-weight: 700;
      color: #4f46e5;
      margin-bottom: 8px;
      letter-spacing: 0.04em;
    }
    .insight-card p { font-size: 0.95rem; color: #334155; }

    /* Connections list */
    .connections-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .connections-list li {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px 18px;
      font-size: 0.95rem;
      display: flex;
      align-items: flex-start;
      gap: 10px;
      transition: background 0.15s;
    }
    .connections-list li:hover { background: #f1f5f9; }
    .conn-arrow { color: #4f46e5; font-size: 1.1rem; flex-shrink: 0; margin-top: 1px; }

    /* Two-column future/questions */
    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 28px;
    }
    .future-list, .questions-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .future-list li, .questions-list li {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px 16px;
      font-size: 0.93rem;
      position: relative;
      padding-left: 28px;
    }
    .future-list li::before {
      content: "\\2192";
      position: absolute;
      left: 10px;
      color: #059669;
      font-weight: 700;
    }
    .questions-list li::before {
      content: "?";
      position: absolute;
      left: 12px;
      color: #7c3aed;
      font-weight: 700;
    }

    /* Citations */
    .citations {
      padding-left: 22px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .citations li {
      font-size: 0.88rem;
      color: #475569;
      line-height: 1.6;
      padding: 8px 12px;
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
    }

    /* Feedback footer */
    .feedback-section {
      background: #fff;
      border-top: 1px solid #e2e8f0;
      padding: 48px 40px 36px;
      text-align: center;
    }
    .feedback-section h3 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 8px;
    }
    .feedback-section > p {
      color: #64748b;
      margin-bottom: 20px;
    }
    .stars {
      display: flex;
      justify-content: center;
      gap: 8px;
      font-size: 2.2rem;
      margin-bottom: 20px;
    }
    .star { cursor: pointer; color: #cbd5e1; transition: color 0.15s, transform 0.1s; }
    .star:hover, .star.active { color: #f59e0b; }
    .star:hover { transform: scale(1.15); }
    #feedback-text {
      display: block;
      width: 100%;
      max-width: 520px;
      margin: 0 auto 16px;
      padding: 12px 14px;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.93rem;
      resize: vertical;
      min-height: 90px;
      color: #1e293b;
    }
    #feedback-text:focus { outline: 2px solid #4f46e5; border-color: transparent; }
    .feedback-section button {
      background: linear-gradient(135deg, #4f46e5, #7c3aed);
      color: #fff;
      border: none;
      padding: 11px 28px;
      border-radius: 8px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.1s;
    }
    .feedback-section button:hover { opacity: 0.9; transform: translateY(-1px); }
    .footer-brand {
      margin-top: 28px;
      font-size: 0.8rem;
      color: #94a3b8;
    }
    .thanks { color: #059669; font-weight: 600; font-size: 1.05rem; padding: 20px 0; }

    /* Responsive */
    @media (max-width: 768px) {
      .hero { padding: 36px 20px 32px; }
      .page-layout { flex-direction: column; padding: 24px 16px; }
      .toc { position: static; flex: none; width: 100%; }
      .two-col { grid-template-columns: 1fr; }
      .feedback-section { padding: 36px 20px 28px; }
    }

    /* Print */
    @media print {
      #progress-bar, .toc, .feedback-section { display: none !important; }
      .hero { background: #4f46e5 !important; -webkit-print-color-adjust: exact; }
      .page-layout { padding: 20px 0; }
    }"""

    # ------------------------------------------------------------------
    # JavaScript
    # ------------------------------------------------------------------

    def _get_javascript(self, safe_query_id: str) -> str:
        return f"""    const QUERY_ID = "{safe_query_id}";
    const API_BASE = window.location.origin;

    // Reading progress bar
    window.addEventListener('scroll', () => {{
      const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      const bar = document.getElementById('progress-bar');
      if (bar) bar.style.width = Math.min(scrolled, 100) + '%';
    }});

    // Smooth scroll for TOC links
    document.querySelectorAll('.toc-link').forEach(link => {{
      link.addEventListener('click', e => {{
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }});
    }});

    // Star rating
    let selectedRating = 0;
    const stars = document.querySelectorAll('.star');

    stars.forEach(star => {{
      star.addEventListener('click', function () {{
        selectedRating = parseInt(this.dataset.rating);
        updateStars(selectedRating);
      }});
      star.addEventListener('mouseenter', function () {{
        updateStars(parseInt(this.dataset.rating));
      }});
    }});

    document.getElementById('star-container')?.addEventListener('mouseleave', () => {{
      updateStars(selectedRating);
    }});

    function updateStars(rating) {{
      stars.forEach(s => {{
        s.classList.toggle('active', parseInt(s.dataset.rating) <= rating);
      }});
    }}

    // Feedback submission
    async function submitFeedback() {{
      if (!selectedRating) {{
        alert('Please select a rating before submitting.');
        return;
      }}
      const text = document.getElementById('feedback-text')?.value || '';
      try {{
        const resp = await fetch(API_BASE + '/api/feedback', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ query_id: QUERY_ID, rating: selectedRating, feedback_text: text }})
        }});
        if (resp.ok) {{
          document.getElementById('feedback-form').innerHTML =
            '<p class="thanks">Thank you for your feedback!</p>';
        }} else {{
          alert('Could not submit feedback. Please try again.');
        }}
      }} catch (e) {{
        console.error('Feedback submission failed:', e);
        alert('Could not submit feedback. Please try again.');
      }}
    }}"""
