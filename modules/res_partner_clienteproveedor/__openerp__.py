# -*- coding: UTF-8 -*-

{
    "name": "res_partner_clienteproveedor",
    "version": "1.0",
    "author": "",
    'depends' : ["hr","base"],
    "data": [
        'wizard/add_contacts_view.xml',
        'view/res_partner_view.xml',
             ],
    'category': 'Purchase Management',
    "description": """
    Modifica la clase res_partner agregando funcionalidad
    """,
    'installable': True,
}