# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class human_resources_configuration(osv.osv_memory):
    _inherit = 'hr.config.settings'
    _columns = {
        'module_hr_utilidades_add_calculo': fields.boolean('Salario a base de calculo',
                                                           help="""Verdadero: obtener el salario promedio durante el periodo seleccionado.\n"
                                                                 "Falso: obtener el salario del mes anterior."""),
        'module_hr_utilidades_add_date_start': fields.date('Inicio periodo de calculo',
                                                           help="Fecha de inicio del periodo para calcular el salario promediio"),
        'module_hr_utilidades_add_date_end': fields.date('Fin periodo de calculo',
                                                         help="Fecha de finalizacion del periodo para calcular el salario promediio"),
    }

    def get_config_values(self, cr):
        res = {}
        cr.execute("""select
	                    module_hr_utilidades_add_calculo,
	                    module_hr_utilidades_add_date_start,
	                    module_hr_utilidades_add_date_end
                      from hr_config_settings ORDER BY write_date desc LIMIT 1""")
        res = cr.dictfetchall()
        return res