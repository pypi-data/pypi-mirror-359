import os
from types import SimpleNamespace
from setuptools import find_packages

module_dir = os.path.dirname(__file__)


class Setup:
    def __init__(self):
        # Read the contents of the README file
        with open(module_dir + "/README.md", "r", encoding="utf-8") as fh:
            long_description = fh.read()
        self.name = "jsify"
        self.version = "1.0.3"  # Update the version as necessary
        self.author = "Zbigniew Rajewski"
        self.author_email = "zbigniew.r@citsystems.pl"
        self.description = "Jsify is a blazing-fast Python library powered by a C extension that transforms dictionaries, lists, and tuples into smart objects with JavaScript-style dot access (e.g., obj.key). It supports lazy, dynamic wrapping and safe, deep navigation where missing attributes return a special Undefined object instead of errors. Ideal for handling messy, deeply nested, or unpredictable JSON and Python data, Jsify enables seamless serialization and real-time, reference-based manipulation for clean and efficient code."
        self.long_description = long_description
        self.long_description_content_type = "text/markdown"
        self.keywords = "jsify, python, json, dot notation, attribute access, javascript, objects, serialization, undefined, c extension, safe access"  # SEO keywords
        self.url = "https://github.com/citsystems/jsify"  # Replace with the correct URL
        self.classifiers = [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ]
        self.python_requires = '>=3.0'  # Specify the required Python versions
        self.install_requires = [
            # List your project dependencies here
            # e.g., "requests >= 2.20.0",
        ]
        self.extras_require = {
            "dev": [
                "pytest>=3.7",
                "sphinx>=3.5.3",
                # Add other development dependencies
            ],
        }
        self.include_package_data = True  # Include non-Python files specified in MANIFEST.in
        self.project_urls = {  # Optional: Additional URLs for the project
            "Documentation": "https://citsystems.github.io/jsify",
            "Source": "https://github.com/citsystems/jsify",
            "Tracker": "https://github.com/citsystems/jsify/issues",
        }

setup = Setup()
