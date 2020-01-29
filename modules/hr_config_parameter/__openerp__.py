# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 21/04/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_config_parameter

{

    'name': 'Config Parameters',
    'description': '''\
Permite gestionar parámetros para el módulo de nóminas
============================

V1.1.0\r\n
Permite gestionar parámetros para el módulo de nóminas\r\n
''',
    'author': '',
    'category': 'Human Resources',
    'data': [
        'views/hr_config_parameter_view.xml',
        ],
    'depends': ['base', 'hr_payroll'],
    'installable': True,
}