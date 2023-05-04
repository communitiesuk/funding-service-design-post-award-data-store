import uuid

ORGANISATION_DATA = {
    "id": [
        uuid.UUID("9e50a53f-7115-4e90-9023-3e600b27f1db"),
        uuid.UUID("5c5d5d5a-7555-4b5c-bfea-1b9f2f555c5c"),
        uuid.UUID("d52f24a9-34b5-48b5-aec0-3d3d3e333ce3"),
    ],
    "organisation_name": ["Test Organisation", "Test Organisation 2", "Test Organisation 3"],
    "geography": ["Earth", "Mars", "Venus"],
}


CONTACT_DATA = {
    "id": [
        uuid.UUID("4eb6baa9-f7b9-4d51-938f-8ebc81214f72"),
        uuid.UUID("d22b2247-0e98-4d7b-83c6-1b7aa460c888"),
        uuid.UUID("8214d4e4-86c4-4f9e-b3e3-ba2df3a1a136"),
    ],
    "email_address": ["jane@example.com", "john@example.com", "joe@example.com"],
    "contact_name": ["Jane Doe", "John Doe", "Joe Bloggs"],
    "telephone": ["123", "789", "334"],
    "organisation_id": [
        str(uuid.UUID("9e50a53f-7115-4e90-9023-3e600b27f1db")),
        str(uuid.UUID("9e50a53f-7115-4e90-9023-3e600b27f1db")),
        str(uuid.UUID("d52f24a9-34b5-48b5-aec0-3d3d3e333ce3")),
    ],
}

# TODO add further test data for all models. Need to generate some new UUIDs for use in further table fk lookups.
