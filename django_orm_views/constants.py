import logging
from typing import List, Any

from dataclasses import dataclass

SUB_SCHEMA_NAME = 'views'
VIEWS_FILE_NAME = 'postgres_views'

LOGGER_NAME = 'django_orm_views'
LOG = logging.getLogger(LOGGER_NAME)

SqlParam = Any


@dataclass
class ParameterisedSQL:
    sql: str
    params: List[SqlParam]


DEFAULT_DATABASE_LABEL = "default"
