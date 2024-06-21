import procrastinate

from config import Config

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(
        conninfo=Config.SQLALCHEMY_DATABASE_URI,
    ),
)
