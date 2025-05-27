from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class CustomUserRateThrottle(UserRateThrottle):
    """
    Limits the rate of requests that an authenticated user can make.
    Example: '100/day' or '10/minute'.
    """
    scope = 'user_burst' 

class CustomAnonRateThrottle(AnonRateThrottle):
    """
    Limits the rate of requests that an unauthenticated user (anonymous) can make.
    """
    scope = 'anon_burst' 