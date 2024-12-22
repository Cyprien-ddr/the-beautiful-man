import subprocess

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, MarkdownViewer, Input


class TheBeautifulMan(App):

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Input(placeholder="type the man name here")

    # # Action Method
    # def action_toggle_dark(self) -> None:
    #     """An action to toggle dark mode."""
    #     self.dark = not self.dark

    @on(Input.Submitted)
    def search_man(self) -> None:
        user_search = self.query_one(Input)
        if user_search.value is not None:
            man_process = subprocess.Popen(['man', user_search.value], stdout=subprocess.PIPE, text=True)
            man2md_process = subprocess.run(['./man2md/man2md'], stdin=man_process.stdout, capture_output=True, text=True)
            man_process.stdout.close()
            with open("tmp.md", "w") as f:
                f.write(man2md_process.stdout)
            f.close()
            self.mount(MarkdownViewer(man2md_process.stdout))

if __name__ == "__main__":
    app = TheBeautifulMan()
    app.run()
