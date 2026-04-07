"""Setup configuration for AudioStream package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="audiostream",
    version="1.0.0",
    author="AudioStream Contributors",
    description="High-Definition Lossless Audio Player with IoT Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/audiostream",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sounddevice>=0.4.5",
        "soundfile>=0.12.1",
        "numpy>=1.21.0",
        "Flask>=2.0.0",
        "Flask-CORS>=3.0.10",
        "mutagen>=1.45.0",
        "PyYAML>=5.4.0",
        "netifaces>=0.11.0",
    ],
    extras_require={
        "rpi": [
            "RPi.GPIO>=0.7.0",
            "gpiozero>=2.0.0",
            "adafruit-circuitpython-ssd1306>=1.6.0",
        ],
        "torrent": [
            "python-libtorrent>=2.0.7",
        ],
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0",
            "pylint>=2.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "audiostream=main:main",
        ],
    },
    include_package_data=True,
)
