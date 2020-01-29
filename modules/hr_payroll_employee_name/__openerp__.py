# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 29/07/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_payroll_employee_name

{
    'name': 'HR Employee Name',
    'description': u'''\
Agrega 2 nombre y 2 apellidos al empleado.
============================

V1.1.1.\r\n
Permite agregar los 2 nombre y los 2 apellidos del empleado de forma separada
''',
    'author': '',
    'category': 'Human Resources',
    'data': [
        'views/hr_payroll_employee_name_view.xml',
        ],
    'depends': ['hr'],
    'installable': True,
}