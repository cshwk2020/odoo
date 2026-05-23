{
    "name": "HR Expense Autofill",
    "version": "1.0",
    "depends": ["hr_expense", "queue_job"],
    'category': 'Human Resources/Expenses Autofill',
    'sequence': 3,
    "data": [
        "security/ir.model.access.csv",
        "views/hr_expense_autofill_views.xml",
        "wizards/receipt_upload_wizard.xml",
    ],

    "assets": {
        "web.assets_backend": [
            "hr_expense_autofill/static/src/js/notification_listener.js",
        ],
    },


    "installable": True,
    "application": True,
}
