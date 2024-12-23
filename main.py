import subprocess
from abc import ABC
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.suggester import Suggester
from textual.widgets import Footer, Header, MarkdownViewer, Input


def get_man_list() -> list[str]:
    man_list_process = subprocess.run(['man', '-k', '.'], capture_output=True, text=True)
    return [man.split(' ')[0] for man in man_list_process.stdout.split('\n')]


class ManSuggester(Suggester):
    def __init__(self, mans: list[str]):
        super().__init__()
        self.mans = mans

    async def get_suggestion(self, value: str) -> str | None:
        return next((man for man in self.mans if man.startswith(value)), None)

class TheBeautifulMan(App[None]):

    # BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self):
        super().__init__()
        # self.man = MarkdownViewer("### NAME\
# printf - format and print data")
        self.mans = get_man_list()
        # print(self.mans)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Input(placeholder="type the man name here", suggester=ManSuggester(self.mans))
        # yield self.man

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
            # with open("tmp.md", "w") as f:
            #     f.write(man2md_process.stdout)
            # f.close()
            self.mount(MarkdownViewer(man2md_process.stdout))
            self.query_one(Input).clear()
            # self.man = MarkdownViewer(man2md_process.stdout)
            # self.update()


if __name__ == "__main__":
    app = TheBeautifulMan()
    app.run()
