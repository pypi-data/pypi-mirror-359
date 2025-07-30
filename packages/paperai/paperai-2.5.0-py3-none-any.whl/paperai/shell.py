"""
paperai query shell module.
"""

import sys

from cmd import Cmd

from .models import Models
from .query import Query


class Shell(Cmd):
    """
    paperai query shell.
    """

    def __init__(self, path):
        super().__init__()

        self.intro = "paperai query shell"
        self.prompt = "(paperai) "

        self.embeddings = None
        self.db = None
        self.path = path

    def preloop(self):
        # Load embeddings and articles.sqlite
        self.embeddings, self.db = Models.load(self.path)

    def postloop(self):
        Models.close(self.db)

    def default(self, line):
        Query.query(self.embeddings, self.db, line, None, None)


def main(path=None):
    """
    Shell execution loop.

    Args:
        path: model path
    """

    if not path and len(sys.argv) > 1:
        path = sys.argv[1]

    Shell(path).cmdloop()


if __name__ == "__main__":
    main()
