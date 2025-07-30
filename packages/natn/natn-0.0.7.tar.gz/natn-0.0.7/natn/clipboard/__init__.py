import subprocess
import sys
import os
from typing import Optional

def copy_to_clipboard(text: str) -> bool:
    # Method 1: Try Jupyter/IPython display
    try:
        from IPython.display import display, Javascript
        display(Javascript(f'''
            navigator.clipboard.writeText(`{text.replace("`", "\\`")}`);
        '''))
        return True
    except Exception:
        pass

    # Method 2: Try pyperclip
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    # Method 3: Try xerox
    try:
        import xerox
        xerox.copy(text)
        return True
    except Exception:
        pass

    # Method 4: System-specific commands
    try:
        if sys.platform.startswith("linux"):
            try:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                           stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                return process.returncode == 0
            except FileNotFoundError:
                try:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'],
                                               stdin=subprocess.PIPE, text=True)
                    process.communicate(input=text)
                    return process.returncode == 0
                except FileNotFoundError:
                    pass
    except Exception:
        pass


    # All methods failed
    return False
