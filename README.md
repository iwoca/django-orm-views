# django_orm_views

The package for managing database views using django, without the migrations.

## What does this support?
This package adds support to Django for **writing** Postgres views using:
* Raw SQL
* Django Querysets

They look something like this:

```python
class MySQLView(PostgresViewFromSQL):
    sql = """
       SELECT col_a, col_b FROM table_1;
    """
```

```python
class MyQuerysetView(PostgresViewFromQueryset):
    
    def get_queryset(self):
        return (
            Table1
            .objects
            .values('col_a', 'col_b')
        )
```

See some more examples in the tests (here)[https://github.com/iwoca/django-orm-views/blob/main/tests/test_project/test_app/postgres_views.py]


This also supports the construction of materialised views via `PostgresMaterialisedViewMixin`. Note that the function `refresh_materialized_view` will
need to be managed by the user in order to keep these up to date where required.
   

## What does this not support?

* Reading from the views in an ORM-friendly way.
* Any database engines aside from Postgres (unless syntax happens to be the same!)

## When should I use this?

Our use-case is for a database which is managed by Django
in which we would like to provide an analytics-friendly
representation of some of our data.  This involves giving
analytics direct access to our database (whilst using a
permissions framework), but using views to expose the data
in a more simple way, as well as obscuring data which
we consider personally identifiable/sensitive.

There are other frameworks existing which do similar things,
usually including reads via the ORM.  We found that these
packages all generate migrations (despite being unmanaged)
and we wanted to remove this from the django migrations process
altogether - there seemed to be no value add by including
migrations and they would just muddy our migration states.

## Cool! But how do I use this?

* `pip install django-orm-views`
* Add `'django_orm_views'` to your `INSTALLED_APPS`
* Create a `postgres_views.py` (file or package) inside any app
* Add a `PostgresViewFromQueryset` or `PostgresViewFromSQL` 
to your `postgres_views.py` (as above)
* run `./manage.py sync_views`

A `postgres_views.py` file might look something like the following:

```python
class ComplexViewFromQueryset(PostgresViewFromQueryset):

    prefix = 'test'  # This is optional, but allows you to prefix the table names for views

    def get_queryset(self):  # Return a `.values` with the query you desire
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
```

When we run the `./manage.py sync_views`, we'll create a view called `test_complexviewfromqueryset` under
the `views` schema.

Note, you can put `./manage.py sync_views` into your CI/CD.  It works by:
* Opening a transaction
* Dropping the views schema
* Recreating the views schema
* Recreating all views under that schema
* Committing the transaction

## What's still to come?

* Support for more database engines.  This currently only supports Postgres, 
but should be a reasonably light shift to support other database engines.
* Support for ORM-friendly readable views (optionally!)
* Making the package more configurable using settings.
* Consideration of implementing reads using the ORM
* Consideration of 0 downtime deployments with views.
  * Note, this can still be achieved with the current implementation,
  but a bad migration (with a view depending) could
  cascade a view and create downtime.  Ideally migrations + 
  view creation should happen in a single transaction.

## Contributing

Feel free to fork the package and propose changes.  The repo comes with a test django project which
can be used to effectively test changes.  It also demonstrates the functionality pretty well.
