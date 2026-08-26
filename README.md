# 🛡️ VideoAuthenticator - AI Video & Deepfake Forensic Detection Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20.svg)](https://www.djangoproject.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**VideoAuthenticator** is a multi-layer AI forensic media authentication platform designed to analyze digital video files and determine whether a video is **AI-Generated / Deepfake** (created by models such as Sora, Runway Gen-2, Pika, Stable Diffusion, or FaceSwap) versus **Authentic Physical Camera Footage**.

---

## 🌟 Key Features

### 1. 🤖 2D FFT Frequency Spectrum Analysis
- Generates 2D **Fast Fourier Transform (FFT) Magnitude Spectrum Heatmaps** for video frames.
- Identifies invisible **high-frequency spectral grid artifacts** created by neural generative AI models that physical camera lenses do not produce.

### 2. 📷 Physical Camera Sensor Noise Verification (PRNU)
- Measures **Photo Response Non-Uniformity (PRNU)** camera sensor noise residuals.
- Distinguishes authentic physical camera sensor noise patterns from synthetic, over-smoothed AI pixel gradients.

### 3. 🔍 Spatial Blur & Facial Smoothing Detection
- Calculates inter-frame **Laplacian variance** $\text{Var}(\Delta I)$.
- Detects artificial skin over-smoothing, face-swap blending boundaries, and spatial sharpness anomalies.

### 4. 🎞️ Inter-Frame Temporal Continuity & Warp Checking
- Evaluates frame-to-frame color histogram correlations and spatial face stability.
- Detects inter-frame flickering, warp distortions, face-swap splicing, and AI frame interpolation glitches.

### 5. 🚨 Explicit Verdict & AI Generation Probability %
- Calculates an exact **AI Generation Likelihood Percentage** (e.g., `89.5% AI Generated` vs `10.5% Real`).
- Assigns an explicit forensic verdict:
  - 🚨 **`AI GENERATED VIDEO / DEEPFAKE DETECTED`** (`CRITICAL RISK`)
  - ⚠️ **`SUSPICIOUS / POTENTIALLY ALTERED VIDEO`** (`MEDIUM RISK`)
  - ✅ **`VERIFIED REAL CAMERA FOOTAGE`** (`LOW RISK`)

### 6. 🔐 Cryptographic Provenance & SHA-256 Fingerprinting
- Generates an immutable **SHA-256 digital hash** for every uploaded video file to guarantee digital provenance and detect tampering.

### 7. 📄 Exportable Forensic Certificates
- Downloads structured **JSON Forensic Certificates** containing SHA-256 hashes, frame rate, resolution, codec, sampled frame statistics, and anomaly logs.

### 8. 🎨 Glassmorphic Dark UI & Interactive Dashboard
- Modern dark-themed dashboard with frosted glass cards (`backdrop-filter: blur`), glowing badges, live search, filter pills (`All`, `Authentic`, `Suspicious`, `Deepfake`), and drag-and-drop file upload.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.10+, Django 5.2
- **Computer Vision & Forensic Analytics**: OpenCV (`opencv-python-headless`), NumPy, Pillow, Matplotlib
- **Database**: SQLite3 (Production configurable for PostgreSQL)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphic Design System), JavaScript (ES6+), FontAwesome Icons

---

## 📁 Repository Directory Structure

```text
VideoAuthenticator/
├── videoauth/                   # Django Project Root
│   ├── manage.py                # Django CLI management script
│   ├── db.sqlite3               # SQLite Database
│   ├── media/                   # Uploaded videos & generated keyframe thumbnails
│   │   ├── video/               # Video storage
│   │   └── thumbnails/          # Generated keyframes & FFT spectrum heatmaps
│   ├── static/                  # Static CSS design assets
│   │   └── css/style.css        # Glassmorphic CSS design system
│   ├── templates/               # Global templates (base.html, login.html, register.html)
│   └── video/                   # Core Video Authentication App
│       ├── models.py            # Video model schema with forensic scores
│       ├── views.py             # Dashboard, upload, detail, export & auth views
│       ├── utils.py             # Multi-layer computer vision & FFT forensic engine
│       ├── forms.py             # Video upload & registration forms with validation
│       ├── urls.py              # Application routing
│       └── templates/video/     # App-specific templates (video_list, video_upload, video_detail)
└── README.md                    # Project Documentation
```

---

## ⚙️ Local Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/VideoAuthenticator.git
cd VideoAuthenticator/videoauth
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv ..\.venv
..\.venv\Scripts\activate

# macOS / Linux
python3 -m venv ../.venv
source ../.venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install Django opencv-python-headless numpy Pillow matplotlib imageio
```

### 4. Run Database Migrations
```bash
python manage.py makemigrations video
python manage.py migrate
```

### 5. Run the Unit Test Suite (Optional)
```bash
python manage.py test
```

### 6. Start the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 🔬 How the Forensic Pipeline Works

```mermaid
graph TD
    A[User Uploads Video] --> B[Compute SHA-256 Digital Fingerprint]
    B --> C[Extract Video Metadata: FPS, Resolution, Codec, Duration]
    C --> D[Sample Keyframes Across Video Stream]
    D --> E[Compute 2D FFT Frequency Spectrum Heatmap]
    D --> F[Extract Camera Sensor Noise Residuals - PRNU]
    D --> G[Calculate Spatial Blur Variance - Laplacian]
    D --> H[Analyze Inter-Frame Color Histogram Correlation]
    E & F & G & H --> I[Calculate Composite Authenticity & AI Likelihood Scores]
    I --> J[Generate Status: Authentic | Suspicious | Deepfake]
    J --> K[Render Interactive Dashboard & Exportable JSON Certificate]
```

---

## 🛡️ Forensic Verification Metrics Breakdown

| Metric | Analysis Technique | Target Anomaly |
| :--- | :--- | :--- |
| **FFT Frequency Spectrum** | 2D Fast Fourier Transform Magnitude Spectrum | High-frequency grid patterns from neural diffusion/GAN models |
| **Sensor Noise Residual** | Gaussian residual noise extraction ($\sigma_{\text{noise}}$) | Lack of physical hardware camera sensor noise (PRNU) |
| **Spatial Blur & Smoothness** | Laplacian Variance $\text{Var}(\Delta I)$ | Artificial facial smoothing & face-swap blending boundaries |
| **Temporal Continuity** | Inter-frame color histogram correlation | Warp distortion, flickering & frame-splicing glitches |
| **Digital Provenance** | Cryptographic SHA-256 Hashing | Tampering detection & file provenance verification |

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## Author

Ayush Kumar Pandey

---

## Contact Maintainer

Email: ayushpandey1974@gmail.com

GitHub: github.com/ayushpandey3357

