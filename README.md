<img src="https://github.com/Leli254/Vidoor/blob/main/images/app_icon.jpg" alt="Vidoor logo" width="200" />


# Vidoor Video Downloader

Vidoor Video Downloader is a professional-grade desktop application for downloading and converting YouTube video and audio content with speed, reliability, and precision.

Built with **PyQt5** and powered by the industry-standard **yt-dlp** engine, Vidoor delivers a streamlined workflow for users who need efficient media extraction with a polished desktop experience.

The application combines:
- A responsive native desktop interface
- Real-time progress monitoring
- High-quality audio conversion
- Dynamic resolution discovery
- Modern JavaScript runtime handling for platform compatibility

---

## ⚖️ Legal Disclaimer

Vidoor is provided as a technical utility for personal content management and lawful media access.

Use of third-party platforms such as YouTube is governed by their respective Terms of Service. By using this software, you acknowledge that you are solely responsible for complying with:
- Applicable copyright laws
- Platform usage policies
- Local regulations regarding media downloading and distribution

The developers of Vidoor do not endorse:
- Unauthorized redistribution of copyrighted material
- Commercial misuse of downloaded content
- Circumvention of platform restrictions in violation of service agreements

---

## ✨ Key Features

### Dynamic Metadata Extraction
Automatically retrieves available video formats and resolutions directly from the source, including:
- 144p
- 360p
- 720p
- 1080p
- 4K (when available)

### High-Quality Audio Conversion
Extract audio streams into high-fidelity MP3 files with:
- Embedded thumbnails
- Metadata preservation
- FFmpeg-powered transcoding

### Real-Time Download Monitoring
Integrated progress tracking provides:
- Download percentage
- Transfer speed
- Estimated time remaining (ETA)
- Live processing status

### Modern JavaScript Runtime Support
Integrated with `yt-dlp-ejs` and Node.js to maintain compatibility with modern signature-based platform protections and dynamic JavaScript extraction logic.

### Flexible File Management
Users can:
- Select custom output directories
- Organize downloads efficiently
- Automatically clean temporary fragments after processing

### Professional Desktop Experience
Built with PyQt5 to provide:
- Native desktop responsiveness
- Clean step-based workflow
- Stable cross-platform operation

---

## 🚀 Installation

## Prerequisites

Before installing Vidoor, ensure the following dependencies are available on your system:

### Required Software

- Python 3.7+
- Node.js
- FFmpeg

### Why These Dependencies Matter

| Dependency | Purpose |
|---|---|
| Python | Core application runtime |
| Node.js | JavaScript signature/runtime support |
| FFmpeg | Audio extraction and media transcoding |

---

## 📥 Source Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Leli254/Vidoor.git
cd Vidoor
```

### 2. Create a Virtual Environment (Recommended)

#### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 📦 Binary Installation

### Linux (.deb)

```bash
sudo dpkg -i vidoor-video-downloader.deb
```

### Windows (.exe)

Download the latest installer from the Releases page.

---

## 🛠 Usage Guide

### Step 1 — Paste URL
Copy and paste the YouTube video URL into the application input field.

### Step 2 — Select Media Type
Choose:
- Video Download
- Audio Extraction

### Step 3 — Choose Resolution
If downloading video, Vidoor automatically fetches available resolutions for selection.

### Step 4 — Select Output Directory
Choose where the downloaded media should be saved.

### Step 5 — Start Download
Click **Start Download** to begin processing.

The application will display:
- Live progress
- Download speed
- ETA
- Conversion status

---

## 📦 Technical Stack

| Category | Technology |
|---|---|
| GUI Framework | PyQt5 |
| Media Engine | yt-dlp |
| JavaScript Runtime Support | yt-dlp-ejs |
| Media Processing | FFmpeg |
| Language | Python |
| Testing | pytest, pytest-qt |

---

## 🧪 Testing

The project includes automated tests for validating:
- Download workflow behavior
- GUI interaction logic
- Media processing functionality
- Runtime stability

### Run All Tests

```bash
pytest -v
```

### Run GUI-Specific Tests

```bash
pytest tests/gui -v
```

---

## 🤝 Contributing

Professional contributions are welcome.

### Standard Contribution Workflow

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/optimization
```

3. Commit changes using conventional commit standards
4. Push your branch
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

See the `LICENSE` file for full details.
