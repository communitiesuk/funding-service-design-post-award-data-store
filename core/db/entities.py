import uuid  # noqa

from sqlalchemy import Column, String

from core.db import db
from core.db.types import GUID


class Contact(db.Model):
    id = Column(
        "id",
        GUID(),  # this should be UUIDType once using Postgres
        default=uuid.uuid4,
        primary_key=True,
    )
    email_address = Column("email", String, nullable=False)
    contact_name = Column("contact_name", String, nullable=True)
    organisation = Column("organisation", String, nullable=True)
    telephone = Column("telephone", String, nullable=True)
