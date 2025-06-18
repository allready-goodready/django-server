from config import settings


def global_variables(request):
    profile_image_url = ""
    if request.user.is_authenticated:
        try:
            profile_image_url = request.user.profile.image.url
        except Exception:
            profile_image_url = "/static/images/user.jpg"  
    return {
        "google_api_key": settings.GOOGLE_API_KEY,
        "username": request.user.username if request.user.is_authenticated else "",
        "profile_image_url": profile_image_url,
    }