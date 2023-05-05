import uuid

uid = {f"uuid{i}": uuid.uuid4() for i in range(1, 21)}

ORGANISATION_DATA = {
    "id": [uid["uuid1"], uid["uuid2"], uid["uuid3"]],
    "organisation_name": ["Test Organisation", "Test Organisation 2", "Test Organisation 3"],
    "geography": ["Earth", "Mars", "Venus"],
}


CONTACT_DATA = {
    "id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "email_address": ["jane@example.com", "john@example.com", "joe@example.com"],
    "contact_name": ["Jane Doe", "John Doe", "Joe Bloggs"],
    "telephone": ["123", "789", "334"],
    "organisation_id": [str(uid["uuid1"]), str(uid["uuid1"]), str(uid["uuid3"])],
}

# TODO add further test data for all models. Need to generate some new UUIDs for use in further table fk lookups.
