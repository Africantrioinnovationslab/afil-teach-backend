from django.apps import AppConfig

class SessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sessions'
    label = 'learning_sessions'  # This is the app label that will be used in the database and migrations