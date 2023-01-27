import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dispander",
    version="1.0.0",
    author="1ntegrale9",
    author_email="1ntegrale9uation@gmail.com",
    description="Discord Message URL Expander",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DiscordBotPortalJP/dispander",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "discord.py@git+https://github.com/Rapptz/discord.py@master",
    ],
)
