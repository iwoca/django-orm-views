from django.apps import AppConfig

from .register import register_all_views


class DjangoPostgresViewsConfig(AppConfig):

    name = 'django_orm_views'
    app_label = 'django_orm_views'
    
    def ready(self):
        register_all_views()
