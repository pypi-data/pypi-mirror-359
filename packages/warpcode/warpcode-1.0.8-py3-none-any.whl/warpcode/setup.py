"""
Setup script for WarpCode
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent.parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
requirements_file = this_directory / "warpcode" / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="warpcode",
    version="1.0.0",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    description="Warp through development cycles with automated BDD and Claude Coder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/warpcodedev/warpcode",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    keywords="bdd testing automation claude ai development orchestration",
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "warpcode=warpcode.main:main",
            "warp=warpcode.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "warpcode": [
            "ascii_art/*.txt",
            "templates/*.py",
            "templates/*.ini",
            "templates/*.feature",
            "templates/*.md",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/warpcodedev/warpcode/issues",
        "Source": "https://github.com/warpcodedev/warpcode",
        "Documentation": "https://github.com/warpcodedev/warpcode#readme",
    },
    zip_safe=False,
)