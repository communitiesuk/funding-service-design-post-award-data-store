from report.submission_form_components.submission_form_page import SubmissionFormPage


class FormNavigator:
    @staticmethod
    def get_next_page_path(page: SubmissionFormPage, form_data: dict):
        if next_page := page.next_page:
            return next_page

        if next_page_conditions := page.next_page_conditions:
            for field, conditions in next_page_conditions.items():
                field_value = form_data.get(field)
                if field_value in conditions:
                    return conditions[field_value]

        return None
