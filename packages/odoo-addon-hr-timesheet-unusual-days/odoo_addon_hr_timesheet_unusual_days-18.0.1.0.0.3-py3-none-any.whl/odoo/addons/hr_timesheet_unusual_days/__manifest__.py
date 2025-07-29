# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Timesheet Calendar Unusual Days",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "glueckkanja AG, Odoo Community Association (OCA)",
    "maintainers": ["CRogos"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "hr_holidays",
        "hr_timesheet_calendar",
    ],
    "data": [
        "views/hr_timesheet_views.xml",
    ],
}
