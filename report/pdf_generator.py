from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from report.form.form_structure import FormStructure


def create_pdf(report_form_structures: dict[str, FormStructure]):
    # Create a BytesIO buffer
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Styles for the document
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    section_style = styles["Heading1"]
    subsection_style = styles["Heading2"]
    page_style = styles["Heading3"]
    normal_style = styles["BodyText"]

    # Extract the data from the report form structures
    for project_name, report_form_structure in report_form_structures.items():
        # Title
        elements.append(Paragraph(f"Report: {project_name}", title_style))
        elements.append(Spacer(1, 12))

        for section in report_form_structure.sections:
            # Section Title
            elements.append(Paragraph(f"Section: {section.name}", section_style))
            elements.append(Spacer(1, 12))

            for subsection in section.subsections:
                # Subsection Title
                elements.append(Paragraph(f"Subsection: {subsection.name}", subsection_style))
                elements.append(Spacer(1, 12))

                for form in subsection.navigated_forms():
                    # Page Title
                    page_name = form["page_id"].replace("-", " ").capitalize()
                    elements.append(Paragraph(page_name, page_style))
                    elements.append(Spacer(1, 12))

                    # Form Data
                    form_data = form["form_data"]
                    for key, value in form_data.items():
                        question = key.replace("_", " ").capitalize()
                        answer = str(value).capitalize()
                        elements.append(Paragraph(f"{question}: {answer}", normal_style))
                        elements.append(Spacer(1, 12))

        elements.append(Spacer(1, 12))

    # Build the PDF
    doc.build(elements)

    # Reset buffer position to the beginning
    buffer.seek(0)
    return buffer
