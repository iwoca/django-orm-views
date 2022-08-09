from django.db import models
from django.db.models import F
from django.utils.functional import classproperty

from django_orm_views.views import (
    PostgresViewFromQueryset,
    PostgresViewFromSQL,
    PostgresMaterialisedViewMixin,
    ReadableViewFromQueryset,
    ReadableViewFromSQL
)
from .models import TestModel, TestModelWithForeignKey


# -----------------------------------------------------------------------------
# From Queryset
# -----------------------------------------------------------------------------


class SimpleViewFromQueryset(PostgresViewFromQueryset):

    prefix = 'test'

    @classmethod
    def get_queryset(cls):
        return TestModel.objects.values()


class ComplexViewFromQueryset(PostgresViewFromQueryset):

    prefix = 'test'

    @classmethod
    def get_queryset(cls):

        return (
            TestModelWithForeignKey
            .objects
            .all()
            .annotate(
                double_integer_col=F('foreign_key__integer_col') * 2
            )
            .values(
                'id',
                'foreign_key__id',
                'foreign_key__integer_col',
                'foreign_key__character_col',
                'foreign_key__date_col',
                'foreign_key__datetime_col',
                'double_integer_col',
            )
        )


# -----------------------------------------------------------------------------
# From SQL
# -----------------------------------------------------------------------------


class SimpleViewFromSQL(PostgresViewFromSQL):

    prefix = 'test'
    sql = """
        SELECT * FROM test_app_testmodel
    """


class ComplexViewFromSQL(PostgresViewFromSQL):

    prefix = 'test'
    sql = """
        SELECT
            b.id as b__id,
            a.*,
            a.integer_col * 2 ddouble_integer_col
        FROM test_app_testmodel a
        LEFT JOIN test_app_testmodelwithforeignkey b ON a.id = b.foreign_key_id
    """


# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------


class DependentView(PostgresViewFromSQL):

    prefix = 'test'

    view_dependencies = [
        SimpleViewFromSQL
    ]

    sql = """
        SELECT * FROM "views"."test_simpleviewfromsql"
    """


# -----------------------------------------------------------------------------
# Materialized
# -----------------------------------------------------------------------------


class SimpleMaterializedView(PostgresMaterialisedViewMixin, PostgresViewFromQueryset):

    prefix = 'test'
    pk_field = 'id'

    @classmethod
    def get_queryset(cls):
        return TestModel.objects.values()


class ReadableTestViewFromQueryset(ReadableViewFromQueryset):

    id = models.IntegerField(primary_key=True)
    character_col = models.CharField(max_length=100)

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return TestModel.objects.values('id', 'character_col')


class ReadableTestViewFromSQL(ReadableViewFromSQL):

    id = models.IntegerField(primary_key=True)
    character_col = models.CharField(max_length=100)

    @classproperty
    def sql(cls) -> str:
        return """
            SELECT "id", "character_col" FROM test_app_testmodel
        """

