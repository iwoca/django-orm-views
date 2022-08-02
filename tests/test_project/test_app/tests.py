import datetime

from django_orm_views.sync import sync_views, refresh_materialized_view
from django.db import connection
from django.test import TestCase

from .models import TestModel, TestModelWithForeignKey
from .postgres_views import SimpleMaterializedView


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

