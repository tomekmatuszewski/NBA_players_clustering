from pathlib import Path
from configparser import ConfigParser
import psycopg2

BASEDIR = Path(__file__).resolve().parent.parent.parent


class Postgres:

    def __init__(self, path):
        self.path = path
        self.config_params = self.config()

    def __enter__(self):
        print('Connecting to the PostgreSQL database...')
        self.conn = psycopg2.connect(**self.config_params)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        print('Database connection closed.')
        self.conn.close()

    def config(self, section='postgresql'):
        parser = ConfigParser()
        parser.read(self.path)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, self.path))
        return db


if __name__ == '__main__':
    path = BASEDIR / 'database.ini'
    with Postgres(path) as curr:
        curr.execute("SELECT * from test1")
        print(curr.fetchall())
