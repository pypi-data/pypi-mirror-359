import subprocess
import sys
import os


def is_pip_package_installed(package_name: str) -> bool:
    """
    Check if a pip package is installed. Never fails, works in any environment.

    Args:
        package_name: Name of the package to check

    Returns:
        bool: True if installed, False otherwise
    """
    try:
        # Method 1: Try pkg_resources (fastest)
        subprocess.run([
            sys.executable, '-c',
            f"import pkg_resources; pkg_resources.get_distribution('{package_name}')"
        ], check=True, capture_output=True, timeout=10)
        return True
    except:
        try:
            # Method 2: Try direct import
            subprocess.run([
                sys.executable, '-c', f"import {package_name}"
            ], check=True, capture_output=True, timeout=10)
            return True
        except:
            try:
                # Method 3: Try pip show (most reliable)
                subprocess.run([
                    sys.executable, '-m', 'pip', 'show', package_name
                ], check=True, capture_output=True, timeout=10)
                return True
            except:
                return False


def install_pip_package_anon(package_name: str) -> bool:
    """
    Install a pip package anonymously with minimal noise. Never fails.

    Args:
        package_name: Name of the package to install

    Returns:
        bool: True if installation succeeded, False otherwise
    """
    try:
        # Set up anonymous environment
        env = os.environ.copy()
        env.update({
            'PIP_NO_WARN_SCRIPT_LOCATION': '1',
            'PIP_DISABLE_PIP_VERSION_CHECK': '1',
            'PIP_NO_COLOR': '1',
            'PYTHONWARNINGS': 'ignore'
        })

        # Install with minimal output
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            package_name,
            '--quiet',
            '--disable-pip-version-check',
            '--no-warn-script-location'
        ], check=True, capture_output=True, timeout=300, env=env)

        return True
    except:
        return False


