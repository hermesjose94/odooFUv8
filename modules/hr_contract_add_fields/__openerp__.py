# -*- encoding: UTF-8 -*-
#    Create:  jeeduardo** 23/07/2016 **  **
#    type of the change:  Creacion
#    Comments: Creacion del modulo de hr_contract_add_fields

{
    'name': 'Contract Aditional data',
    'description': '''\
Adds aditional fields to hr_contract module
============================

V1.1.1.
Agrega los siguientes campos adicionales al contrato de los empleados:\n
    * Bono Nocturno\n
    * Dias de Sueldo Pendiente\n
    * Feriados\n
    * Feriados no Laborados\n
    * Horas extraordinarias Diurnas\n
    * Retroactivo de Sueldo\n
    * Aporte Patronal F.A.O.V.\n
    * Aporte Patronal  Fondo de Ahorro\n
    * Aporte Patronal P.I.E.\n
    * Aporte Patronal S.O.S.\n
    * Fondo de Caja de Ahorro\n
    * Horas no Laboradas\n
    * Inasistencias Injustificadas\n
    * Permiso no Remunerados Dias\n
    * Permiso no Remunerados Horas\n
    * Retenciones  F.A.O.V.\n
    * Retenciones Fondo de Ahorro\n
    * Retenciones I.S.L.R.\n
    * Retenciones P.I.E.\n
    * Retenciones  S.O.S.\n
''',
    'author': '',
    'category': 'Human Resources',
    'data': [
        'views/hr_contract_add_fields_view.xml',
        ],
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll'],
    'installable': True,
}