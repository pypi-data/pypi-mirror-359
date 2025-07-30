import os
import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from codefabric.graph.developer_agent import DeveloperAgent
from codefabric.types.models import Requirements
from codefabric.types.enums import Technologies

console = Console()


class CodeFabricCLI:
    """CLI-based project generator with better UI/UX"""

    def __init__(self):
        self.project_name = ""
        self.project_description = ""
        self.technology = ""

    def display_welcome(self) -> None:
        """Display welcome banner and API key check"""
        console.print(Panel.fit(
            """
╔══════════════════════════════════════════════════════════════════════╗
║ ██████╗ ██████╗ ██████╗ ███████╗ █████╗ ██████╗ ██████╗ ██╗ ██████╗ ║
║ ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██║██╔════╝ ║
║ ██║     ██║   ██║██║  ██║█████╗  ███████║██████╔╝██████╔╝██║██║      ║
║ ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██║██╔══██╗██╔══██╗██║██║      ║
║ ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║██████╔╝██║  ██║██║╚██████╗ ║
║  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ║
║               Professional Project Generator v2.2.0                  ║
╚══════════════════════════════════════════════════════════════════════╝
""",
            title="[bold blue]CodeFabric CLI[/bold blue]",
            border_style="bold blue",
            padding=(1, 2)
        ))

        console.print("[yellow]⚠️  You must set your OpenAI API key in the environment as[/yellow] [bold]OPENAI_API_KEY[/bold]\n")
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[red]❌ Error: OPENAI_API_KEY is not set in environment variables.[/red]")
            raise SystemExit

    def get_project_details(self) -> None:
        """Prompt for basic project details"""
        self.project_name = Prompt.ask(
            "\n[bold blue]📝 Project Name[/bold blue]\n[dim]Enter a unique name for your project[/dim]",
            default="my-awesome-app"
        ).strip()

        if not self.project_name:
            console.print("[red]Project name cannot be empty.[/red]")
            raise SystemExit

        self.project_description = Prompt.ask(
            "\n[bold blue]💡 Project Description[/bold blue]\n[dim]What does your project do?[/dim]",
            default="A new project created with CodeFabric"
        ).strip()

        tech_choices = [tech.value for tech in Technologies]
        self.technology = Prompt.ask(
            "\n[bold blue]💻 Technology Stack[/bold blue]\n[dim]Choose your preferred technology[/dim]",
            choices=tech_choices,
            default=tech_choices[0]
        )

    def show_summary(self) -> bool:
        """Show project summary and confirm creation"""
        console.print(Panel.fit(
            f"[bold green]📦 Project:[/bold green] {self.project_name}\n"
            f"[bold green]🧾 Description:[/bold green] {self.project_description}\n"
            f"[bold green]🧰 Technology:[/bold green] {self.technology}",
            title="[bold]Project Summary[/bold]",
            border_style="green"
        ))
        return Confirm.ask("[bold yellow]🚀 Ready to create the project?[/bold yellow]")

    async def execute_creation(self) -> None:
        """Trigger project creation logic"""
        try:
            agent = DeveloperAgent(
                process_id=self.project_name,
                requirements=Requirements(
                    project_name=self.project_name,
                    project_description=self.project_description,
                    packages=[],
                    technology=self.technology,
                ),
            )
            agent.run()
            console.print(f"\n[bold green]✅ Project '{self.project_name}' created successfully![/bold green]")
        except Exception as e:
            console.print(f"\n[red]❌ Failed to create project: {e}[/red]")

    async def create_project(self) -> None:
        """Main flow controller"""
        self.display_welcome()
        self.get_project_details()

        if not self.show_summary():
            console.print("[yellow]❌ Project creation cancelled by user.[/yellow]")
            return

        await self.execute_creation()


def main():
    cli = CodeFabricCLI()
    asyncio.run(cli.create_project())


if __name__ == "__main__":
    main()
