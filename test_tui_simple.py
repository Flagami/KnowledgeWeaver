"""Simple TUI test to verify textual framework works on macOS."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static
from textual.app import App


class WelcomeScreen(Screen):
    """Welcome screen for testing."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the welcome screen."""
        yield Header(show_clock=True)
        yield Container(
            Vertical(
                Label("[bold cyan]KnowledgeWeaver TUI Test[/bold cyan]"),
                Label(""),
                Label("[green]✓ Textual framework is working![/green]"),
                Label(""),
                Label("This is a simple test to verify the TUI works on your Mac."),
                Label(""),
                Label("[yellow]Press 'q' to quit[/yellow]"),
            )
        )
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class TestApp(App):
    """Simple test application."""

    TITLE = "KnowledgeWeaver TUI Test"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        print("✓ App mounted successfully")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


if __name__ == "__main__":
    print("🚀 Starting KnowledgeWeaver TUI Test...")
    print("📝 If you see a terminal UI below, the textual framework is working!")
    print("⌨️  Press 'q' to quit\n")

    app = TestApp()
    app.run()

    print("\n✅ Test completed successfully!")
