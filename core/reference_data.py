from pathlib import Path

import pandas as pd

from core.controllers.mappings import DataMapping
from core.db import db
from core.db.entities import Fund, GeospatialDim


def seed_geospatial_dim_table():
    """
    Input seed data to geospatial_dim table using the mappings in /tests/resources/geospatial_dim.csv
    but dropping the hardcoded id which is only used for tests.

    If the table is empty then it will be directly populated with the seed data. If data already exists,
    the script will merge any incoming rows where the postcode_prefix matches what's in the database
    to preserve any FK relationships.

    Updates to the seed data will require an update to the DataMapping below and to test_geospatial_dim_table.
    """

    resources = Path(__file__).parent / ".." / "tests" / "resources"
    geospatial_dim_df = pd.read_csv(resources / "geospatial_dim.csv")
    geospatial_dim_df["id"] = None

    geospatial_dim_mapping = DataMapping(
        table="geospatial_dim",
        model=GeospatialDim,
        column_mapping={
            "postcode_prefix": "postcode_prefix",
            "itl1_region_code": "itl1_region_code",
            "itl1_region_name": "itl1_region_name",
        },
        cols_to_jsonb=[
            "itl1_region_name",
        ],
    )

    mapped_geospatial_data = geospatial_dim_mapping.map_data_to_models(geospatial_dim_df)

    existing_geospatial_data = GeospatialDim.query.all()

    if existing_geospatial_data is None:
        db.session.add_all(mapped_geospatial_data)
    else:
        for geospatial_record in mapped_geospatial_data:
            previous_record = next(
                (
                    record
                    for record in existing_geospatial_data
                    if record.postcode_prefix == geospatial_record.postcode_prefix
                ),
                None,
            )
            if previous_record:
                geospatial_record.id = previous_record.id
                db.session.merge(geospatial_record)
            else:
                db.session.add(geospatial_record)

    db.session.commit()


def seed_fund_table():
    """
    Input seed data to fund_dim table using the mappings in /tests/resources/fund_dim.csv.

    This is used to populate the db locally, as fund reference data is otherwise populated via
    migrations of SQL insertions for higher regions.
    """

    resources = Path(__file__).parent / ".." / "tests" / "resources"
    fund_df = pd.read_csv(resources / "fund_dim.csv")

    fund_dim_mapping = DataMapping(
        table="fund_dim",
        model=Fund,
        column_mapping={
            "id": "id",
            "fund_code": "fund_code",
        },
    )

    mapped_fund_data = fund_dim_mapping.map_data_to_models(fund_df)

    existing_fund_data = Fund.query.all()

    if existing_fund_data is None:
        db.session.add_all(mapped_fund_data)
    else:
        for fund_record in mapped_fund_data:
            previous_record = next(
                (record for record in existing_fund_data if record.fund_code == fund_record.fund_code),
                None,
            )
            if previous_record:
                fund_record.id = previous_record.id
                db.session.merge(fund_record)
            else:
                db.session.add(fund_record)

    db.session.commit()
