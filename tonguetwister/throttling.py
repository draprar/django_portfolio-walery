from rest_framework.throttling import AnonRateThrottle

class CustomAnonThrottle(AnonRateThrottle):
    rate = '1000/day'