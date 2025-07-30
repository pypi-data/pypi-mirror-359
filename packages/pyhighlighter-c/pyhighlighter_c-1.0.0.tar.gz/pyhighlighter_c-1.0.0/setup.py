from setuptools import setup, find_packages

setup(
    name="pyhighlighter-c",
    version="1.0.0", 
    author="Jay C",
    author_email="your.email@example.com",
    description="Advanced syntax highlighter with built-in compiler",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyhighlighter",
    packages=find_packages(),
    install_requires=[
        "pygments>=2.10.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="syntax highlighting code editor compiler",
    entry_points={
        "console_scripts": [
            "dockr=highlighter.dockr:main",
        ],
    },
)