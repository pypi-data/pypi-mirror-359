import sys
import subprocess
import logging

def copy_to_clipboard(text: str):
    # Method 2: Try Jupyter browser clipboard via Javascript
    try:
        from IPython.display import display, Javascript
        safe_text = text.replace('\\', '\\\\').replace('`', '\\`')
        js_code = f"""
        (async () => {{
            try {{
                await navigator.clipboard.writeText(`{safe_text}`);
                console.log('Copied to clipboard!');
            }} catch (err) {{
                console.error('Failed to copy:', err);
                alert('⚠️ Unable to copy to clipboard. Please allow clipboard access in your browser.');
            }}
        }})();
        """
        display(Javascript(js_code))
        return True
    except Exception as e:
        pass

    # Method 3: Try pyperclip
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception as e:
        pass

    # Method 4: Try xerox
    try:
        import xerox
        xerox.copy(text)
        return True
    except Exception as e:
        pass

    # Method 5: System clipboard tools
    try:
        if sys.platform.startswith("linux"):
            try:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                           stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                success = process.returncode == 0
                if success:
                    return True
            except FileNotFoundError as e:
                pass

            try:
                process = subprocess.Popen(['xsel', '--clipboard', '--input'],
                                           stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                success = process.returncode == 0
                if success:
                    return True
            except FileNotFoundError as e:
                pass
    except Exception as e:
        pass

    return False
