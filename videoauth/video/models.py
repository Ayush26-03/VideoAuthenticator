from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Authentic', 'Authentic'),
        ('Suspicious', 'Suspicious'),
        ('Deepfake', 'Deepfake / AI-Generated'),
        ('Error', 'Analysis Failed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='video/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Forensic & Verification Fields
    verification_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    authenticity_score = models.FloatField(default=0.0) # 0 to 100%
    file_hash = models.CharField(max_length=64, blank=True)
    
    # Technical Metadata
    duration = models.FloatField(default=0.0)
    resolution = models.CharField(max_length=50, blank=True)
    fps = models.FloatField(default=0.0)
    frame_count = models.IntegerField(default=0)
    video_codec = models.CharField(max_length=50, blank=True)
    has_audio = models.BooleanField(default=False)
    
    # Sub-scores (0 to 100)
    metadata_score = models.FloatField(default=0.0)
    spatial_score = models.FloatField(default=0.0)
    temporal_score = models.FloatField(default=0.0)
    noise_score = models.FloatField(default=0.0)
    
    # Forensic JSON details & thumbnail
    forensic_report_json = models.JSONField(default=dict, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    def __str__(self):
        return self.title

