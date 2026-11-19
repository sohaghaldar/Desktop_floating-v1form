from setuptools import setup, find_packages
import os

readme_content = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()

setup(
    name="desktop-spider",
    version="2.6.0",
    author="Sohag Haldar",
    author_email="sohaghaldar@users.noreply.github.com",
    description="Interactive, physics-driven cross-platform desktop spider & floating pet ecosystem for Windows, Linux, and macOS.",
    long_description=readme_content,
    long_description_content_type="text/markdown",
    url="https://github.com/sohaghaldar/desktop-pet-ecosystem",
    py_modules=["desktop_spider"],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["assets/*", "locales/*", "settings.json", "VERSION"],
    },
    install_requires=[
        "pystray>=0.19.4",
        "Pillow>=9.0.0",
    ],
    extras_require={
        ":sys_platform != 'win32'": [
            "pynput>=1.7.6",
        ],
    },
    entry_points={
        "gui_scripts": [
            "desktop-spider=desktop_spider:main",
            "desktop-floating=desktop_spider:main",
            "desktop-pet=desktop_spider:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Desktop Environment",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
)
