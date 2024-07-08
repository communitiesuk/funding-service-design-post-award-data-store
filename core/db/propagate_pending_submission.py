from core.controllers import load_functions
from core.controllers.mappings import INGEST_MAPPINGS
from core.db import db
from core.db.entities import PendingSubmission
from core.db.queries import get_programme_by_id_and_round
from core.dto.programme import ProgrammeDTO
from core.transformation.pathfinders.pf_transform_r2 import transform as pf_r2_transform

TRANSFORM_FUNCTION_MAPPING = {
    "HS": {
        1: pf_r2_transform,
    },
}

LOAD_FUNCTION_MAPPING = {
    "HS": {
        "Submission_Ref": load_functions.load_submission_level_data,
        "Organisation_Ref": lambda *args, **kwargs: None,
        "Programme_Ref": lambda *args, **kwargs: None,
        "Programme Junction": load_functions.load_programme_junction,
        "Programme Progress": load_functions.load_submission_level_data,
        "Place Details": load_functions.load_submission_level_data,
        "Funding Questions": load_functions.load_submission_level_data,
        "Project Details": load_functions.load_submission_level_data,
        "Project Progress": load_functions.generic_load,
        "Funding": load_functions.load_submission_level_data,
        "Outputs_Ref": load_functions.load_outputs_outcomes_ref,
        "Output_Data": load_functions.load_submission_level_data,
        "Outcome_Ref": load_functions.load_outputs_outcomes_ref,
        "Outcome_Data": load_functions.load_submission_level_data,
        "RiskRegister": load_functions.load_submission_level_data,
        "ProjectFinanceChange": load_functions.load_submission_level_data,
    },
}


def propagate_pending_submission(programme_dto: ProgrammeDTO, reporting_round: int) -> None:
    pending_submission: PendingSubmission = PendingSubmission.query.filter_by(
        programme_id=programme_dto.id,
        reporting_round=reporting_round,
    ).one()
    fund = pending_submission.programme.fund
    programme = pending_submission.programme
    try:
        transform_function = TRANSFORM_FUNCTION_MAPPING[fund.fund_code][reporting_round]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported fund {fund.fund_name} and reporting round {reporting_round} combination."
        ) from exc
    transformed_data = transform_function(pending_submission)

    programme_exists_same_round = get_programme_by_id_and_round(programme.programme_id, reporting_round)
    submission_id, submission_to_del = load_functions.get_or_generate_submission_id(
        programme_exists_same_round, reporting_round, fund.fund_code
    )
    if submission_to_del:
        load_functions.delete_existing_submission(submission_to_del)
    load_mapping = LOAD_FUNCTION_MAPPING[fund.fund_code]
    for mapping in INGEST_MAPPINGS:
        if load_function := load_mapping.get(mapping.table):
            load_function(transformed_data, mapping, submission_id=submission_id, reporting_round=reporting_round)
    db.session.commit()
