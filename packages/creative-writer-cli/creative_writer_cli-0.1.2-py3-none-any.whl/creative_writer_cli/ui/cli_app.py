import questionary
from rich.console import Console
import json
import os

from ..data.repositories.project_repository import ProjectRepository
from ..core.templates import TEMPLATES
from .wizards.generic_wizards import prompt_for_project_directory
from ..utils import config_manager
from .ascii_art import get_ascii_art
from .services.project_interaction_service import ProjectInteractionService

console = Console()

class CLIApp:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository
        self.console = Console()
        self.project_interaction_service = ProjectInteractionService(project_repository, self.console)

    def main_menu(self):
        self.console.print(get_ascii_art())
        while True:
            choice = questionary.select(
                "What do you want to do?",
                choices=["Create New Project", "View Existing Projects", "Delete Project", "Configure Project Directory", "Exit"]
            ).ask()

            if choice == "Create New Project":
                self.create_project()
            elif choice == "View Existing Projects":
                self.view_projects()
            elif choice == "Delete Project":
                self.delete_project()
            elif choice == "Configure Project Directory":
                self._configure_project_directory()
            elif choice == "Exit" or choice is None:
                if questionary.confirm("Are you sure you want to exit? This will close the application.").ask():
                    break
                else:
                    continue # If user says no, continue the loop and show main menu again

    def _configure_project_directory(self):
        self.console.print("\n[bold]Configure Project Directory[/bold]")
        new_path = prompt_for_project_directory(self.project_repository.base_dir)
        if new_path is None: # User cancelled (Ctrl+C)
            self.console.print("[yellow]Project directory configuration cancelled.[/yellow]")
            return
        
        if new_path != self.project_repository.base_dir: # Only update if path actually changed
            config_manager.set_project_directory_in_config(new_path)
            self.project_repository.base_dir = new_path # Update the repository's base_dir immediately
            self.console.print(f"[green]Project directory set to: {new_path}[/green]")
        else:
            self.console.print("[yellow]Project directory remains unchanged.[/yellow]")

    def _validate_project_directory(self):
        if not os.path.exists(self.project_repository.base_dir) or not os.path.isdir(self.project_repository.base_dir):
            self.console.print("[bold red]Error: Could not open specified project folder. Please configure project directory.[/bold red]")
            return False
        return True

    def create_project(self):
        if not self._validate_project_directory():
            return

        project_type = questionary.select(
            "What type of writing?",
            choices=list(TEMPLATES.keys())
        ).ask()

        if project_type is None:
            return

        project_name = questionary.text("Enter project name:").ask()

        if not project_name:
            self.console.print("[bold red]Project name cannot be empty.[/bold red]")
            return

        success, message = self.project_repository.create_project(project_name, project_type)

        if success:
            self.console.print(f"[bold green]{message}[/bold green]")
            # Initial input for Novel projects
            if project_type == "Novel":
                initial_input_choice = questionary.select(
                    "Initial input",
                    choices=["Plot", "Characters", "skip to template overview"]
                ).ask()

                if initial_input_choice and initial_input_choice != "skip to template overview":
                    self.project_interaction_service.edit_section(project_name, initial_input_choice)
        else:
            self.console.print(f"[bold red]{message}[/bold red]")

    def view_projects(self):
        if not self._validate_project_directory():
            return

        projects = self.project_repository.get_projects()
        if not projects:
            self.console.print("[bold yellow]No projects found.[/bold yellow]")
            return

        project_choices = []
        for project_name in projects:
            project_meta = self.project_repository.get_project_meta(project_name)
            project_type = project_meta.get('type', 'Unknown Type')
            project_choices.append(f"{project_name} ({project_type})")

        project_to_view_display = questionary.select(
            "Select a project to view:",
            choices=project_choices
        ).ask()

        if project_to_view_display:
            # Extract the actual project name from the display string
            project_to_view = project_to_view_display.split(' (')[0]

        if project_to_view:
            self.project_interaction_service.project_menu(project_to_view)

    def delete_project(self):
        projects = self.project_repository.get_projects()
        if not projects:
            self.console.print("[bold yellow]No projects found.[/bold yellow]")
            return

        project_to_delete = questionary.select(
            "Select a project to delete:",
            choices=projects
        ).ask()

        if project_to_delete:
            if questionary.confirm(f"Are you sure you want to delete the project '{project_to_delete}'?").ask():
                success, message = self.project_repository.delete_project(project_to_delete)
                if success:
                    self.console.print(f"[bold green]{message}[/bold green]")
                else:
                    self.console.print(f"[bold red]{message}[/bold red]")