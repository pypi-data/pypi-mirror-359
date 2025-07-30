import sys
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

def copy_to_clipboard(text: str):
    # Method 1: Try IPython %clip magic
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip:
            ip.run_line_magic("clip", text)
            logging.debug("Copied to clipboard using IPython %clip magic.")
            return True
        else:
            logging.debug("IPython shell not found.")
    except Exception as e:
        logging.debug(f"IPython %clip method failed: {e}")

    # Method 2: Try Jupyter browser clipboard via Javascript
    try:
        from IPython.display import display, Javascript
        display(Javascript(f'''
            navigator.clipboard.writeText(`{text.replace("`", "\\`")}`);
        '''))
        logging.debug("Clipboard copy attempt using Jupyter Javascript.")
        return True
    except Exception as e:
        logging.debug(f"Jupyter Javascript clipboard method failed: {e}")

    # Method 3: Try pyperclip
    try:
        import pyperclip
        pyperclip.copy(text)
        logging.debug("Copied to clipboard using pyperclip.")
        return True
    except Exception as e:
        logging.debug(f"pyperclip method failed: {e}")

    # Method 4: Try xerox
    try:
        import xerox
        xerox.copy(text)
        logging.debug("Copied to clipboard using xerox.")
        return True
    except Exception as e:
        logging.debug(f"xerox method failed: {e}")

    # Method 5: System clipboard tools
    try:
        if sys.platform.startswith("linux"):
            try:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                           stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                success = process.returncode == 0
                logging.debug("xclip clipboard method: " + ("success" if success else "failure"))
                if success:
                    return True
            except FileNotFoundError as e:
                logging.debug(f"xclip not found: {e}")

            try:
                process = subprocess.Popen(['xsel', '--clipboard', '--input'],
                                           stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                success = process.returncode == 0
                logging.debug("xsel clipboard method: " + ("success" if success else "failure"))
                if success:
                    return True
            except FileNotFoundError as e:
                logging.debug(f"xsel not found: {e}")
    except Exception as e:
        logging.debug(f"Linux clipboard method failed: {e}")

    # All methods failed
    logging.warning("Failed to copy to clipboard using all available methods.")
    return False
