import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from report.form.form_page import FormPage

from report.interfaces import Loadable, Serializable
from report.persistence.report_page import ReportPage


@dataclasses.dataclass
class ReportSubsection(Loadable, Serializable):
    name: str
    pages: list[ReportPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportSubsection":
        name = json_data["name"]
        pages = [ReportPage.load_from_json(page_data) for page_data in json_data["pages"]]
        return cls(name=name, pages=pages)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "pages": [page.serialize() for page in self.pages],
        }

    def get_form_data(self, form_page: "FormPage", instance_number: int) -> dict:
        matched_pages = [page for page in self.pages if page.page_id == form_page.page_id]
        if instance_number >= len(matched_pages):
            return {}
        return matched_pages[instance_number].form_data

    def set_form_data(self, form_page: "FormPage", instance_number: int, form_data: dict) -> None:
        matched_pages = [page for page in self.pages if page.page_id == form_page.page_id]
        if instance_number >= len(matched_pages):
            new_page = ReportPage(page_id=form_page.page_id, form_data=form_data)
            self.pages.append(new_page)
            return
        existing_page = matched_pages[instance_number]
        existing_page.form_data = form_data
