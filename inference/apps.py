from django.apps import AppConfig
class InferenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inference'

    def ready(self):
        import inference.signals  # Ensure signals are imported and registered