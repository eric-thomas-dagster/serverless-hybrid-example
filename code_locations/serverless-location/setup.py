from setuptools import find_packages, setup
from pathlib import Path

# Read requirements from requirements.txt
# Use absolute path relative to this setup.py file
setup_dir = Path(__file__).parent
requirements_file = setup_dir / "requirements.txt"

with open(requirements_file) as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="serverless-location",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    python_requires=">=3.10,<3.14",
)
