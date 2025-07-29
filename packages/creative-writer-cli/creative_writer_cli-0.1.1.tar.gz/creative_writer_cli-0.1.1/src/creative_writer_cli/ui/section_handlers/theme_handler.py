from .base_section_handler import BaseSectionHandler
from ..display.tables import display_themes_table
from ..display.views import view_details
from ..wizards.novel_wizards import get_theme_input
import questionary

class ThemeHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_themes_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Theme")
        if data:
            choices.insert(1, "Edit Theme")
            choices.insert(2, "Delete Theme")
            choices.insert(3, "View Theme Details")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Theme":
            new_item_data = get_theme_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Theme added.[/green]")
        elif action == "Edit Theme":
            if not data:
                self.console.print("[yellow]No themes to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select theme to edit:", choices=[item.get("theme_name", f"Theme {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("theme_name") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_theme_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Theme updated.[/green]")
        elif action == "Delete Theme":
            if not data:
                self.console.print("[yellow]No themes to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select theme to delete:", choices=[item.get("theme_name", f"Theme {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("theme_name") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Theme deleted.[/green]")
        elif action == "View Theme Details":
            view_details(data, "theme_name")
