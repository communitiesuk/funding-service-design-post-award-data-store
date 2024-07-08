import dataclasses

from report.interfaces import Loadable, Serializable


@dataclasses.dataclass
class ReportPageBlob(Loadable, Serializable):
    page_id: str
    form_data: dict

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportPageBlob":
        page_id = json_data["page_id"]
        form_data = json_data["form_data"]
        return cls(page_id=page_id, form_data=form_data)

    def serialize(self) -> dict:
        return {"page_id": self.page_id, "form_data": self.form_data}
