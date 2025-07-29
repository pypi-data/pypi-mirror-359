import questionary
from rich.console import Console

from ...data.repositories.project_repository import ProjectRepository
from ...core.templates import TEMPLATES

# Import all new section handlers
from ..section_handlers.character_handler import CharacterHandler
from ..section_handlers.plot_handler import PlotHandler
from ..section_handlers.worldbuilding_handler import WorldbuildingHandler
from ..section_handlers.theme_handler import ThemeHandler
from ..section_handlers.notes_handler import NotesHandler
from ..section_handlers.reference_handler import ReferenceHandler
from ..section_handlers.scientific_text_handler import ScientificTextHandler
from ..section_handlers.chapter_handler import ChapterHandler
from ..section_handlers.generic_handler import GenericHandler

# Re-import project_overview from display.views as it's still used in project_menu
from ..display.views import project_overview


class ProjectInteractionService:
    def __init__(self, project_repository: ProjectRepository, console: Console):
        self.project_repository = project_repository
        self.console = console
        self.section_handlers = {
            "Novel": {
                "Characters": CharacterHandler,
                "Plot": PlotHandler,
                "Worldbuilding": WorldbuildingHandler,
                "Themes": ThemeHandler,
                "Notes/Ideas": NotesHandler,
            },
            "Scientific Article": {
                "References": ReferenceHandler,
                "Title": ScientificTextHandler,
                "Abstract": ScientificTextHandler,
                "Introduction": ScientificTextHandler,
                "Methods": ScientificTextHandler,
                "Results": ScientificTextHandler,
                "Discussion": ScientificTextHandler,
                "Conclusion": ScientificTextHandler, # Assuming Conclusion is also a scientific text section
            },
            "Scientific Book": {
                "References": ReferenceHandler,
                "Title": ScientificTextHandler,
                "Abstract": ScientificTextHandler,
                "Introduction": ScientificTextHandler,
                "Methods": ScientificTextHandler,
                "Results": ScientificTextHandler,
                "Discussion": ScientificTextHandler,
                "Conclusion": ScientificTextHandler,
                "Chapter 1": ChapterHandler,
                "Chapter 2": ChapterHandler,
                "Chapter 3": ChapterHandler,
                # Add more chapters as needed
            },
            # Add other project types and their sections here
        }
        # Default handler for any section not explicitly defined
        self.default_handler = GenericHandler

    def project_menu(self, project_name):
        while True:
            self.console.print(f"\n[bold cyan]Project: {project_name}[/bold cyan]")
            sections = self.project_repository.get_project_sections(project_name)
            choice = questionary.select(
                "What do you want to do?",
                choices=["View/Edit Sections", "Rename Project", "Project Overview", "Export Project", "Back to Main Menu"]
            ).ask()

            if choice == "View/Edit Sections":
                self.view_edit_sections(project_name, sections)
            elif choice == "Project Overview":
                project_meta = self.project_repository.get_project_meta(project_name)
                project_type = project_meta.get('type')
                sections = self.project_repository.get_project_sections(project_name)
                project_overview(project_name, sections, project_type, self.project_repository)
            elif choice == "Rename Project":
                self.rename_project(project_name)
                # After renaming, the project_name variable in this scope is outdated.
                # We need to break and let the main_menu re-list projects.
                break
            elif choice == "Export Project":
                self.export_project_menu(project_name)
            elif choice == "Back to Main Menu" or choice is None:
                break

    def rename_project(self, old_project_name):
        new_project_name = questionary.text(f"Enter new name for project '{old_project_name}':").ask()
        if not new_project_name:
            self.console.print("[bold red]New project name cannot be empty.[/bold red]")
            return

        if new_project_name == old_project_name:
            self.console.print("[bold yellow]Project name is the same. No change made.[/bold yellow]")
            return

        success, message = self.project_repository.rename_project(old_project_name, new_project_name)
        if success:
            self.console.print(f"[bold green]{message}[/bold green]")
        else:
            self.console.print(f"[bold red]{message}[/bold red]")

    def view_edit_sections(self, project_name, sections):
        section_to_edit = questionary.select(
            "Select a section to view/edit:",
            choices=sections
        ).ask()

        if section_to_edit:
            self.edit_section(project_name, section_to_edit)

    def export_project_menu(self, project_name):
        export_format = questionary.select(
            "Select export format:",
            choices=["Markdown", "JSON", "TXT"]
        ).ask()

        if export_format:
            message = self.project_repository.export_project(project_name, export_format)
            self.console.print(f"[bold green]{message}[/bold green]")

    def edit_section(self, project_name, section_name):
        project_meta = self.project_repository.get_project_meta(project_name)
        project_type = project_meta.get('type')

        # Determine the appropriate handler
        handler_class = self.section_handlers.get(project_type, {}).get(section_name, self.default_handler)
        handler = handler_class(self.project_repository, self.console)

        while True:
            data = self.project_repository.get_section_content(project_name, section_name)
            self.console.print(f"\n[bold]Editing: {section_name}[/bold]")

            handler.display_content(data)

            choices = handler.get_choices(data)
            action = questionary.select(
                "What do you want to do?",
                choices=choices
            ).ask()

            if action == "Back to Project Menu" or action is None:
                break

            handler.handle_section_action(project_name, section_name, action, data)