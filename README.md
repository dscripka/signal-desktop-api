# README

This repo implements a basic Python API for the [Signal Desktop](https://signal.org/en/download/) application. It can be used to send text messages and perform basic monitoring for received text messages.

Note that there are other options that are more suitable for programmatic usage of Signal (e.g., https://github.com/AsamK/signal-cli). This repository was built primarily to experiment with PyAutoGui and other tools to programmatically control systems originally designed for human interaction.

## Requirements

An installed Signal Desktop app, running an Ubuntu 20.04+ system (this code is specific to that OS).

Tesseract 4.1.1+ also must be available to read messages.

See the requirements.txt files for environment details.

## Usage

The class is written leveraging asyncio in Python, and can be run independently or integrated within a larger asynchronous Python applications. To launch the program independently:

```
python signal_desktop_api.py
```

Note that the `signal_conversation_icon.png` image will need to be updated to match the pattern of your particular Signal Desktop setup.