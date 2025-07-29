from pathlib import Path

from setuptools import setup


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="streamlit-argparse",
    version="0.0.1",
    description="Generates a form for an argparse Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/streamlit-community/streamlit-navigation-bar",
    project_urls={
        "Source Code": "https://github.com/streamlit-community/streamlit-navigation-bar",
        "Bug Tracker": "https://github.com/streamlit-community/streamlit-navigation-bar/issues",
        "Release notes": "https://github.com/streamlit-community/streamlit-navigation-bar/releases",
        "Documentation": "https://github.com/streamlit-community/streamlit-navigation-bar/wiki/API-reference",
        "Community": "https://discuss.streamlit.io/t/new-component-streamlit-navigation-bar/66032",
    },
    author="Hans Then",
    author_email="hans.then@gmail.com",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Widget Sets",
    ],
    packages=["streamlit_argparse"],
    include_package_data=False,
    python_requires=">=3.10",
    install_requires=[
        "streamlit > 1.38.0",
        "streamlit_tags",
    ],

)
