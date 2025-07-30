from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bsod",
    version="0.1.4",
    author="arpy8",
    author_email="arpitsengar99@gmail.com",
    description="Blue Screen of Death",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arpy8/bsod",
    packages=find_packages(),
    install_requires=["pygame", "keyboard", "pywin32", "pyautogui", "setuptools==66.1.1"],
    entry_points={
        "console_scripts": [
            "bsod=bsod.main:main",
        ],  
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={'bsod': ['assets/*.mp3']},
    include_package_data=True,
    license="MIT"
)
