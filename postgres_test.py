import procrastinate

from core.controllers.async_download import do_async_download

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(
        # pool_factory=psycopg_pool.AsyncNullConnectionPool,
        conninfo="postgresql://postgres:password@database:5432/data_store",
    )
)


@app.task(name="download")
def async_download(
    email_address: str,
    file_format: str,
    funds: list[str] | None = None,
    organisations: list[str] | None = None,
    regions: list[str] | None = None,
    rp_start: str | None = None,
    rp_end: str | None = None,
    outcome_categories: list[str] | None = None,
):
    """Download data, store file in S3 and send an email to the user with the download link."""

    query_params = {
        "email_address": email_address,
        "file_format": file_format,
        "funds": funds,
        "organisations": organisations,
        "regions": regions,
        "rp_start": rp_start,
        "rp_end": rp_end,
        "outcome_categories": outcome_categories,
    }

    do_async_download(**query_params)
