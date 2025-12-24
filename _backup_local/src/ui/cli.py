from rich.console import Console
from rich.markdown import Markdown
from rich import print as rprint
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live
import time
from src.core.io import InputProvider, OutputDisplay

class RichOutputDisplay(OutputDisplay):
    def __init__(self):
        self.console = Console()

    def display(self, message: str) -> None:
        # Render markdown for nice AI formatting
        self.console.print(Panel(
            Markdown(message), 
            title="🎭 던전 마스터", 
            border_style="blue",
            padding=(1, 2)
        ))

    def display_system(self, message: str) -> None:
        self.console.print(f"[bold yellow]{message}[/bold yellow]")
    
    def show_spinner(self, message: str = "생각 중..."):
        """Show a spinner with message"""
        return self.console.status(f"[bold green]{message}[/bold green]", spinner="dots")

class ConsoleInputProvider(InputProvider):
    def __init__(self):
        self.console = Console()

    def get_input(self, prompt: str = "") -> str:
        # Use Rich's prompt for better UX
        return Prompt.ask(f"[bold cyan]🎮 {prompt}[/bold cyan]")

