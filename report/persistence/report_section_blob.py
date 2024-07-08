import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from report.form.form_page import FormPage
    from report.form.form_subsection import FormSubsection

from report.interfaces import Loadable, Serializable
from report.persistence.report_subsection_blob import ReportSubsectionBlob


@dataclasses.dataclass
class ReportSectionBlob(Loadable, Serializable):
    name: str
    subsections: list[ReportSubsectionBlob]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportSectionBlob":
        name = json_data["name"]
        subsections = [
            ReportSubsectionBlob.load_from_json(subsection_data) for subsection_data in json_data["subsections"]
        ]
        return cls(name=name, subsections=subsections)

    def serialize(self) -> dict:
        return {"name": self.name, "subsections": [subsection.serialize() for subsection in self.subsections]}

    def subsection(self, form_subsection: "FormSubsection") -> ReportSubsectionBlob:
        existing_subsection = next(
            (subsection for subsection in self.subsections if subsection.name == form_subsection.name), None
        )
        if not existing_subsection:
            new_subsection = ReportSubsectionBlob(name=form_subsection.name, pages=[])
            self.subsections.append(new_subsection)
            return new_subsection
        return existing_subsection

    def get_form_data(self, form_subsection: "FormSubsection", form_page: "FormPage", instance_number: int) -> dict:
        subsection = self.subsection(form_subsection)
        return subsection.get_form_data(form_page, instance_number)

    def set_form_data(
        self,
        form_subsection: "FormSubsection",
        form_page: "FormPage",
        instance_number: int,
        form_data: dict,
    ) -> None:
        subsection = self.subsection(form_subsection)
        subsection.set_form_data(form_page, instance_number, form_data)
