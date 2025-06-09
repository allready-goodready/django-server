from config import settings


def global_variables(request):
    return {
        "google_api_key": settings.GOOGLE_API_KEY,
        # "username": request.user.username if request.user.is_authenticated else "",
        # "profile_image_url": request.user.profile.image.url if request.user.is_authenticated else "",
    }
