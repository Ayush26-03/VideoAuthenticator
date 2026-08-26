from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse, HttpResponseForbidden
import json

from .models import Video
from .forms import VideoForm, UserRegistrationForm
from .utils import analyze_video

def video_list(request):
    """Gallery view of all uploaded videos with search, filter, and stats summary."""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip()

    videos = Video.objects.all().order_by('-uploaded_at')

    if query:
        videos = videos.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(file_hash__icontains=query)
        )

    if status_filter and status_filter != 'all':
        videos = videos.filter(verification_status=status_filter)

    # Compute Statistics Overview
    all_videos = Video.objects.all()
    total_count = all_videos.count()
    authentic_count = all_videos.filter(verification_status='Authentic').count()
    deepfake_count = all_videos.filter(verification_status='Deepfake').count()
    suspicious_count = all_videos.filter(verification_status='Suspicious').count()
    
    avg_score_res = all_videos.aggregate(Avg('authenticity_score'))
    avg_score = round(avg_score_res['authenticity_score__avg'] or 0.0, 1)

    stats = {
        'total': total_count,
        'authentic': authentic_count,
        'deepfake': deepfake_count,
        'suspicious': suspicious_count,
        'avg_score': avg_score
    }

    context = {
        'videos': videos,
        'stats': stats,
        'query': query,
        'selected_status': status_filter
    }
    return render(request, 'video/video_list.html', context)

@login_required
def video_upload(request):
    """Handles video upload and triggers multi-layer forensic AI analysis."""
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            video.verification_status = 'Processing'
            video.save()
            
            # Execute AI Forensic Video Verification
            try:
                analyze_video(video)
                messages.success(request, f"Video '{video.title}' successfully analyzed! Authenticity status: {video.verification_status}.")
                return redirect('video_detail', pk=video.pk)
            except Exception as e:
                messages.error(request, f"Error analyzing video: {str(e)}")
                video.verification_status = 'Error'
                video.save()
                return redirect('video_list')
        else:
            messages.error(request, "Failed to upload video. Please check form errors.")
    else:
        form = VideoForm()

    return render(request, 'video/video_upload.html', {'form': form})

def video_detail(request, pk):
    """Interactive video forensic report dashboard."""
    video = get_object_or_404(Video, pk=pk)
    report = video.forensic_report_json or {}
    
    context = {
        'video': video,
        'report': report,
        'report_json_pretty': json.dumps(report, indent=2)
    }
    return render(request, 'video/video_detail.html', context)

@login_required
def video_delete(request, pk):
    """Deletes a video if user owns it or is superuser."""
    video = get_object_or_404(Video, pk=pk)
    if video.uploaded_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this video.")
    
    if request.method == 'POST':
        title = video.title
        video.file.delete(save=False)
        if video.thumbnail:
            video.thumbnail.delete(save=False)
        video.delete()
        messages.success(request, f"Video '{title}' has been deleted.")
        return redirect('video_list')
        
    return render(request, 'video/video_confirm_delete.html', {'video': video})

def register(request):
    """User Sign Up view."""
    if request.user.is_authenticated:
        return redirect('video_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to VideoAuthenticator, {user.username}! Your account has been created.")
            return redirect('video_list')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def export_report(request, pk):
    """Exports forensic report as downloadable JSON file."""
    video = get_object_or_404(Video, pk=pk)
    report = video.forensic_report_json or {}
    response = JsonResponse(report, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="forensic_report_video_{video.pk}.json"'
    return response
