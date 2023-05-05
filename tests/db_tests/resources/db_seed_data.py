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
    "organisation_id": [uid["uuid1"], uid["uuid1"], uid["uuid3"]],
}

PACKAGE_DATA = {
    "id": [uid["uuid7"], uid["uuid8"], uid["uuid9"]],
    "package_name": ["Regeneration Project", "North Eastern Scheme", "Southern Access Project"],
    "package_id": ["ABC00123", "GHSG001", "ABC05678"],
    "fund_type_id": ["HIJ", "LMN", "OPQR"],
    "organisation_id": [uid["uuid1"], uid["uuid2"], uid["uuid3"]],
    "name_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "project_sro_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "cfo_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "m_and_e_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
}
