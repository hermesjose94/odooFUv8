
# -*- encoding: UTF-8 -*-
#    Create:  randara** 19/07/2016 **  **
#    type of the change:  New module
#    Comments: Creacion del modulo de hr_special_splip


{
    'name' : 'Datos de RRHH',
    'version' : '1.0',
    'author' : '',
    'website': '',
    'category' : 'Human Resources',
    'depends': [ "hr", "base" ],
    'description': u"""

Agrega la pestaña Datos RRHH a la ficha del empleado.\n
==============================================\n
Colaboración: RVolcan\n
\n
Agrega la pestaña Datos RRHH a la ficha del empleado, con los siguientes campos.\n
    * Información Adicional
        * Fecha de Ingreso
        * Fecha de Egreso
        * Motivo de Egreso
    * Antigüedad
        * Días
        * Meses
        * Años
    * Información Bancaria
        * Institución Financiera
        * Nro. de Cuenta
        * Tipo de Cuenta
    """,
    'data': [ "views/hr_datos_rrhh_view.xml"],
    'installable': True,
    'auto_install': True,

}