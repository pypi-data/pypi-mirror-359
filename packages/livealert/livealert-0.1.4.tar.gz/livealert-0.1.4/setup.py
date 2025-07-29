from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("LICENSE", "r", encoding="utf-8") as f:
    license_text = f.read()

setup(
    name="livealert",
    version="0.1.4",
    author="cyrus-spc-tech",
    author_email="tanishgupta12389@gmail.com",
    description="A CLI tool to fetch real-time weather and news alerts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyrus-spc-tech/livealert",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.1",
        "python-dotenv>=0.19.0",
        "rich>=12.0.0",
        "pyfiglet>=0.8.post1"
    ],
    entry_points={
        'console_scripts': [
            'livealert=livealert.cli:main',
            'weather=livealert.cli:weather',
            'news=livealert.cli:news'
        ]
    },
    license=license_text
)
