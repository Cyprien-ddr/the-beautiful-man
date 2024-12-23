import subprocess
from bs4 import BeautifulSoup

from textual import on
from textual.app import App, ComposeResult
from textual.suggester import Suggester
from textual.widgets import Footer, Header, MarkdownViewer, Input


def get_man_list() -> list[str]:
    """
    Retrieves a list of available man page names.

    :return: A list of strings, each representing the name of a manual page.
    """
    man_list_process = subprocess.run(['man', '-k', '.'], capture_output=True, text=True)
    return [man.split(' ')[0] for man in man_list_process.stdout.split('\n')]

def convert_man_to_html(man_name: str) -> str:
    """
    Convert a Unix man page to HTML format.

    :param man_name: (str): The name of the manual page to convert.
    :return:  str: The HTML content of the specified manual page.
    """
    command = f'man -Thtml {man_name}'
    html_content = subprocess.run(command, shell=True, capture_output=True, text=True).stdout
    return html_content

def parse_html_to_markdown(html: str) -> str:
    """
    Converts HTML content into Markdown format.

    This function processes the given HTML string, removing anchor tags,
    converting header tags (h1, h2) to Markdown headers, and transforming
    specific paragraph structures into Markdown sections with headers.

    :param html: A string containing HTML content to be converted.
    :return: A string with the converted Markdown content.
    """
    soup = BeautifulSoup(html, 'lxml')

    for a in soup.find_all('a', href=True):
        a.unwrap()

    for h1 in soup.find_all('h1'):
        h1.insert_before('# ' + h1.text.strip() + '\n')
        h1.decompose()

    for h2 in soup.find_all('h2'):
        h2.insert_before('## ' + h2.text.strip() + '\n')
        h2.decompose()

    for p in soup.find_all('p'):
        if (len(p.find_all('b')) == 1 and len(p.contents) == 1) or (len(p.find_all('b')) == 2 and len(p.contents) == 3 and p.contents[1].strip().startswith(',')):

            options = p.b.text.split('\n')
            if len(p.find_all('b')) == 2 and len(p.contents) == 3 and p.contents[1].strip().startswith(','):
                p.insert_before('---\n### ' + ''.join(map(str, p.text[1:])) + '\n')
            elif len(options) == 1:
                p.insert_before('---\n### ' + options[0] + '\n')
            else:
                p.insert_before('---\n### ' + options[0] + '\n\n' + '**' + ' '.join(map(str, options[1:])) + '**\n')
            p.decompose()

    markdown_text = soup.get_text('\n')
    return markdown_text.strip()


class ManSuggester(Suggester):
    def __init__(self, mans: list[str]):
        super().__init__()
        self.mans = mans

    async def get_suggestion(self, value: str) -> str | None:
        """
        Provides a suggestion for a man page name based on the input value.

        :param value: A string representing the user's input to match against man page names.
        :return: The first man page name that starts with the input value, or None if no match is found.
        """
        return next((man for man in self.mans if man.startswith(value)), None)


class TheBeautifulMan(App):
    """
    A Textual application for viewing Unix man pages in Markdown format.

    This application provides a user interface with input for searching
    man pages and a viewer for displaying the converted Markdown content.
    """

    def __init__(self):
        super().__init__()
        self.viewer = MarkdownViewer("# The Beautiful Man\n"
            "A nice viewer for man", show_table_of_contents=False, id = "viewer")
        self.mans = get_man_list()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Input(placeholder="type the man name here", suggester=ManSuggester(self.mans))
        yield self.viewer

    @on(Input.Submitted)
    def search_man(self) -> None:
        """
        Handles the event when the user submits input in the Input widget.

        Converts the specified man page to Markdown and updates the viewer
        with the converted content. Clears the input field after processing.

        :return: None
        """
        user_search = self.query_one(Input)
        if user_search.value is not None:
            output = parse_html_to_markdown(convert_man_to_html(user_search.value))
            self.query_one("#viewer").document.update(output)
            self.query_one(Input).clear()


if __name__ == "__main__":
    app = TheBeautifulMan()
    app.run()
