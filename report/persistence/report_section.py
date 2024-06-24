import dataclasses

from report.form.form_page import FormPage
from report.form.form_subsection import FormSubsection
from report.persistence.report_subsection import ReportSubsection


@dataclasses.dataclass
class ReportSection:
    name: str
    subsections: list[ReportSubsection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportSection":
        name = json_data["name"]
        subsections = [ReportSubsection.load_from_json(subsection_data) for subsection_data in json_data["subsections"]]
        return cls(name=name, subsections=subsections)

    def serialize(self) -> dict:
        return {"name": self.name, "subsections": [subsection.serialize() for subsection in self.subsections]}

    def subsection(self, form_subsection: FormSubsection) -> ReportSubsection:
        existing_subsection = next(
            (subsection for subsection in self.subsections if subsection.name == form_subsection.name), None
        )
        if not existing_subsection:
            new_subsection = ReportSubsection(name=form_subsection.name, pages=[])
            self.subsections.append(new_subsection)
            return new_subsection
        return existing_subsection

    def get_form_data(self, form_subsection: FormSubsection, form_page: FormPage, instance_number: int) -> dict:
        subsection = self.subsection(form_subsection)
        return subsection.get_form_data(form_page, instance_number)

    def set_form_data(
        self,
        form_subsection: FormSubsection,
        form_page: FormPage,
        instance_number: int,
        form_data: dict,
    ) -> None:
        subsection = self.subsection(form_subsection)
        subsection.set_form_data(form_page, instance_number, form_data)
