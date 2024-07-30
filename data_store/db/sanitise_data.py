import subprocess

from sqlalchemy.orm.attributes import flag_modified

from data_store.db import db
from data_store.db.entities import PlaceDetail, ProgrammeJunction, RiskRegister, Submission
from data_store.db.sanitisation_utils import f, shuffle_word

"""
Script to sanitise data in the database. This script is used to anonymise the data in the database to be
used in the test environment.

Tables and fields to be sanitised:
    - Submission
        - TF:
            - submitting_user_email
        - PF:
            - submitting_user_email
            - data_blob
                - sign_off_name
                - sign_off_role
    - RiskRegister
        - TF:
            - data_blob
                - consequences
                - full_desc
                - mitigations
                - pre_mitigated_impact
                - pre_mitigated_likelihood
                - post_mitigated_impact
                - post_mitigated_likelihood
                - proximity
                - risk_category
                - risk_name
                - risk_owner_role
                - short_desc
        - PF:
            - data_blob
                - mitigations
                - pre_mitigated_impact
                - pre_mitigated_likelihood
                - post_mitigated_impact
                - post_mitigated_likelihood
                - risk_category
                - risk_name
                - short_desc
"""


def sanitise_db():
    tf_submissions, pf_submissions = get_submissions()
    sanitise_submissions(qs=tf_submissions, fund_type="TF")
    sanitise_submissions(qs=pf_submissions, fund_type="PF")
    sanitise_risk_register(qs=tf_submissions, fund_type="TF")
    sanitise_risk_register(qs=pf_submissions, fund_type="PF")
    sanitise_place_details_towns_fund(qs=tf_submissions)
    # sanitise_place_details(qs=pf_submissions, fund_type='PF')
    # create_sql_dump()


def get_submissions():
    tf_submissions = Submission.query.filter(Submission.submission_id.like("S-R%")).all()
    pf_submissions = Submission.query.filter(Submission.submission_id.like("S-PF-R%")).all()

    return tf_submissions, pf_submissions


def sanitise_submissions(qs, fund_type):
    for submission in qs:
        # print(submission.submission_id)
        # print(submission.submission_date)
        sign_off = f.sign_off_name()
        submission.submitting_user_email = sign_off["email"]

        if fund_type == "PF":  # only PF submissions have data_blob
            submission.data_blob["sign_off_name"] = sign_off["name"]
            submission.data_blob["sign_off_role"] = f.sign_off_role()
            flag_modified(submission, "data_blob")

        db.session.commit()
        # print()


def sanitise_risk_register(qs, fund_type):
    for submission in qs:
        risk_registers = (
            db.session.query(RiskRegister)
            .join(ProgrammeJunction, ProgrammeJunction.id == RiskRegister.programme_junction_id)
            .filter(ProgrammeJunction.submission_id == submission.id)
            .all()
        )
        for item in risk_registers:
            item.data_blob["risk_name"] = f.risk_name()
            item.data_blob["short_desc"] = f.sentence(nb_words=7)
            item.data_blob["mitigations"] = f.risk_register()["mitigation"]
            item.data_blob["pre_mitigated_impact"] = f.impact()
            item.data_blob["pre_mitigated_likelihood"] = f.likelihood()
            item.data_blob["post_mitigated_impact"] = f.impact()
            item.data_blob["post_mitigated_likelihood"] = f.likelihood()
            item.data_blob["risk_category"] = f.risk_category()

            if fund_type == "TF":
                item.data_blob["consequences"] = f.sentence(nb_words=8)
                item.data_blob["full_desc"] = f.sentence(nb_words=12)
                item.data_blob["proximity"] = f.proximity()
                item.data_blob["risk_owner_role"] = f.risk_owner_role()

            db.session.commit()


def get_place_details(submission):
    place_details = (
        db.session.query(PlaceDetail)
        .join(ProgrammeJunction, ProgrammeJunction.id == PlaceDetail.programme_junction_id)
        .filter(ProgrammeJunction.submission_id == submission.id)
        .all()
    )
    return place_details


def sanitise_place_details_towns_fund(qs):
    contact_mapping = {
        "s151": f.sign_off_name(),
        "programme senior": f.sign_off_name(),
        "grant recipient's": f.sign_off_name(),
        "monitoring": f.sign_off_name(),
    }
    for submission in qs:
        place_details = get_place_details(submission)

        for item in place_details:
            for key, value in contact_mapping.items():
                if item.data_blob["question"].lower().startswith(key):
                    if item.data_blob["indicator"].lower() == "name":
                        item.data_blob["answer"] = value["name"]
                    elif item.data_blob["indicator"].lower() == "email":
                        item.data_blob["answer"] = value["email"]
                    elif item.data_blob["indicator"].lower() == "telephone":
                        item.data_blob["answer"] = f.phone_number()

            if item.data_blob["question"].startswith("Grant Recipient:"):
                if item.data_blob["answer"]:
                    item.data_blob["answer"] = shuffle_word(item.data_blob["answer"])
            flag_modified(item, "data_blob")
            db.session.commit()

            # print(item.data_blob["question"])
            # print(item.data_blob["indicator"])
            # print(item.data_blob["answer"])
            # print()

            # TODO: item.data_blob["question" == "Please select your place name"


def sanitise_place_details_pathfinder(qs):
    pass


def create_sql_dump():
    command = [
        "pg_dump",
        # '-U', 'username',
        # '-h', 'host',
        # '-p', 'port',
        "-d",
        "data_store",
        "-f",
        "dump.sql",
    ]
    subprocess.run(command, check=True)
