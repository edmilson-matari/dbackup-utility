import pytest
import project
from psycopg2 import OperationalError

def test_mongodb_backup():
    assert project.mongodb_backup({'uri': 'any.uri', 'password': 'password', 'database': 'any'}) == False

def test_mysql_backup():
    assert project.mysql_backup({'host': 'localhost', 'user': 'any', 'database': 'anydb', 'password': 'pass'}) == False

def test_postgres_backup():
    assert project.postgresql_backup({'host': 'localhost', 'port': 5432, 'user': 'any', 'database': 'anydb', 'password': 'pass'}) == False
