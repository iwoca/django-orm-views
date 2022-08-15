import re
from typing import Optional
from django.db.models import QuerySet

try:
    # Django 3.1 and above
    from django.utils.functional import classproperty
except ImportError:
    from django.utils.decorators import classproperty

from .constants import SUB_SCHEMA_NAME, ParameterisedSQL
from .register import AutoRegisterMixin
from .exceptions import InvalidViewDepencies
from .not_managed_model import NotManagedModel


class HiddenViewMixin:
    hidden = True


class PostgresMaterialisedViewMixin:
    """Mixin to make a subclass of AutoRegisterMixin and BasePostgresView materialized.

    Attributes:
        pk_field (str): is an optional string with the column name from the view.
            This column will get a unique index. Having a unique index will allow this
            view to refresh concurrently.
    """

    pk_field: Optional[str] = None

    @classproperty
    def creation_sql(cls) -> ParameterisedSQL:
        parameterised_sql = cls._parameterised_sql
        sql = f"CREATE MATERIALIZED VIEW {cls.name_with_schema} AS {parameterised_sql.sql};"

        if cls.pk_field:
            sql += f"CREATE UNIQUE INDEX {cls.name}_{cls.pk_field} ON {cls.name_with_schema} ({cls.pk_field});"

        return ParameterisedSQL(
            sql=sql,
            params=parameterised_sql.params,
        )

    @classmethod
    def get_refresh_sql(cls, concurrently: bool = False) -> str:
        """Get the SQL statement to refresh the view.

        Args:
            concurrently (bool): if True the statement will be for a concurrent refresh

        Raises:
            ValueError: If concurrently is True and there's no pk_field
        """
        statement_parts = ["REFRESH MATERIALIZED VIEW"]
        if concurrently:
            if not cls.pk_field:
                raise ValueError("Can't refresh concurrently without a pk_field")
            statement_parts.append("CONCURRENTLY")
        statement_parts.append(f"{cls.name_with_schema};")
        return " ".join(statement_parts)


class BasePostgresView:
    view_dependencies = []
    prefix = None
    hidden = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if len(set([view.database for view in cls.view_dependencies])) > 1:
            raise InvalidViewDepencies("View dependencies connect to more than one database")


    @classproperty
    def _parameterised_sql(cls) -> ParameterisedSQL:
        """Used to create a common interface in the two base classes.  This is
        entirely internal and externals methods are exposed to set this accordingly.
        """
        raise NotImplementedError

    @classproperty
    def creation_sql(cls) -> ParameterisedSQL:
        """Returns the SQL to create the view.

        Note that this creates the views under the schema SUB_SCHEMA_NAME.  This
        is because it makes views much simpler to discover and delete (drop the schema
        w/ cascade => views are all removed).

        This also leaves the cursor to deal with the parameters correctly.
        The example error case here is a datetime:

        ```
            >>> queryset = TableA.objects.filter(created__lte=datetime.datetime(2019, 1, 1, tzinfo=pytz.UTC))
            >>> str(queryset.query)
        ```

        Django will call `__str__` on the datetime, which is not the same representation as that of Postgres.
        params is a kwarg given by the cursor to execute SQL which leaves the responsibility of
        representation to the cursor itself (in this case, an ISO Format datetime,
        which is not the default `__str__` in python)
        """
        parameterised_sql = cls._parameterised_sql
        return ParameterisedSQL(
            sql=f'CREATE VIEW {cls.name_with_schema} AS {parameterised_sql.sql};',
            params=parameterised_sql.params
        )

    @classproperty
    def name(cls) -> str:
        """The name of the view.  This can be overridden by subclasses
        if you'd like to not depend on the class name, but for now it splits
        based on camelcase.

        e.g.:
            MyPostgresView -> mypostgresview
            MyPostgreSQLView -> mypostgressqlview

        """
        word = cls.__name__
        word = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1\2', word)
        word = re.sub(r'([a-z\d])([A-Z])', r'\1\2', word)
        word = word.replace('-', '')
        word = word.lower()

        if cls.prefix is not None:
            word = f'{cls.prefix}_{word}'

        return word

    @classproperty
    def name_with_schema(cls) -> str:
        """The name of the view nested under the name of the base schema."""
        return f'{SUB_SCHEMA_NAME}.{cls.name}'

    @classproperty
    def schema_qry(cls) -> ParameterisedSQL:
        qry = f"""
          SELECT
           column_name,
           data_type
        FROM    
           information_schema.columns
        WHERE
           table_schema = '{SUB_SCHEMA_NAME}'
           AND table_name = '{cls.name}'
        
        """
        return ParameterisedSQL(sql=qry, params=[])


class PostgresViewFromQueryset(AutoRegisterMixin, BasePostgresView, should_register=False):
    """Used as the interface to the package for defining views based on a Django Queryset."""

    @classmethod
    def get_queryset(cls) -> QuerySet:
        raise NotImplementedError

    @classproperty
    def _parameterised_sql(cls) -> ParameterisedSQL:
        qset = cls.get_queryset()
        sql, params = qset.query.sql_with_params()
        parameterised_sql = ParameterisedSQL(sql=sql, params=params)
        return parameterised_sql


class PostgresViewFromSQL(AutoRegisterMixin, BasePostgresView, should_register=False):
    """Used as the interface to the package for defining views based on raw SQL"""

    @classproperty
    def sql(cls):
        raise NotImplementedError

    @classproperty
    def _parameterised_sql(cls) -> ParameterisedSQL:
        return ParameterisedSQL(sql=cls.sql, params=[])


class ReadableViewFromQueryset(
    PostgresViewFromQueryset, NotManagedModel, is_abstract_model=True, should_register=False
):
    class Meta:
        abstract = True


class ReadableViewFromSQL(PostgresViewFromSQL, NotManagedModel, is_abstract_model=True, should_register=False):
    class Meta:
        abstract = True
