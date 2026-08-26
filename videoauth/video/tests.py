import os
import tempfile
import cv2
import numpy as np
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from video.models import Video
from video.utils import analyze_video, compute_sha256

class VideoAuthenticatorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.client = Client()
        self.client.login(username='testuser', password='password123')

        # Create a temporary synthetic MP4 video file
        self.temp_video_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        self.temp_video_path = self.temp_video_file.name
        self.temp_video_file.close()

        # Generate 15 frames of synthetic video (width=320, height=240, 30fps)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.temp_video_path, fourcc, 30.0, (320, 240))
        for i in range(15):
            # Create a moving shape with subtle texture noise
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            cv2.circle(frame, (50 + i * 10, 120), 30, (0, 255, 100), -1)
            # Add synthetic sensor noise
            noise = np.random.normal(0, 5, frame.shape).astype(np.uint8)
            frame = cv2.add(frame, noise)
            out.write(frame)
        out.release()

    def tearDown(self):
        if os.path.exists(self.temp_video_path):
            try:
                os.remove(self.temp_video_path)
            except Exception:
                pass

    def test_sha256_computation(self):
        file_hash = compute_sha256(self.temp_video_path)
        self.assertEqual(len(file_hash), 64)

    def test_analyze_video_engine(self):
        with open(self.temp_video_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile("test_video.mp4", f.read(), content_type="video/mp4")

        video = Video.objects.create(
            title="Test Synthetic Video",
            description="Unit test video upload",
            file=uploaded_file,
            uploaded_by=self.user,
            verification_status="Processing"
        )

        analyze_video(video)
        video.refresh_from_db()

        self.assertIn(video.verification_status, ['Authentic', 'Suspicious', 'Deepfake'])
        self.assertGreater(video.authenticity_score, 0)
        self.assertGreater(video.fps, 0)
        self.assertEqual(len(video.file_hash), 64)
        self.assertIsNotNone(video.forensic_report_json)
        self.assertIn('file_hash_sha256', video.forensic_report_json)

    def test_video_list_view(self):
        response = self.client.get(reverse('video_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Forensic Video Dashboard")

    def test_video_upload_view(self):
        with open(self.temp_video_path, 'rb') as f:
            post_data = {
                'title': 'Uploaded Test Video',
                'description': 'Description for test',
                'file': f
            }
            response = self.client.post(reverse('video_upload'), post_data)
        
        self.assertEqual(response.status_code, 302) # Redirects to detail page
        self.assertTrue(Video.objects.filter(title='Uploaded Test Video').exists())
