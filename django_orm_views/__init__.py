from .views import (
    PostgresMaterialisedViewMixin,
    PostgresViewFromQueryset,
    PostgresViewFromSQL,
)

from .sync import (
    sync_views,
    topological_sort_views,
)

default_app_config = 'django_orm_views.apps.DjangoPostgresViewsConfig'
