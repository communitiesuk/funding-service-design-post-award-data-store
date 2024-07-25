from flask import current_app, request, url_for


def inject_service_information() -> dict:
    host = request.host

    if host == current_app.config["FIND_HOST"]:
        service_name = current_app.config["FIND_SERVICE_NAME"]
        service_phase = current_app.config["FIND_SERVICE_PHASE"]
        service_url = url_for("find.download")
    elif host == current_app.config["SUBMIT_HOST"]:
        service_name = current_app.config["SUBMIT_SERVICE_NAME"]
        service_phase = current_app.config["SUBMIT_SERVICE_PHASE"]
        service_url = url_for("submit.dashboard")
    else:
        return {}

    return dict(service_name=service_name, service_phase=service_phase, service_url=service_url)
