from core.db import db


def seed_test_database(model: db.Model, model_data: dict[list]) -> None:
    """
    Insert rows into a specified DB model table from a dict of test data.

    Test data consists of dict, keys are table rows and vals are lists of row data. Lists are positionally indexed,
    and list for each field must be the same length. Keys (column names) must match db field names (as they are
    inserted as key word arguments).

    :param model: a DB model class.
    :param model_data: dict of test seed data.
    """
    model_rows = []
    cols = len(next(iter(model_data.values())))
    for idx in range(cols):
        model_args = {key: val[idx] for key, val in model_data.items()}
        model_rows.append(model(**model_args))

    db.session.add_all(model_rows)
