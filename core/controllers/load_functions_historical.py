from core.db.entities import Programme, ProgrammeJunction, Submission


def get_programmes_same_round_or_older(reporting_round: int, programme_ids: list[str]) -> dict[str, str]:
    """Return ids of programmes updated in any round up to and including the specified round.

    :param reporting_round: The round currently being ingested.
    :param programme_ids: The programme ids of the data being ingested.
    :return: list of programme ids
    """

    existing_programmes = (
        Programme.query.join(ProgrammeJunction)
        .join(Submission)
        .filter(Programme.programme_id.in_(programme_ids))
        .filter(Submission.reporting_round <= reporting_round)
        .all()
    )

    existing_programme_ids = {programme.programme_id: programme.id for programme in existing_programmes}

    return existing_programme_ids


def get_programmes_newer_round(reporting_round: int, programme_ids: list[str]) -> list[str]:
    """Return ids of programmes updated in any round after the specified round.

    :param reporting_round: The round currently being ingested.
    :param programme_ids: The programme ids of the data being ingested.
    :return: list of programme ids
    """
    programmes_newer_round = (
        Programme.query.join(ProgrammeJunction)
        .join(Submission)
        .filter(Programme.programme_id.in_(programme_ids))
        .filter(Submission.reporting_round >= reporting_round)
        .with_entities(Programme.programme_id)
        .all()
    )

    programme_ids_newer_round = [programme.programme_id for programme in programmes_newer_round]

    return programme_ids_newer_round
