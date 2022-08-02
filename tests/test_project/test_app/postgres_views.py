from django_orm_views import PostgresViewFromQueryset, PostgresViewFromSQL
from django.db.models import F

from .models import TestModel, TestModelWithForeignKey


# -----------------------------------------------------------------------------
# From Queryset
# -----------------------------------------------------------------------------


class SimpleViewFromQueryset(PostgresViewFromQueryset):

    prefix = 'test'

    def get_queryset(self):
        return TestModel.objects.values()


class ComplexViewFromQueryset(PostgresViewFromQueryset):

    prefix = 'test'

    def get_queryset(self):

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
