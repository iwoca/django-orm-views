import datetime

from django_orm_views.sync import sync_views, refresh_materialized_view
from django.db import connection
from django.test import TestCase

from .models import TestModel, TestModelWithForeignKey
from .postgres_views import (
    SimpleMaterializedView,
    ReadableTestViewFromQueryset,
    ReadableTestViewFromSQL,
)


class BaseTestCase(TestCase):

    def setUp(self):
        sync_views()

    def _execute_raw_sql(self, sql, params=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


class TestSimpleViewFromQueryset(BaseTestCase):

    def test_view_generates_and_returns_as_expected(self):
        test_data = TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        result = self._execute_raw_sql("""
            SELECT * FROM "views"."test_simpleviewfromqueryset";
        """)

        self.assertEqual(
            result,
            [
                (
                    test_data.id,
                    2,
                    'A',
                    datetime.date(2019, 1, 1),
                    datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
                )
            ]
        )


class TestComplexViewFromQueryset(BaseTestCase):

    def test_view_generates_and_returns_as_expected(self):
        test_data = TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        test_fk = TestModelWithForeignKey.objects.create(foreign_key=test_data)

        result = self._execute_raw_sql(
            """
                SELECT * FROM "views"."test_complexviewfromqueryset"
            """
        )

        self.assertEqual(
            result,
            [
                (
                    test_fk.id,
                    test_data.id,
                    2,
                    'A',
                    datetime.date(2019, 1, 1),
                    datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc),
                    4
                )
            ]
        )


class TestSimpleViewFromSQL(BaseTestCase):

    def test_view_generates_and_returns_as_expected(self):
        test_data = TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        result = self._execute_raw_sql("""
            SELECT * FROM "views"."test_simpleviewfromsql";
        """)

        self.assertEqual(
            result,
            [
                (
                    test_data.id,
                    2,
                    'A',
                    datetime.date(2019, 1, 1),
                    datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
                )
            ]
        )


class TestComplexViewFromSQL(BaseTestCase):

    def test_view_generates_and_returns_as_expected(self):
        test_data = TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        test_fk = TestModelWithForeignKey.objects.create(foreign_key=test_data)

        result = self._execute_raw_sql(
            """
                SELECT * FROM "views"."test_complexviewfromsql"
            """
        )

        self.assertEqual(
            result,
            [
                (
                    test_fk.id,
                    test_data.id,
                    2,
                    'A',
                    datetime.date(2019, 1, 1),
                    datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc),
                    4
                )
            ]
        )


class TestDependentView(BaseTestCase):

    """It would probably be ideal to test the "bad case" of missing dependencies, of cyclic dependencies,
    but that would require more thought.
    """

    def test_view_generates_and_returns_as_expected(self):
        test_data = TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        result = self._execute_raw_sql("""
            SELECT * FROM "views"."test_dependentview";
        """)

        self.assertEqual(
            result,
            [
                (
                    test_data.id,
                    2,
                    'A',
                    datetime.date(2019, 1, 1),
                    datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
                )
            ]
        )


class TestMaterialisedView(BaseTestCase):

    def test_no_results_pre_generation(self):
        TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        result = self._execute_raw_sql("""
            SELECT * FROM "views"."test_simplematerializedview";
        """)

        self.assertEqual(
            result,
            []
        )

    def test_materialised_non_concurrently_returns_results(self):
        test_data = TestModel.objects.create(
            integer_col=2,
            character_col='A',
            date_col=datetime.date(2019, 1, 1),
            datetime_col=datetime.datetime(2019, 1, 1),
        )
        refresh_materialized_view(SimpleMaterializedView(), concurrently=False)

        result = self._execute_raw_sql("""
            SELECT * FROM "views"."test_simplematerializedview";
        """)

        self.assertEqual(
            result,
            [
                (
                    test_data.id,
                    2,
                    'A',
                    datetime.date(2019, 1, 1),
                    datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
                )
            ]
        )

    def test_refresh_materialised_doesnt_error(self):
        # We can't check the output here because the database will do this concurrently
        # and it could lead to a flakey test. We instead check the function doesn't error.
        refresh_materialized_view(SimpleMaterializedView(), concurrently=True)


class TestReadableViews(BaseTestCase):

    @staticmethod
    def _add_row(**kwargs):
        default_fields = {
            "integer_col": 1,
            "character_col": "a",
            "date_col": datetime.date(2019, 1, 1),
            "datetime_col": datetime.datetime(2019, 1, 1)
        }
        return TestModel.objects.create(**default_fields, **kwargs)

    def test_readable_view_from_queryset_no_results(self):
        results = ReadableTestViewFromQueryset.objects.values('id')
        self.assertEqual(results.count(), 0)

    def test_readable_view_from_queryset_with_results(self):
        test_data = self._add_row()
        results = list(ReadableTestViewFromQueryset.objects.values_list('id', flat=True))
        self.assertEqual(results, [test_data.id])

    def test_readable_view__does_not_exist_exception_raised_when_object_not_found(self):
        with self.assertRaises(ReadableTestViewFromQueryset.DoesNotExist):
            ReadableTestViewFromQueryset.objects.get(id=123)

    def test_readable_view__multiple_objects_exception_raised_when_multiple_objects_found(self):
        test_data_1 = self._add_row()
        test_data_2 = self._add_row()
        with self.assertRaises(ReadableTestViewFromQueryset.MultipleObjectsReturned):
            ReadableTestViewFromQueryset.objects.get(character_col=test_data_1.character_col)

    def test_readable_view_from_sql_no_results(self):
        results = ReadableTestViewFromSQL.objects.values('id')
        self.assertEqual(results.count(), 0)

    def test_readable_view_from_sql_with_results(self):
        test_data = self._add_row()
        results = list(ReadableTestViewFromSQL.objects.values_list('id', flat=True))
        self.assertEqual(results, [test_data.id])

