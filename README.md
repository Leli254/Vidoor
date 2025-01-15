![Vidoor logo](https://github.com/Leli254/Vidoor/blob/main/images/app_icon.jng?raw=true)

# Vidoor Video Downloader

A simple, GUI-based YouTube video and audio downloader built with PyQt5 and yt-dlp.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Overview

Vidoor Video Downloader is designed to provide an easy-to-use interface for downloading videos or extracting audio from YouTube URLs. Leveraging yt-dlp for downloads and PyQt5 for the GUI, it ensures performance, versatility, and user-friendliness.

## Features
- **Download Videos/Audio**: Choose between video or audio-only downloads.
- **Resolution Selection**: Select video resolution from available options fetched dynamically from YouTube.
- **Progress Indication**: Visual progress bar to monitor download status.
- **Customizable Output**: Downloads are saved to the user's Downloads folder with a filename based on the video title.

## Installation

### Linux (.deb)

Download the .deb file from the releases page and install it using the following command:

```sh
sudo dpkg -i vidoor-video-downloader.deb
```

Resolve any missing dependencies by running:

```sh
sudo apt-get install -f
```

### Windows (Executable)

Download the .exe installer from the releases page and follow the installation prompts.

### Source Installation (Installing from Source Code)
#### Prerequisites
- Python 3.7+
- PyQt5
- yt-dlp

#### Steps to Install
1. **Clone the repository:**
   ```sh
   git clone https://github.com/Leli254/Vidoor.git
   cd Vidoor
   ```

2.**Install required packages:**
```sh
pip install -r requirements.txt
```


**Note:** requirements.txt should contain:
PyQt5
yt-dlp

**3.Run the application:**

```sh
python main.py
```


## Usage
1. Enter URL: Paste the YouTube video or playlist URL into the provided text field.
2. Select Type: Choose whether to download as video or audio.
For video, choose the desired resolution from the dropdown (once fetched).
3. Download: Click the "Download" button to start the process. 

## Dependencies
PyQt5: For creating the GUI.
yt-dlp: A youtube-dl fork with additional features and bug fixes.

Install dependencies using:

```sh
pip install -r requirements.txt
```

## Contributing
Contributions are welcome! Here's how you can contribute:
- Fork the repository
- Create your feature branch (git checkout -b feature/YourFeature)
- Commit your changes (git commit -m 'Add some feature')
- Push to the branch (git push origin feature/YourFeature)
- Open a pull request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License
This project is licensed under the [MIT License](./LICENSE). 
