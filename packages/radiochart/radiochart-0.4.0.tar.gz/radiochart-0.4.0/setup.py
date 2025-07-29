from setuptools import setup, find_packages

setup(
    name="radiochart",
    version="0.4.0",
    description="Generate hierarchical radio charts for Arma 3 MILSIM units.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="KingCharlesVII",
    author_email="viikingcharles@gmail.com",
    url="https://github.com/kingcharlesvi/radiochart",
    packages=find_packages(),
    install_requires=[
        "graphviz",
        "InquirerPy",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "radiochart=radiochart.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    include_package_data=True,
)