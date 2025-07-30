"""Package configuration."""

from setuptools import find_packages, setup
from komora_syncer import __appname__

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

requirements = [
    "click==8.1.7",
    "pynetbox==7.4.0",
    "python-slugify==8.0.4",
    "appdirs==1.4.4",
    "PyYAML==6.0.2",
    "lat-lon-parser",
    "loguru",
]

setup_requirements = [
    "pytest-runner",
]
test_requirements = ["pytest", "pytest-cov", "pytest-mock", "pynxos", "ipdb", "ruff"]

setup(
    name=__appname__,
    author="Jan Krupa",
    author_email="jan.krupa@cesnet.cz",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Operating System :: Unix",
    ],
    description="Synchronize data between Komora and Netbox applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    include_package_data=True,
    keywords="netbox,komora",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://gitlab.cesnet.cz/701/done/netbox_komora_syncer",
    version="5.7",
    zip_safe=False,
    python_requires=">=3.8, <4",
    entry_points={
        "console_scripts": [
            "komora_syncer=komora_syncer.__main__:cli",
        ]
    },
)
