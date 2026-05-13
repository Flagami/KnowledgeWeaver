"""TUI application for KnowledgeWeaver using textual framework."""

from textual.app import ComposeResult, on
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static, TextArea
from textual.binding import Binding

from knowledgeweaver.core.query_manager import QueryManager
from knowledgeweaver.core.synthesis_pipeline import SynthesisPipeline
from knowledgeweaver.utils.logger import logger


class QueryInputWidget(Static):
    """Widget for query input."""

    class QuerySubmitted(Message):
        """Message when query is submitted."""

        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class ShowHistory(Message):
        """Message to show history."""

        pass

    def compose(self) -> ComposeResult:
        """Compose the query input widget."""
        yield Label("Enter your research query:")
        yield Input(
            id="query_input",
            placeholder="e.g., quantum computing applications",
        )
        yield Horizontal(
            Button("Search", id="search_btn", variant="primary"),
            Button("Clear", id="clear_btn"),
            Button("History", id="history_btn"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search_btn":
            query_input = self.query_by_id("query_input", Input)
            if query_input.value:
                self.post_message(self.QuerySubmitted(query_input.value))
        elif event.button.id == "clear_btn":
            query_input = self.query_by_id("query_input", Input)
            query_input.value = ""
        elif event.button.id == "history_btn":
            self.post_message(self.ShowHistory())


class StatusPanel(Static):
    """Panel showing processing status."""

    def render(self) -> str:
        """Render the status panel."""
        return """
[bold cyan]KnowledgeWeaver - Research Synthesis System[/bold cyan]

[yellow]Status:[/yellow] Ready
[yellow]Active Queries:[/yellow] 0
[yellow]Completed:[/yellow] 0

Press [bold]Ctrl+C[/bold] to exit
        """


class ResultsPanel(Static):
    """Panel showing results."""

    def render(self) -> str:
        """Render the results panel."""
        return """
[bold]Results[/bold]

No results yet. Submit a query to begin.
        """


class HistoryPanel(Static):
    """Panel showing query history."""

    def render(self) -> str:
        """Render the history panel."""
        return """
[bold]Query History[/bold]

No history yet.
        """


class KnowledgeWeaverApp:
    """Main TUI application for KnowledgeWeaver."""

    def __init__(self):
        """Initialize the application."""
        self.query_manager = QueryManager()
        self.pipeline = SynthesisPipeline()
        self.logger = logger

    async def run_query(self, query_text: str) -> None:
        """Run a query through the pipeline.

        Args:
            query_text: Query text to process
        """
        try:
            # Submit query
            query = await self.query_manager.submit_query(query_text)
            self.logger.info(f"Processing query: {query.query_id}")

            # Start processing
            await self.query_manager.start_processing(query)

            # Run pipeline
            result_path = await self.pipeline.process(query, depth="medium")

            # Complete query
            await self.query_manager.complete_query(query, result_path=result_path)
            self.logger.info(f"Query completed: {query.query_id}")

        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            await self.query_manager.fail_query(query, str(e))

    def get_status(self) -> dict:
        """Get current status.

        Returns:
            Status dictionary
        """
        stats = self.query_manager.get_stats()
        return {
            "pending": stats["pending"],
            "active": stats["active"],
            "completed": stats["completed"],
            "max_concurrent": stats["max_concurrent"],
        }

    def get_history(self, limit: int = 10) -> list:
        """Get query history.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of completed queries
        """
        queries = self.query_manager.get_completed_queries(limit=limit)
        return [
            {
                "query": q.query_text,
                "domain": q.domain,
                "time": f"{q.processing_time_seconds:.2f}s",
                "status": q.status.value,
            }
            for q in queries
        ]


class KnowledgeWeaverScreen(Screen):
    """Main screen for KnowledgeWeaver TUI."""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+h", "show_history", "History"),
    ]

    def __init__(self):
        """Initialize the screen."""
        super().__init__()
        self.app_controller = KnowledgeWeaverApp()

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        yield Container(
            Vertical(
                StatusPanel(id="status_panel"),
                QueryInputWidget(id="query_input_widget"),
                ResultsPanel(id="results_panel"),
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        self.title = "KnowledgeWeaver - Research Synthesis System"
        self.logger = logger

    def action_show_history(self) -> None:
        """Show query history."""
        history = self.app_controller.get_history()
        history_text = "[bold]Query History[/bold]\n\n"
        for i, q in enumerate(history, 1):
            history_text += f"{i}. {q['query'][:50]}\n"
            history_text += f"   Domain: {q['domain']}, Time: {q['time']}\n\n"

        history_panel = self.query_one("#results_panel", ResultsPanel)
        history_panel.update(history_text)

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
