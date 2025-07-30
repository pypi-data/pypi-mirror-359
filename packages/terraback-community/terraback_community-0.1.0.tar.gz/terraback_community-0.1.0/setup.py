import os
from setuptools import setup, find_packages

# Default to community build if not specified
terraback_tier = os.environ.get("TERRABACK_TIER", "community")

# Base dependencies for all tiers
install_requires = [
    "boto3",
    "click",
    "pyyaml",
    "rich",
    "google-api-python-client",
    "google-cloud-storage",
    "azure-identity",
    "azure-mgmt-resource",
    "azure-mgmt-compute",
    "paramiko",
    "cryptography",
    "requests",
]

# Base entry points
entry_points = {
    "console_scripts": [
        "terraback=terraback.cli.main:cli",
    ],
}

# Tier-specific adjustments
if terraback_tier == "migration":
    # Add migration-specific dependencies if any
    # install_requires.extend([...])
    entry_points["console_scripts"].append(
        "terraback-migration=terraback.migration.cli:cli"
    )

elif terraback_tier == "enterprise":
    # Add enterprise-specific dependencies if any
    # install_requires.extend([...])
    entry_points["console_scripts"].extend([
        "terraback-migration=terraback.migration.cli:cli",
        "terraback-enterprise=terraback.enterprise.cli:cli",
    ])

setup(
    name=f"terraback-{terraback_tier}",
    version="0.1.0",
    packages=find_packages(),
    author="Your Name",
    author_email="your.email@example.com",
    description="Terraback: A tool for infrastructure scanning and backup.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points=entry_points,
    install_requires=install_requires,
)