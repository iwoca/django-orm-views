import datetime

from django_orm_views import sync_views
from django.db import connection
from django.test import TestCase

from .models import TestModel, TestModelWithForeignKey


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