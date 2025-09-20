from django.apps import AppConfig


class TongueTwisterConfig(AppConfig):
    name = 'tonguetwister'

    def ready(self):
        import tonguetwister.signals
