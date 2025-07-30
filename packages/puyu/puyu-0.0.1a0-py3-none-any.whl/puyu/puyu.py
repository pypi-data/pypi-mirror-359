from typing import Generic, TypeVar

from prompt_toolkit.application import Application

ResultT = TypeVar('ResultT')


class Puyu(Generic[ResultT]):
    def __init__(self, app: Application[ResultT]) -> None:
        self.app = app

    def ask(self) -> ResultT:
        return self.app.run()

    def ask_async(self) -> ResultT:
        return self.app.run_async()
