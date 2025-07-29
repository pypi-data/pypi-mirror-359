import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="auto-stomp",
    version="0.0.1",
    author="sieun lee",
    author_email="leesieun08@naver.com",
    description="A simple STOMP client for WebSocket with asyncio support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sieunie/auto-stomp",
    packages=setuptools.find_packages(exclude=["example"]),
    python_requires='>=3.7',
    install_requires=[
        "websockets>=10.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)