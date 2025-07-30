from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="crackify",
    version="0.1.0",
    description="Terminal-based Spotify artist autostreamer (headless, requires librespot)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="YOUR NAME",
    author_email="YOUR_EMAIL",
    url="https://github.com/yourgithub/crackify",
    packages=find_packages(),
    install_requires=["spotipy>=2.23.0"],
    python_requires=">=3.7",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)