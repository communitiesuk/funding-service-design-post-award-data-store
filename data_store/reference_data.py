from pathlib import Path

import pandas as pd

from data_store.controllers.mappings import DataMapping
from data_store.db import db
from data_store.db.entities import Fund, GeospatialDim, ReportingRound


def seed_geospatial_dim_table():
    """
    Input seed data to geospatial_dim table using the mappings in /tests/resources/geospatial_dim.csv

    If the table is empty then it will be directly populated with the seed data. If data already exists,
    the script will merge any incoming rows where the postcode_prefix matches what's in the database
    to preserve any FK relationships.

    This is used to populate the db locally, as geospatial reference data is otherwise populated via
    migrations of SQL insertions for higher regions."""

    resources = Path(__file__).parent / ".." / "tests" / "resources"
    geospatial_dim_df = pd.read_csv(resources / "geospatial_dim.csv")

    geospatial_dim_mapping = DataMapping(
        table="geospatial_dim",
        model=GeospatialDim,
        column_mapping={
            "id": "id",
            "postcode_prefix": "postcode_prefix",
            "itl1_region_code": "itl1_region_code",
            "itl1_region_name": "itl1_region_name",
        },
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


def seed_reporting_round_table():
    """
    Seed the reporting round table with the data in /tests/resources/reporting_round.csv
    """
    resources = Path(__file__).parent / ".." / "tests" / "resources"
    reporting_round_df = pd.read_csv(resources / "reporting_round.csv")
    for _, row in reporting_round_df.iterrows():
        reporting_round = ReportingRound.query.filter_by(
            round_number=row["round_number"], fund_id=row["fund_id"]
        ).first()
        if reporting_round is None:
            reporting_round = ReportingRound(
                round_number=row["round_number"],
                fund_id=row["fund_id"],
                observation_period_start=row["observation_period_start"],
                observation_period_end=row["observation_period_end"],
                submission_period_start=(sps if not pd.isnull(sps := row["submission_period_start"]) else None),
                submission_period_end=(spe if not pd.isnull(spe := row["submission_period_end"]) else None),
            )
        else:
            reporting_round.observation_period_start = row["observation_period_start"]
            reporting_round.observation_period_end = row["observation_period_end"]
            reporting_round.submission_period_start = (
                sps if not pd.isnull(sps := row["submission_period_start"]) else None
            )
            reporting_round.submission_period_end = spe if not pd.isnull(spe := row["submission_period_end"]) else None
        db.session.add(reporting_round)
    db.session.commit()
