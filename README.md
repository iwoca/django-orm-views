# django_orm_views

## What does this support?
This package adds support to Django for **writing** Postgres views using:
* Raw SQL
* Querysets

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
   

## What does this not support?

Reading the views in an ORM-friendly way.

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

* Add `'django_orm_views'` to your `INSTALLED_APPS`
* Create a `postgres_views.py` (file or package) inside any app
* Add a `PostgresViewFromQueryset` or `PostgresViewFromSQL` 
to your `postgres_views.py` (as above)
* run `./manage.py sync_views`

## What's still to come?

* Views depending on other views - this needs
some small dependency analysis which we haven't
implemented as of yet.
* Making the package more configurable using settings.
* Consideration of implementing reads using the ORM
* Consideration of 0 downtime deployments with views.
Note, this can still be achieved with the current implementation,
but a bad migration (with a view depending) could
cascade a view and create downtime.  Ideally migrations + 
view creation should happen in a single transaction.
* Actual tests!
