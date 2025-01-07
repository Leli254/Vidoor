# Sonic
Youtube Downloader

# Sonic Video Downloader

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

Sonic Video Downloader is designed to provide an easy-to-use interface for downloading videos or extracting audio from YouTube URLs. This application leverages the power of `yt-dlp` for downloading and PyQt5 for the GUI, ensuring both performance and user-friendliness.

## Features
- **Download Videos/Audio**: Choose between video or audio-only downloads.
- **Resolution Selection**: Select video resolution from available options fetched dynamically from YouTube.
- **Progress Indication**: Visual progress bar to monitor download status.
- **Cancel Download**: Option to cancel ongoing downloads.
- **Customizable Output**: Downloads are saved to the user's Downloads folder with a filename based on the video title.

## Installation

### Prerequisites
- Python 3.7+
- PyQt5
- yt-dlp

### Steps to Install
1. **Clone the repository:**
   ```sh
   git clone git@github.com:yourusername/SonicVideoDownloader.git
   cd SonicVideoDownloader

2.**Install required packages:**
sh
pip install -r requirements.txt

Note: requirements.txt should contain:
PyQt5
yt-dlp

**3.Run the application:**
sh
python main.py


## Usage
Enter URL: Paste the YouTube video or playlist URL into the provided text field.
Select Type: Choose whether to download as video or audio.
For video, choose the desired resolution from the dropdown (once fetched).
Download: Click the "Download" button to start the process. 
Cancel: If needed, you can cancel the download with the "Cancel" button.

## Dependencies
PyQt5: For creating the GUI.
yt-dlp: A youtube-dl fork with additional features and bug fixes.

## Contributing
Contributions are welcome! Here's how you can contribute:
Fork the repository
Create your feature branch (git checkout -b feature/YourFeature)
Commit your changes (git commit -m 'Add some feature')
Push to the branch (git push origin feature/YourFeature)
Open a pull request

Please ensure your code follows the project's coding standards and includes appropriate tests.

License
This project is licensed under the MIT License (LICENSE). 


**Notes:**
- Replace `yourusername` and `yourprojectname` with your actual GitHub username and project name.
- You would need to create a `requirements.txt` file with the dependencies listed.
- If you decide to use this README, make sure to add an actual `LICENSE` file in your repository for the MIT License or whatever license you choose.
- The `main.py` should be the script you run to start your application, so adjust this if your entry point is named differently.