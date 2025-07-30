from .clipboard import copy_to_clipboard
from .core import ask

async def round(question: str, python_only: int = 1, show_answer: int = 0) -> None:
    answer = await ask(question, bool(python_only))

    if bool(show_answer):
        print(show_answer)

    if len(answer) == 0:
       copy_to_clipboard("104")
    else:
        copy_to_clipboard(answer)
