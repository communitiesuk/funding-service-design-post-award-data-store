import dataclasses

from core.db.entities import ProjectRef
from report.persistence.report import Report


@dataclasses.dataclass
class Submission:
    programme_report: Report
    project_reports: list[Report]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "Submission":
        programme_report = Report.load_from_json(json_data["programme_report"])
        project_reports = [Report.load_from_json(report_data) for report_data in json_data["project_reports"]]
        return cls(programme_report=programme_report, project_reports=project_reports)

    def serialize(self) -> dict:
        return {
            "programme_report": self.programme_report.serialize(),
            "project_reports": [report.serialize() for report in self.project_reports],
        }

    def project_report(self, project: ProjectRef) -> Report:
        project_name = project.project_name
        existing_report = next((report for report in self.project_reports if report.name == project_name), None)
        if not existing_report:
            new_report = Report(name=project_name, sections=[])
            self.project_reports.append(new_report)
            return new_report
        return existing_report
