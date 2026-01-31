from setuptools import setup, find_packages

setup(
    name="scraplog-git2net",
    version="0.1.0",
    description="Transform Git logs into collaboration networks",
    author="Your Name",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "networkx>=3.0",
        "rich>=13.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "scraplog=scraplog:main",
            "transform-nofi-2-nofo=transform_nofi_2_nofo_graphml:main",
            "deanonymize-github-users=deanonymize_github_users:main",
            ""
        ],
    },
    python_requires=">=3.8",
)
