from setuptools import setup, find_packages

setup(
    name="stage0_py_utils",
    version="0.2.14",
    description="A utility package for stage0 microservices",
    author="Mike Storey",
    author_email="devs@agile-learning.institute",
    license="MIT",
    packages=find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "pymongo",
        "discord",
        "ollama"
    ],
    extras_require={
        "dev": ["black", "pytest", "unittest"]
    },
    include_package_data=True,
)