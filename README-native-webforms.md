# How to add a new native webform:

At the moment I've only built out project-level report pages, not programme-level. Bear in mind that all of the instructions below are aimed at adding project pages and aren't generalised for programmes yet. I'd expect some changes, albeit not huge ones.
## Adding a single page
- Look in `report/fund_reporting_structures.py` at `submission_structure` and find the section+subsection you want to add a question/page to.
- Create the FlaskForm instance for the question(s) you want to ask on a single page in `report/forms.py`, subclassed from ReportForm.
- Create a template to render the form in `report/templates/<section>/<subsection>/<page-name>.py`, extending from `report/form_base.html`.
- Insert a `SubmissionPage` instance in the specific subsection's `pages` attribute in `report/fund_reporting_structures.py:submission_structure`.
- Done

## Adding a subsection (an entry in a section's tasklist)
- Look in `report/fund_reporting_structures.py` and find the section you want to add a new subsection to.
- Create the FlaskForm instances for the questions/pages you want to add in `report/forms.py`, subclassed from `ReportForm`.
- Create a new directory in `report/templates/<section>`; choose a hyphenated directory name that will match the subsection's URL slug/path_fragment.
- Add templates to that subsection template directory for each form/page you've created.
- Create a `SubmissionSubsection` instance in the specific section's `pages` attribute` in `report/fund_reporting_structures.py:submission_structure`.

## Adding a new section (a full tasklist)
- Follow the same structure/pattern as for a subsection...

-----------------------

# native webforms spike thoughts

## pros / nice stuff
- govuk-frontend-jinja+govuk-frontend-wtf make it easy to build forms that are gov.uk design system styled
- the FormSubmissionStructure (name TBC) thing makes it quite clear what sections/subsections/pages/forms 'make up' a submission, and you could imagine this being programmatically generated on a per-fund basis fairly easily. So would be easy to enable/disable sections for a given fund, while still reusing sections/subsections/forms to keep questions/data collection consistent
- we can have a template for every page/form we want to display, meaning we can make it look exactly how we want it to look, which still reusing base templates from the app for consistency.

## neutral / could go either way
- this spike is built on the monolith ... 🙃
- I started off building the pages as fully separate views. This quickly felt like it would be hard to keep form/data collection consistent. Adding a single page that handles form/page generation from a described structure (FormSubmissionStructure) gives us high consistency and much less code to maintain, but may limit per-page flexibility somewhat.
- i have some questions now over how accessible form builder pages are - is text associated with form fields nicely? **can** it all be linked up nicely?
- I haven't built out a strict conditional page (ie answer 'yes' on page 1 leads to page 2, 'no' on page 1 leads to page 3). But have been able to use GOV.UK Design System conditional-revealing on the same page (ie click 'yes' on page1 instantly reveals another textbox on the page to fill in).

## cons / tricky stuff
- had to build out a 'circular'/'recursive' form flow for adding multiple of the same thing (eg project challenges)
- collecting+merging data was slightly tricky and the spike implementation is probably hacky
- some of what i've ended up doing felt harder than it would've been with form builder - obviously.
- a lot of other stuff probably - i started writing this late in the process
