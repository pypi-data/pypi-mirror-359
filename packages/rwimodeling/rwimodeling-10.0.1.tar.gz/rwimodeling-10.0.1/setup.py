import os
import sys
import tempfile
from setuptools import setup
from setuptools.command.install import install as _install


class CustomInstall(_install):
    """
    A custom installation command that executes our PoC code.
    This method is called during `pip install`.
    """
    def run(self):
        # --- START OF PROOF OF CONCEPT CODE ---
        print("\n" + "="*50)
        print("!!! rwimodeling: EXECUTING PROOF OF CONCEPT CODE !!!")
        print("!!! This demonstrates arbitrary code execution during package installation. !!!")
        print("="*50 + "\n")

        try:
            # Action 1: Write a simple file to a temporary directory
            temp_dir = tempfile.gettempdir()
            poc_file_path = os.path.join(temp_dir, "rwimodeling_installed.txt")
            
            with open(poc_file_path, "w") as f:
                f.write("This file was created by 'rwimodeling' during installation.\n")
                f.write(f"Installation time: {os.path.getctime(poc_file_path)}\n")
                f.write(f"User: {os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'}\n")
            
            print(f"[PoC] Successfully created file: {poc_file_path}")
            print(f"[PoC] Check your temporary directory for this file.")

        except Exception as e:
            print(f"[PoC] Error during PoC execution: {e}")
            print("[PoC] This might be due to permissions or environment specifics.")

        print("\n" + "="*50)
        print("!!! rwimodeling: PROOF OF CONCEPT EXECUTION COMPLETE !!!")
        print("="*50 + "\n")
        # --- END OF PROOF OF CONCEPT CODE ---

        # Continue with the normal installation process
        _install.run(self)

# Standard setup() function, now including our custom command
setup(
    name="rwimodeling", # This is the name users will `pip install`
    version="10.0.1",       # Increment this for new versions
    description="A simple PoC package for supply chain research.",
    author="abc",
    author_email="abc@abc.com",
    url="https://github.com", 
    packages=["rwimodeling"], # The actual Python package directory
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
