# -*- encoding: UTF-8 -*-
#    Create:  rvolcan** 12/08/2016 **  **
#    type of the change:  New module
#    Comments: Creacion del modulo res_partner_display_name

{
    "name": "res_partner_name",
    'version' : '1.0',
    'author' : '',
    'website': '',
    'category' : 'Human Resources',
    'depends' : ["base"],
    "description": """
     Modulo para Contabilidad.\n
==============================================\n
Colaboracion: RVolcan \n
\n
     Muestra datos del modulo de Contabilidad.
    """,
    'data': ["view/res_partner_display_name_view.xml"],
    'installable': True,

}


