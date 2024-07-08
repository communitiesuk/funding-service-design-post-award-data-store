import dataclasses

from core.db.entities import ProjectRef
from report.interfaces import Loadable, Serializable
from report.persistence.report_blob import ReportBlob


@dataclasses.dataclass
class SubmissionBlob(Loadable, Serializable):
    programme_report: ReportBlob
    project_reports: dict[str, ReportBlob]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "SubmissionBlob":
        programme_report = ReportBlob.load_from_json(json_data["programme_report"])
        project_reports = {
            project_id: ReportBlob.load_from_json(report_data)
            for project_id, report_data in json_data["project_reports"].items()
        }
        return cls(programme_report=programme_report, project_reports=project_reports)

    def serialize(self) -> dict:
        return {
            "programme_report": self.programme_report.serialize(),
            "project_reports": {
                project_id: project_report.serialize() for project_id, project_report in self.project_reports.items()
            },
        }

    def project_report(self, project: ProjectRef) -> ReportBlob:
        project_id = project.project_id
        existing_report = self.project_reports.get(project_id)
        if not existing_report:
            new_report = ReportBlob(name=project.project_name, sections=[])
            self.project_reports[project_id] = new_report
            return new_report
        return existing_report
