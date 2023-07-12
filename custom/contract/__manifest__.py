# -*- coding: utf-8 -*-
{
    'name': "contract",

    'summary': """
        extends employee contracts""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_holidays','hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/contract_form_extend.xml',
        'views/job_form_extend.xml',
        'data/email_template.xml',
        'data/cron.xml',
        'data/hr_holiday_data.xml'
    ],
    # only loaded in demonstration mode
   
}
