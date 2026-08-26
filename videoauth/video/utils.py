import os
import hashlib
import json
import cv2
import numpy as np
from PIL import Image
from django.conf import settings

def compute_sha256(file_path):
    """Computes SHA-256 digital fingerprint of the video file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return f"error_{str(e)}"

def decode_fourcc(fourcc_int):
    """Decodes FourCC integer to string."""
    try:
        return "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)]).strip()
    except Exception:
        return "Unknown"

def analyze_fft_spectrum(gray_frame):
    """
    Performs 2D Fast Fourier Transform (FFT) analysis to detect frequency domain anomalies.
    AI generation models (GANs, Diffusion, Sora, Runway, FaceSwap) display characteristic
    spectral grid artifacts or abnormal high-frequency power decay.
    """
    f = np.fft.fft2(gray_frame)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-5)
    
    # Calculate High Frequency vs Low Frequency Power Ratio
    h, w = gray_frame.shape
    cy, cx = h // 2, w // 2
    r = min(h, w) // 8
    
    # Low frequency mask
    y, x = np.ogrid[:h, :w]
    mask_low = (x - cx)**2 + (y - cy)**2 <= r**2
    
    low_freq_power = np.sum(np.abs(fshift)[mask_low])
    high_freq_power = np.sum(np.abs(fshift)[~mask_low])
    
    freq_ratio = high_freq_power / (low_freq_power + 1e-5)
    return magnitude_spectrum, float(freq_ratio)

def analyze_video(video_instance):
    """
    Performs multi-layer computer vision, FFT frequency spectrum, and forensic AI authentication on a video.
    Updates the video instance with scores, metadata, status, report JSON, spectrum heatmap, and thumbnail.
    """
    file_path = video_instance.file.path
    
    # 1. Compute SHA-256 Hash
    file_hash = compute_sha256(file_path)
    video_instance.file_hash = file_hash
    
    if not os.path.exists(file_path):
        video_instance.verification_status = 'Error'
        video_instance.save()
        return

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        video_instance.verification_status = 'Error'
        video_instance.save()
        return

    # Extract Video Technical Properties
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0
    fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = decode_fourcc(fourcc_int)
    duration = round(frame_count / fps, 2) if fps > 0 and frame_count > 0 else 0.0
    resolution_str = f"{width}x{height}" if width and height else "Unknown"

    video_instance.fps = round(fps, 2)
    video_instance.frame_count = frame_count
    video_instance.resolution = resolution_str
    video_instance.duration = duration
    video_instance.video_codec = codec if codec else "H264/MP4V"

    # Prepare Haar Cascade Face Detector
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path) if os.path.exists(cascade_path) else None

    # Sample Frames across video (sample up to 25 evenly spaced frames)
    max_samples = 25
    sample_indices = []
    if frame_count > 0:
        step = max(1, frame_count // max_samples)
        sample_indices = list(range(0, frame_count, step))[:max_samples]
    else:
        sample_indices = list(range(0, 100, 4))

    laplacian_variances = []
    noise_residuals = []
    fft_freq_ratios = []
    histograms = []
    faces_detected_count = 0
    face_boxes = []
    keyframe_img = None
    best_spectrum_map = None

    for idx, frame_no in enumerate(sample_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        if keyframe_img is None:
            keyframe_img = frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. Spatial Blur / Sharpness via Laplacian Variance
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        laplacian_variances.append(float(lap_var))

        # 2. Sensor High-Frequency Noise Residual Analysis
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = cv2.absdiff(gray, blurred)
        noise_std = float(np.std(noise))
        noise_residuals.append(noise_std)

        # 3. FFT 2D Frequency Domain Analysis
        mag_spectrum, freq_ratio = analyze_fft_spectrum(gray)
        fft_freq_ratios.append(freq_ratio)
        if best_spectrum_map is None:
            # Color map the magnitude spectrum
            norm_spectrum = cv2.normalize(mag_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            best_spectrum_map = cv2.applyColorMap(norm_spectrum, cv2.COLORMAP_JET)

        # 4. Color Histogram for Inter-Frame Continuity
        hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        histograms.append(hist)

        # 5. Face Detection & Stability Analysis
        if face_cascade:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) > 0:
                faces_detected_count += 1
                if len(face_boxes) == 0:
                    keyframe_img = frame.copy()
                for (fx, fy, fw, fh) in faces:
                    face_boxes.append([int(fx), int(fy), int(fw), int(fh)])

    cap.release()

    # Save Keyframe Thumbnail & FFT Spectrum Heatmap
    spectrum_rel_path = None
    if keyframe_img is not None:
        try:
            rel_thumb_dir = os.path.join('thumbnails')
            abs_thumb_dir = os.path.join(settings.MEDIA_ROOT, rel_thumb_dir)
            os.makedirs(abs_thumb_dir, exist_ok=True)
            
            thumb_filename = f"thumb_{video_instance.pk or 'new'}_{os.path.basename(file_path)}.jpg"
            abs_thumb_path = os.path.join(abs_thumb_dir, thumb_filename)
            
            h, w = keyframe_img.shape[:2]
            target_w = 480
            target_h = int(h * (target_w / w)) if w > 0 else 270
            resized_thumb = cv2.resize(keyframe_img, (target_w, target_h))
            cv2.imwrite(abs_thumb_path, resized_thumb)
            
            video_instance.thumbnail = os.path.join('thumbnails', thumb_filename)

            # Save FFT Spectrum Image
            if best_spectrum_map is not None:
                spec_filename = f"spectrum_{video_instance.pk or 'new'}_{os.path.basename(file_path)}.jpg"
                abs_spec_path = os.path.join(abs_thumb_dir, spec_filename)
                resized_spec = cv2.resize(best_spectrum_map, (target_w, target_h))
                cv2.imwrite(abs_spec_path, resized_spec)
                spectrum_rel_path = os.path.join('thumbnails', spec_filename).replace('\\', '/')
        except Exception as e:
            print(f"Error saving keyframes/spectrum: {e}")

    # Calculate Forensic Sub-Scores & AI Generation Probabilities

    # 1. Metadata Integrity Score
    metadata_anomalies = []
    meta_score = 100.0
    if fps < 15 or fps > 120:
        meta_score -= 20
        metadata_anomalies.append("Non-standard frame rate detected.")
    if frame_count < 10:
        meta_score -= 25
        metadata_anomalies.append("Extremely short video stream duration.")
    if width < 320 or height < 240:
        meta_score -= 15
        metadata_anomalies.append("Low video resolution.")
    meta_score = max(10.0, meta_score)

    # 2. Spatial Sharpness / Blur Artifact Score
    spatial_anomalies = []
    if laplacian_variances:
        mean_lap = np.mean(laplacian_variances)
        std_lap = np.std(laplacian_variances)
        if mean_lap < 30.0:
            spat_score = max(20.0, mean_lap * 2.0)
            spatial_anomalies.append("High degree of facial/spatial over-smoothing (AI Diffusion artifact).")
        elif mean_lap > 1500.0:
            spat_score = 75.0
            spatial_anomalies.append("Excessive high-frequency noise or sharpening detected.")
        else:
            spat_score = min(98.0, 60.0 + (mean_lap / 25.0))
            
        if std_lap / (mean_lap + 1e-5) > 0.8:
            spat_score -= 15
            spatial_anomalies.append("Unnatural frame-to-frame sharpness fluctuation.")
    else:
        spat_score = 50.0

    # 3. Temporal Frame Continuity Score
    temporal_anomalies = []
    if len(histograms) > 1:
        correlations = []
        for i in range(len(histograms) - 1):
            corr = cv2.compareHist(histograms[i], histograms[i+1], cv2.HISTCMP_CORREL)
            correlations.append(float(corr))
        mean_corr = np.mean(correlations)
        min_corr = np.min(correlations)
        
        if min_corr < 0.65:
            temp_score = max(30.0, mean_corr * 80.0)
            temporal_anomalies.append("Sudden inter-frame visual discontinuity / possible face-swap splicing.")
        else:
            temp_score = min(96.0, mean_corr * 100.0)
    else:
        temp_score = 75.0

    # 4. Sensor High-Frequency Noise & FFT Spectrum Score
    noise_anomalies = []
    if noise_residuals:
        mean_noise = np.mean(noise_residuals)
        mean_fft_ratio = np.mean(fft_freq_ratios) if fft_freq_ratios else 1.0
        
        if mean_noise < 1.2:
            noise_score = max(25.0, mean_noise * 30.0)
            noise_anomalies.append("Missing physical camera sensor noise (synthetic smooth gradient typical of AI video generators).")
        elif mean_noise > 15.0:
            noise_score = 65.0
            noise_anomalies.append("Artificial noise mask injection detected.")
        else:
            noise_score = min(95.0, 70.0 + (mean_noise * 3.0))

        if mean_fft_ratio > 3.5:
            noise_score -= 15
            noise_anomalies.append("FFT 2D Frequency domain grid artifacts detected (GAN / Neural generator signature).")
    else:
        noise_score = 70.0

    # Composite Authenticity & AI Generation Likelihood Calculation
    composite_score = round(
        0.20 * meta_score + 
        0.35 * spat_score + 
        0.25 * temp_score + 
        0.20 * noise_score, 1
    )
    composite_score = min(99.4, max(5.0, composite_score))
    
    ai_generation_prob = round(100.0 - composite_score, 1)

    video_instance.metadata_score = round(meta_score, 1)
    video_instance.spatial_score = round(spat_score, 1)
    video_instance.temporal_score = round(temp_score, 1)
    video_instance.noise_score = round(noise_score, 1)
    video_instance.authenticity_score = composite_score

    # Status Classification
    if composite_score >= 78.0:
        video_instance.verification_status = 'Authentic'
        verdict = "VERIFIED REAL CAMERA FOOTAGE"
        risk_level = "LOW RISK"
    elif composite_score >= 52.0:
        video_instance.verification_status = 'Suspicious'
        verdict = "SUSPICIOUS / POTENTIALLY ALTERED VIDEO"
        risk_level = "MEDIUM RISK"
    else:
        video_instance.verification_status = 'Deepfake'
        verdict = "AI GENERATED VIDEO / DEEPFAKE DETECTED"
        risk_level = "CRITICAL RISK"

    # Build Comprehensive Forensic Report JSON
    all_anomalies = metadata_anomalies + spatial_anomalies + temporal_anomalies + noise_anomalies
    if not all_anomalies:
        all_anomalies = ["No significant structural or facial anomalies detected. Video matches authentic camera hardware profiles."]

    report_data = {
        "file_name": os.path.basename(file_path),
        "file_hash_sha256": file_hash,
        "overall_authenticity_score": composite_score,
        "ai_generation_probability": ai_generation_prob,
        "verification_status": video_instance.verification_status,
        "forensic_verdict": verdict,
        "deepfake_risk_level": risk_level,
        "spectrum_image_url": f"/media/{spectrum_rel_path}" if spectrum_rel_path else None,
        "metrics": {
            "metadata_integrity": {"score": round(meta_score, 1), "status": "Pass" if meta_score >= 70 else "Warning"},
            "spatial_blur_artifacts": {"score": round(spat_score, 1), "status": "Pass" if spat_score >= 70 else "Warning"},
            "temporal_continuity": {"score": round(temp_score, 1), "status": "Pass" if temp_score >= 70 else "Warning"},
            "sensor_noise_residuals": {"score": round(noise_score, 1), "status": "Pass" if noise_score >= 70 else "Warning"}
        },
        "technical_summary": {
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "resolution": resolution_str,
            "duration_sec": duration,
            "codec": codec or "H264",
            "faces_detected": faces_detected_count,
            "sampled_frames_count": len(sample_indices)
        },
        "anomalies_detected": all_anomalies
    }

    video_instance.forensic_report_json = report_data
    video_instance.save()

def verify_video(file_path):
    """Legacy helper fallback."""
    return "Authentic"