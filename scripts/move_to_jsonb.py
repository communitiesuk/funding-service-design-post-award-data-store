from core import db
from core.db.entities import Funding

funding_rows = Funding.query.all()
jsonb = {}
for row in funding_rows:
    jsonb["start_date"] = str(row.start_date)
    jsonb["end_date"] = str(row.end_date)
    jsonb["funding_source_name"] = row.funding_source_name
    jsonb["funding_source_type"] = row.funding_source_type
    jsonb["secured"] = row.secured
    jsonb["spend_for_reporting_period"] = float(row.spend_for_reporting_period)
    jsonb["status"] = row.status
    row.json_blob = jsonb
db.session.commit()
