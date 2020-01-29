# -*- encoding: UTF-8 -*-
#    Create:  ** 30/07/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_payroll_generate_txt

{
    'name': 'HR Generate txt',
    'description': u'''\
Agrega funcionalidades para la generación de archivo txt
============================

V1.1.1.\n
funcionalidades para la generación del archivo txt de la nómina que debe ser enviado al banco.\n

''',
    'author': '',
    'category': 'Human Resources',
    'data': [
        'views/hr_payroll_generate_txt_view.xml',
        ],
    'depends': ['hr_payroll'],
    'installable': True,
}