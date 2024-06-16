from flask import current_app, request


def inject_service_information() -> dict:
    host = request.host

    if host == current_app.config["FIND_DOMAIN"]:
        service_name = current_app.config["FIND_SERVICE_NAME"]
        service_phase = current_app.config["FIND_SERVICE_PHASE"]
    elif host == current_app.config["SUBMIT_DOMAIN"]:
        service_name = current_app.config["SUBMIT_SERVICE_NAME"]
        service_phase = current_app.config["SUBMIT_SERVICE_PHASE"]
    else:
        return {}

    return dict(service_name=service_name, service_phase=service_phase)
