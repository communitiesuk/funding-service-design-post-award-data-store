import logging
from enum import Enum

import pytest
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage, MultiDict

from admin.entities import OrganisationAdminView
from data_store.const import EXCEL_MIMETYPE, OrganisationTypeEnum
from data_store.controllers.ingest import ingest
from data_store.db import db
from data_store.db.entities import Organisation, Submission


class TestReingestS3AdminView:
    # TODO: add some tests
    ...


class TestReingestFileAdminView:
    # NOTE[RESP_CLOSE]
    # Flask's test client sometimes does not close large files passed to it correctly, so we force them to close
    # here. Not doing this manually can make pytest throw a ResourceWarning, which gets flagged as an error.
    # See also:
    #    https://github.com/pallets/werkzeug/issues/1785
    #    https://github.com/pallets/werkzeug/pull/2041

    def test_success(
        self,
        test_client_reset,
        towns_fund_round_3_success_file_path,
        test_buckets,
        mock_sentry_metrics,
        admin_test_client,
        caplog,
    ):
        with open(towns_fund_round_3_success_file_path, "rb") as tf_r3:
            ingest(
                fund_name="Towns Fund",
                reporting_round=3,
                do_load=True,
                excel_file=FileStorage(tf_r3, content_type=EXCEL_MIMETYPE),
            )
        original_id, submitted_at_before = (
            Submission.query.with_entities(Submission.id, Submission.submission_date)
            .order_by(desc(Submission.submission_date))
            .first()
        )

        with open(towns_fund_round_3_success_file_path, "rb") as tf_r3:
            with caplog.at_level(logging.WARNING):
                resp = admin_test_client.post(
                    "/admin/reingest_file/",
                    data={
                        "submission_id": "s-r03-1",  # also sneakily testing case-insensitivity
                        "excel_file": FileStorage(tf_r3, content_type=EXCEL_MIMETYPE),
                    },
                    follow_redirects=True,
                )
        assert resp.status_code == 200

        new_id, submitted_at_after = (
            Submission.query.with_entities(Submission.id, Submission.submission_date)
            .order_by(desc(Submission.submission_date))
            .first()
        )
        assert submitted_at_before < submitted_at_after  # NS precision so shouldn't need to freeze time

        assert caplog.messages == [
            (
                f"Submission ID S-R03-1 (original db id={original_id}, new db id={new_id}) "
                f"reingested by admin@communities.gov.uk from a local file"
            )
        ]

        resp.close()  # See note `RESP_CLOSE` near top of class

    def test_no_matching_submission(
        self,
        test_client_reset,
        towns_fund_round_3_success_file_path,
        test_buckets,
        mock_sentry_metrics,
        admin_test_client,
    ):
        with open(towns_fund_round_3_success_file_path, "rb") as tf_r3:
            resp = admin_test_client.post(
                "/admin/reingest_file/",
                data={
                    "submission_id": "S-R03-999",
                    "excel_file": FileStorage(tf_r3, content_type=EXCEL_MIMETYPE),
                },
                follow_redirects=True,
            )

            resp.close()  # See note `RESP_CLOSE` near top of class

        assert resp.status_code == 200
        assert "Could not find a matching submission with ID S-R03-999" in resp.text


class TestRetrieveSubmissionAdminView:
    # TODO: add some tests
    ...


class TestRetrieveFailedSubmissionAdminView:
    # TODO: add some tests
    ...


class ExtendedOrganisationTypeEnum(str, Enum):
    LOCAL_AUTHORITY = OrganisationTypeEnum.LOCAL_AUTHORITY.value
    NEW_VALUE = "New Value"


def test_organisationadmin_edit_allowed(test_client_reset, admin_test_client, test_organisation):
    organisation = test_organisation
    form_data = {
        "external_reference_code": "New Code",
    }

    with admin_test_client.application.app_context():
        response = admin_test_client.post(
            f"/admin/organisation/edit/?id={organisation.id}", data=form_data, follow_redirects=True
        )

        assert response.status_code == 200
        edited_instance = Organisation.query.filter_by(id=organisation.id).first()

        # Allowed field should be updated to new value
        assert edited_instance.external_reference_code == "New Code"
        # All other fields should remain the same
        assert edited_instance.organisation_name == "Original Name"
        assert edited_instance.organisation_type == OrganisationTypeEnum.LOCAL_AUTHORITY


def test_organisationadmin_edit_disallowed(test_client_reset, admin_test_client, test_organisation):
    organisation = test_organisation
    form_data = {
        "organisation_name": "New Name",
        "external_reference_code": "New Code",
        "organisation_type": ExtendedOrganisationTypeEnum.NEW_VALUE.value,
    }
    with admin_test_client.application.app_context():
        response = admin_test_client.post(
            f"/admin/organisation/edit/?id={organisation.id}", data=form_data, follow_redirects=True
        )

        assert response.status_code == 200
        edited_instance = Organisation.query.filter_by(id=organisation.id).first()

        # Allowed field should be updated to new value, all other fields sent in the form
        # are removed from the form data before being processed by Flask-Admin and should not be updated
        assert edited_instance.external_reference_code == "New Code"
        assert edited_instance.organisation_name == "Original Name"
        assert edited_instance.organisation_type == OrganisationTypeEnum.LOCAL_AUTHORITY


def test_organisationadmin_on_model_change(test_client_reset, admin_test_client, test_organisation):
    organisation = test_organisation
    view = OrganisationAdminView(db.session)

    # Do not exclude organisation_name in this case to test the view's "on_model_change" method
    # to test preventing model update, imitating editing the html manually to include the organisation_name field
    # in the form. If the organisation_name field was included in the form_excluded_columns, Flask-Admin would
    # remove it from the form, and that's not we want to test here.
    view.form_excluded_columns = [
        "programmes",
        "organisation_type",
    ]
    form_data = {
        "organisation_name": "New Name",
        "external_reference_code": "New Code",
        "organisation_type": ExtendedOrganisationTypeEnum.NEW_VALUE.value,
    }
    form: MultiDict = MultiDict()
    form.data = form_data

    with pytest.raises(ValueError, match=r"^organisation_name field can't be updated\.$"):
        view.on_model_change(form=form, model=organisation, is_created=False)

    instance_attempted_to_edit = Organisation.query.filter_by(id=organisation.id).first()
    # No fields should be updated
    assert instance_attempted_to_edit.organisation_name == "Original Name"
    assert instance_attempted_to_edit.external_reference_code == "Original Code"
    assert instance_attempted_to_edit.organisation_type == OrganisationTypeEnum.LOCAL_AUTHORITY
