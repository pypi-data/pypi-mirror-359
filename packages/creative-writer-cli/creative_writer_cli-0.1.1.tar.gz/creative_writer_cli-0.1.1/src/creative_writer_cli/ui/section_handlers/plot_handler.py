from .base_section_handler import BaseSectionHandler
from ..display.tables import display_plot_table
from ..display.views import view_details
from ..wizards.novel_wizards import get_plot_point_input
import questionary

class PlotHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_plot_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Plot Point")
        if data:
            choices.insert(1, "Edit Plot Point")
            choices.insert(2, "Delete Plot Point")
            choices.insert(3, "View Plot Point Details")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Plot Point":
            new_item_data = get_plot_point_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Plot Point added.[/green]")
        elif action == "Edit Plot Point":
            if not data:
                self.console.print("[yellow]No plot points to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select plot point to edit:", choices=[item.get("name", f"Plot Point {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_plot_point_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Plot Point updated.[/green]")
        elif action == "Delete Plot Point":
            if not data:
                self.console.print("[yellow]No plot points to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select plot point to delete:", choices=[item.get("name", f"Plot Point {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Plot Point deleted.[/green]")
        elif action == "View Plot Point Details":
            view_details(data, "name")
