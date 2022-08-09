import importlib
from collections import defaultdict
from django.apps import apps
from .constants import LOG, VIEWS_FILE_NAME, DEFAULT_DATABASE_LABEL


registry = defaultdict(set)


class AutoRegisterMixin:
    """
    This is used to build up the registry.

    Note that we instantiate the views when we're adding them
    to the registry.  This is a bit of a hack to get around the
    fact that we are required to conform to django's standard of
    class inheritance (can't have a Queryset on the module level).
    """

    database = DEFAULT_DATABASE_LABEL

    def __init_subclass__(cls, should_register: bool = True, **kwargs):
        """This implements a should_register var, which allows us to implement
        base classes without those base classes being registered themselves.

        This can be used if we want to implement a new type of base class
        which can add functionality for implementing views.
        """
        super().__init_subclass__(**kwargs)
        if not should_register:
            return

        # Instantiating the view here because we don't need it as a class
        registry[cls.database].add(cls)


def register_all_views():
    """
    Forces import of all views which will then register themselves using AutoRegisterMixin.
    """
    LOG.getChild(__name__).info('Importing all Postgres views from .%s files/packages in apps', VIEWS_FILE_NAME)
    # Iterate over all app configs to build out our list of postgres views
    for app_label, app_config in apps.app_configs.items():

        # Assume we have a top level module/package called postgres_views in our app.
        import_name = app_config.name
        to_import = f'{import_name}.{VIEWS_FILE_NAME}'
        try:
            importlib.import_module(to_import)
        except ImportError:
            continue
