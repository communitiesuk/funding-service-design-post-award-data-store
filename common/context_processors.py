from flask import current_app, request


def inject_service_information() -> dict:
    subdomain = request.host.split(".")[0]

    if subdomain == current_app.config["FIND_SUBDOMAIN"]:
        service_name = current_app.config["FIND_SERVICE_NAME"]
        service_phase = current_app.config["FIND_SERVICE_PHASE"]
    elif subdomain == current_app.config["SUBMIT_SUBDOMAIN"]:
        service_name = current_app.config["SUBMIT_SERVICE_NAME"]
        service_phase = current_app.config["SUBMIT_SERVICE_PHASE"]
    else:
        return {}

    return dict(service_name=service_name, service_phase=service_phase)
