from django.contrib.auth import logout


class LogoutBannedUserMiddleware:
    """
    Log out banned users when they try to use the website
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
        return self.get_response(request)
