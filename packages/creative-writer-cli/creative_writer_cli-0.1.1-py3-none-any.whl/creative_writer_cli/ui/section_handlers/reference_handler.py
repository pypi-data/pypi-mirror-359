from .base_section_handler import BaseSectionHandler
from ..display.tables import display_references_table
from ..display.views import view_details
from ..wizards.scientific_wizards import get_reference_input
import questionary

class ReferenceHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_references_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Reference")
        if data:
            choices.insert(1, "Edit Reference")
            choices.insert(2, "Delete Reference")
            choices.insert(3, "View Reference Details")
            choices.insert(0, "Export References") # Specific to references
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Reference":
            new_item_data = get_reference_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Reference added.[/green]")
        elif action == "Edit Reference":
            if not data:
                self.console.print("[yellow]No references to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select reference to edit:", choices=[item.get("title", f"Reference {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_reference_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Reference updated.[/green]")
        elif action == "Delete Reference":
            if not data:
                self.console.print("[yellow]No references to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select reference to delete:", choices=[item.get("title", f"Reference {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Reference deleted.[/green]")
        elif action == "View Reference Details":
            view_details(data, "title")
        elif action == "Export References":
            export_format = questionary.select(
                "Select reference export format:",
                choices=["BibTeX", "RIS", "Zotero RDF"]
            ).ask()
            if export_format:
                message = self.project_repository.export_project(project_name, export_format)
                self.console.print(f"[bold green]{message}[/bold green]")
