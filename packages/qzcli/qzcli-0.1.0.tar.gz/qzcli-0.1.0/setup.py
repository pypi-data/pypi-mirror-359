from setuptools import setup, find_packages

setup(
    name="qzcli",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="CLI tool to run remote Python queries via SSH",
    url="https://github.com/yourusername/qz",   # optional
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "qz=qz.qz:main"
        ]
    },
    install_requires=[],
    python_requires=">=3.6",
)
