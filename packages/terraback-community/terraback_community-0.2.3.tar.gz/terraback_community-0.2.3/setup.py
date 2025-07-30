import os
from setuptools import setup, find_packages

# Default to community build if not specified
terraback_tier = os.environ.get("TERRABACK_TIER", "community")

# Base dependencies for all tiers
install_requires=[
    # AWS SDK
    "boto3==1.38.21",
    "botocore==1.38.21",

    # Azure SDK
    "azure-identity==1.15.0",
    "azure-mgmt-resource==23.1.0",
    "azure-mgmt-compute==31.0.0",
    "azure-mgmt-network==27.0.0",
    "azure-mgmt-storage==21.2.0",
    "azure-mgmt-web==7.3.0",
    "azure-mgmt-sql==3.0.1",
    "azure-mgmt-keyvault==10.3.0",
    "azure-mgmt-monitor==6.0.0",
    "azure-core==1.30.0",

    # Google Cloud SDK
    "google-cloud-compute==1.14.0",
    "google-cloud-storage==2.10.0",
    "google-cloud-resource-manager==1.10.0",
    "google-auth==2.23.0",

    # CLI Framework & Display
    "typer==0.15.4",
    "click==8.1.8",
    "rich==14.0.0",
    "colorama==0.4.6",
    "Pygments==2.19.1",

    # Templating
    "Jinja2==3.1.6",
    "MarkupSafe==3.0.2",

    # Utilities
    "requests",
    "cryptography",
    "paramiko",
    "pyyaml",
    "jmespath==1.0.1",
    "markdown-it-py==3.0.0",
    "mdurl==0.1.2",
    "python-dateutil==2.9.0.post0",
    "shellingham==1.5.4",
    "six==1.17.0",
    "typing_extensions==4.13.2",
    "urllib3>=1.26.0,<2.0",
],

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
    version="0.2.3",
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