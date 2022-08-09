import itertools

from typing import Optional

from django.db import connections, transaction

from .exceptions import CyclicDependencyError
from .constants import SUB_SCHEMA_NAME, LOG
from .register import registry, register_all_views
from .views import PostgresMaterialisedViewMixin


def topological_sort_views(list_of_views):
    """Implements a topological sort to build the views based on their dependencies.  This
    is because the SQL needs to be executed in the correct order.

    Returns an ordered list of views
    Raises CyclicDependencyError if there is a cyclic dependency between the views.
    """

    def _sets_of_views_deps_iterator(views):
        """Builds an iterator based on the number of dependencies, popping off
        any which no longer have any dependencies.
        """

        view_to_deps = {view: set(view.view_dependencies) for view in views}

        while True:
            ordered = set(item for item, dep in view_to_deps.items() if not dep)
            if not ordered:
                break
            yield ordered

            view_to_deps = {
                item: (dep - ordered)
                for item, dep in view_to_deps.items()
                if item not in ordered
            }

        if view_to_deps:
            raise CyclicDependencyError(f'A Cyclic dependency exists amongst {view_to_deps}')

    # Flatten the list of sets
    return list(itertools.chain.from_iterable(_sets_of_views_deps_iterator(list_of_views)))


def sync_views(
        grant_select_permissions_to_user: Optional[str] = None
):
    """This function syncs all the views in the registry.

    This effectively destroys + recreates all views within a transaction. Views live under a separate schema
    so that we can tear them down/recreate them simply.

    Implements topological sorting in order to analyse interdependencies and execute the SQL in the correct order.

    Note, it assumes that the registry has been built (i.e. depending on the AppConfig of this app calling ready).
    """
    logger = LOG.getChild('sync')

    logger.info('Syncing view registry for databases %s', list(registry.keys()))

    register_all_views()

    for database, views in registry.items():
        views_to_generate = topological_sort_views(views)
        with connections[database].cursor() as cursor:
            with transaction.atomic():
                # Drop the view schema and recreate it
                cursor.execute(f'DROP SCHEMA IF EXISTS {SUB_SCHEMA_NAME} CASCADE; CREATE SCHEMA {SUB_SCHEMA_NAME};')

                # Execute each SQL statement from the views
                for view in views_to_generate:
                    LOG.info("generating view %s", view.name)
                    cursor.execute(view.creation_sql.sql, params=view.creation_sql.params)

                # Re-grant permissions.
                if grant_select_permissions_to_user is not None:
                    cursor.execute(
                        f'GRANT USAGE ON SCHEMA {SUB_SCHEMA_NAME} TO {grant_select_permissions_to_user};'
                    )
                for view in views_to_generate:
                    if view.hidden or grant_select_permissions_to_user is None:
                        continue
                    cursor.execute(
                        f'GRANT SELECT ON {SUB_SCHEMA_NAME}.{view.name} TO {grant_select_permissions_to_user};'
                    )
        LOG.info('Successfully sync\'d %s views for %s database', len(views_to_generate), database)

    LOG.info('Successfully sync\'d %s views', len(registry))


def refresh_materialized_view(
    view: PostgresMaterialisedViewMixin, concurrently: bool = False
):
    """Refresh the given materialized view."""
    with connections[view.database].cursor() as cursor:
        cursor.execute(view.get_refresh_sql(concurrently))
