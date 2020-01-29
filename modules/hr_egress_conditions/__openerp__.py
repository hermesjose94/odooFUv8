# -*- encoding: UTF-8 -*-
#    Create:  rvolcan** 25/07/2016 **  **
#    type of the change:  New module
#    Comments: Creacion del modulo de hr_egress_conditions

{
    'name' : 'Motivos de Egreso',
    'version' : '1.0',
    'author' : '',
    'website': '',
    'category' : 'Human Resources',
    'depends': ["hr_contract", "hr", "base" ],
    'description': """

Modulo para Motivos de Egreso.\n
==============================================\n
Colaboracion: RVolcan\n
\n
Este Modulo crea la funcionalidad de motivos de Egreso de los empleados\n
    - Fecha de Egreso\n
    - Motivo de Egreso\n
    """,
    'data' :[
        'views/hr_egress_conditions.xml'
    ]
}
