import contextlib
import inspect

import pytest
from _pytest.fixtures import FixtureRequest
from flask import url_for
from sqlalchemy.exc import DataError


class TestAdminModelsAuthorization:
    models = (
        "fund",
        "geospatialdim",
        "organisation",
        "outcomedim",
        "outputdim",
        "submission",
        "reportinground",
        "projectprogress",
    )

    def test_all_models_captured(self, find_test_client):
        from admin import entities

        admin_module_classes = [
            obj
            for _, obj in inspect.getmembers(entities)
            if inspect.isclass(obj) and issubclass(obj, entities.BaseAdminView) and obj is not entities.BaseAdminView
        ]
        assert len(admin_module_classes) == len(self.models), (
            "If this test is failing and you've added a new admin model, "
            "then increase this number and make sure it's appropriately tested below."
        )

    @pytest.mark.parametrize("has_admin_role", [True, False])
    @pytest.mark.parametrize("admin_view_name", models)
    def test_get(self, request: FixtureRequest, seeded_test_client, has_admin_role: bool, admin_view_name: str):
        client = request.getfixturevalue("admin_test_client" if has_admin_role else "find_test_client")

        with client.application.app_context():
            response = client.get(f"/admin/{admin_view_name}/")
            if has_admin_role:
                assert response.status_code == 200
            else:
                assert response.status_code == 302
                assert response.location.startswith("http://authenticator.communities.gov.localhost:4004/")

    @pytest.mark.parametrize("has_admin_role", [True, False])
    @pytest.mark.parametrize("admin_view_name", models)
    def test_create_new_instance(
        self, request: FixtureRequest, seeded_test_client, has_admin_role: bool, admin_view_name: str
    ):
        client = request.getfixturevalue("admin_test_client" if has_admin_role else "find_test_client")

        CAN_CREATE_MODELS = ["reportinground"]

        with client.application.app_context():
            response = client.post(f"/admin/{admin_view_name}/new/")

            if has_admin_role:
                if admin_view_name in CAN_CREATE_MODELS:
                    assert response.status_code == 200

                else:
                    assert response.status_code == 302
                    assert response.location == f"/admin/{admin_view_name}/"

            else:
                assert response.status_code == 302
                assert response.location.startswith("http://authenticator.communities.gov.localhost:4004/")

    @pytest.mark.parametrize("has_admin_role", [True, False])
    @pytest.mark.parametrize("admin_view_name", models)
    def test_edit_instances(
        self, request: FixtureRequest, seeded_test_client, has_admin_role: bool, admin_view_name: str
    ):
        client = request.getfixturevalue("admin_test_client" if has_admin_role else "find_test_client")

        CAN_EDIT_MODELS: list[str] = ["organisation"]

        with client.application.app_context():
            # Bit of a hack - we pass a non-uuid ID through. This only gets checked if all of the authorization checks
            # pass and the view is actually enabled for edits, so we use this to short-circuit having to find a
            # valid instance in the DB to hook up.
            should_be_able_to_edit = admin_view_name in CAN_EDIT_MODELS and has_admin_role
            ignore_id_error = pytest.raises(DataError) if should_be_able_to_edit else contextlib.nullcontext()

            with ignore_id_error:
                response = client.post(f"/admin/{admin_view_name}/edit/?id=invalid-oh-no")

                if has_admin_role:
                    assert response.status_code == 302
                    assert response.location == f"/admin/{admin_view_name}/"

                else:
                    assert response.status_code == 302
                    assert response.location.startswith("http://authenticator.communities.gov.localhost:4004/")

            if should_be_able_to_edit:
                # We expect this error if the view was accessed "successfully" (ie user has admin group and the entity
                # is configured to allow edits
                excinfo = ignore_id_error.excinfo  # type: ignore[union-attr]
                assert "invalid input syntax for type uuid" in str(excinfo), (
                    "Looks like the test thinks you can edit the model, but you actually can't"
                )

    @pytest.mark.parametrize("has_admin_role", [True, False])
    @pytest.mark.parametrize("admin_view_name", models)
    def test_delete_instances(
        self, request: FixtureRequest, seeded_test_client, has_admin_role: bool, admin_view_name: str
    ):
        client = request.getfixturevalue("admin_test_client" if has_admin_role else "find_test_client")

        CAN_DELETE_MODELS: list[str] = []

        with client.application.app_context():
            # Bit of a hack - we pass a non-uuid ID through. This only gets checked if all of the authorization checks
            # pass and the view is actually enabled for edits, so we use this to short-circuit having to find a
            # valid instance in the DB to hook up.
            should_be_able_to_delete = admin_view_name in CAN_DELETE_MODELS and has_admin_role
            ignore_id_error = pytest.raises(Exception) if should_be_able_to_delete else contextlib.nullcontext()

            response = client.post(f"/admin/{admin_view_name}/delete/", json={"id": "invalid-oh-no"})

            if has_admin_role:
                assert response.status_code == 302
                assert response.location == f"/admin/{admin_view_name}/"

            else:
                assert response.status_code == 302
                assert response.location.startswith("http://authenticator.communities.gov.localhost:4004/")

            if should_be_able_to_delete:
                # We expect this error if the view was accessed "successfully" (ie user has admin group and the entity
                # is configured to allow edits
                excinfo = ignore_id_error.excinfo  # type: ignore[union-attr]
                assert "invalid input syntax for type uuid" in str(excinfo), (
                    "Looks like the test thinks you can delete the model, but you actually can't"
                )


class TestAdminActionsAuthorization:
    actions = (
        "reingest_s3",
        "reingest_file",
        "retrieve_submission",
        "retrieve_failed_submission",
    )

    def test_all_actions_captured(self, find_test_client):
        from admin import actions

        admin_module_classes = [
            obj
            for _, obj in inspect.getmembers(actions)
            if inspect.isclass(obj) and issubclass(obj, actions.BaseAdminView) and obj is not actions.BaseAdminView
        ]
        assert len(admin_module_classes) == len(self.actions), (
            "If this test is failing and you've added a new admin action, "
            "then increase this number and make sure it's appropriately tested below."
        )

    @pytest.mark.parametrize("has_admin_role", [True, False])
    @pytest.mark.parametrize("admin_view_name", actions)
    def test_get_authorization(
        self, request: FixtureRequest, seeded_test_client, has_admin_role: bool, admin_view_name: str
    ):
        client = request.getfixturevalue("admin_test_client" if has_admin_role else "find_test_client")

        with client.application.app_context():
            response = client.get(f"/admin/{admin_view_name}/")
            if has_admin_role:
                assert response.status_code == 200
            else:
                assert response.status_code == 302
                assert response.location.startswith("http://authenticator.communities.gov.localhost:4004/")

    @pytest.mark.parametrize("has_admin_role", [True, False])
    @pytest.mark.parametrize("admin_view_name", actions)
    def test_post_authorization(self, request, has_admin_role, seeded_test_client, admin_view_name):
        client = request.getfixturevalue("admin_test_client" if has_admin_role else "find_test_client")

        with client.application.test_request_context():
            reingest_url = url_for(f"{admin_view_name}.index")

        response = client.post(reingest_url)

        if has_admin_role:
            assert response.status_code == 200  # request authorized (but will be in form error state)
        else:
            assert response.status_code == 302
            assert response.location.startswith("http://authenticator.communities.gov.localhost:4004/")
