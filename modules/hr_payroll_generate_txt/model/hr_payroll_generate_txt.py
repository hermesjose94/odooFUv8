# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    Change:  **  20/07/2016 **  hr_payroll_generate_txt**  created
#    Comments: Generacion de archivo txt para el banco
#
# ##############################################################################################################################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64
from datetime import datetime
from openerp.exceptions import Warning

_DATETIME_FORMAT = "%Y-%m-%d"

class hr_payroll_generate_txt(osv.osv):
    _inherit = 'hr.payslip.run'

    _columns = {
        'txt_filename': fields.char('Nombre Archivo txt'),
        'txt_binary': fields.binary('Enlace archivo txt'),
        'bank_account_id':fields.many2one('res.partner.bank', 'Banco de Nomina', help="Payslip bank"),
    }

    def generate_txt(self, cr, uid, ids, context=None):
        """
        function called from button
        """
        txt_name = ''
        txt_extension = '.txt'
        content = ''
        res = {}
        warning_shown = {}
        msg_warning = ''
        config_obj = self.pool.get('hr.config_parameter')
        for ps in self.browse(cr, uid, ids):
            if ps.check_special_struct:
                if 'fideicomiso' in ps.struct_id.name.lower():
                    #TODO AGREGAR FUNCIONALIDAD PARA GENERAR EL ARCHIVO TXT DE FIDEICOMISO
                    pass
                elif 'ticket' in ps.struct_id.name.lower():
                    #TODO AGREGAR FUNCIONALIDAD PARA GENERAR EL ARCHIVO TXT DE CESTATICKETS
                    pass
                elif 'habitacional' in ps.struct_id.name.lower():
                    #TODO AGREGAR FUNCIONALIDAD PARA GENERAR EL ARCHIVO TXT DE BNAHAVI
                    pass
                elif config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.prestaciones',True) in ps.struct_id.code:
                    raise osv.except_osv(_('Advertencia!'),_(u'Este tipo de nómina no soporta archivo txt!!'))
                elif config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.utilidades',True) in ps.struct_id.code:
                    if not ps.bank_account_id.id:
                        raise osv.except_osv(_('Advertencia!'), _(
                            'Debe seleccionar una Institucion Financiera para poder generar el Archivo!!'))
                    b_txt = ps.bank_account_id
                    if 'PROVINCIAL' in ps.bank_account_id.bank.name.upper():
                        content = self.generate_detail_bbva_txt(cr, uid, ids, b_txt, False, context)
                        txt_name = 'TXT BBVA PROVINCIAL'
                    else:
                        # TODO AGREGAR FUNCIONALIDADES PARA GENERAR EL ARCHIVO TXT DE NOMINA PARA OTROS BANCOS
                        pass
                elif config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.vacaciones',True) in ps.struct_id.code:
                    if not ps.bank_account_id.id:
                        raise osv.except_osv(_('Advertencia!'), _(
                            'Debe seleccionar una Institucion Financiera para poder generar el Archivo!!'))
                    b_txt = ps.bank_account_id
                    if 'PROVINCIAL' in ps.bank_account_id.bank.name.upper():
                        content = self.generate_detail_bbva_txt(cr, uid, ids, b_txt, False, context)
                        txt_name = 'TXT BBVA PROVINCIAL'
                    else:
                        # TODO AGREGAR FUNCIONALIDADES PARA GENERAR EL ARCHIVO TXT DE NOMINA PARA OTROS BANCOS
                        pass
                else:
                    #TODO AGREGAR FUNCIONALIDAD PARA GENERAR EL ARCHIVO TXT DE VACACIONES, UTILIDADES, LIQUIDACIONES
                    pass
            else:
                if not ps.bank_account_id.id:
                    raise osv.except_osv(_('Advertencia!'),_('Debe seleccionar una Institucion Financiera para poder generar el Archivo!!'))
                b_txt = ps.bank_account_id
                if 'PROVINCIAL' in ps.bank_account_id.bank.name.upper():
                    content = self.generate_detail_bbva_txt(cr, uid, ids, b_txt, False, context)
                    txt_name = 'TXT BBVA PROVINCIAL'
                else:
                    #TODO AGREGAR FUNCIONALIDADES PARA GENERAR EL ARCHIVO TXT DE NOMINA PARA OTROS BANCOS
                    pass
        if not content['txt_str']:
            msg_warning = 'No se podido generar el archivo debido a que hay datos incompletos.\n'
        else:
            self.write(cr, uid, ids, {
                'txt_filename': txt_name + txt_extension,
                'txt_binary': base64.encodestring(content['txt_str'].encode('latin'))
            }, context=context)
            res.update({'txt_filename': txt_name + txt_extension})
            res.update({'txt_binary': base64.encodestring(content['txt_str'].encode('latin'))})

        if content['employees']== False:
            msg_warning = msg_warning + 'Los empleados; ' + ', '.join(content['employees']) + ', no tienen numero de cuenta,\n por lo tanto no se incluyeron en el archivo txt'
        else:
            msg_warning = msg_warning + 'No hay empleados en la nomina;'




        if msg_warning:
            warning_shown = {
                'title': ("Advertencia!!"),
                'message':(msg_warning)
            }
            #return {'warning': {'title': "Advertencia!", 'message': msg_warning}}
        return {'value':res, 'warning' : warning_shown}

        # Genera el contenido del archivo txt que sera enviado al banco BBVA Provincial
    def generate_detail_bbva_txt(self, cr, uid, ids, b_txt, special_struct, context=None):
        context = context or {}
        res = {}
        employees = []
        config_obj = self.pool.get('hr.config_parameter')
        code = [config_obj.hr_get_parameter(cr, uid,'hr.payroll.net.code', True)]  # para obtener el monto neto a pagar
        total_amount = 0.0
        txt_str = ''
        detalle_str = ''
        monto = 0.0
        local_bank_account_id = None
        local_account_type = None
        local_bank_account_number = None
        for i in self.browse(cr, uid, ids):
            for j in i.slip_ids:
                if special_struct:
                    #TODO LECTURA DE DATOS PARA TXT DE NOMINA ESPECIAL
                    #local_bank_account_id = j.employee_id.bank_account_id_other
                    #local_account_type = j.employee_id.account_type_other
                    #local_bank_account_number = j.employee_id.account_number_other
                    pass
                else:
                    local_bank_account_number = j.employee_id.account_number_2
                if b_txt == j.employee_id.bank_account_id_emp_2 and local_bank_account_number: #randara: si el banco es igual al seleccionado lo ingresa en el archivo
                    monto = self.get_amount(cr, uid, j.id, code)
                    total_amount += monto
                    detalle_str = detalle_str + ''.join([local_bank_account_number,self.fill_name_trail_blank(' ', 1),j.employee_id.nationality, \
                                  self.fill_nbr_lead_ceros(j.employee_id.identification_id_2, 10,False), self.fill_name_trail_blank(' ', 1), \
                                  self.fill_nbr_lead_ceros(monto, 15, True), self.fill_name_trail_blank(' ', 1), j.employee_id.lastname, \
                                  self.fill_name_trail_blank(' ', 1), j.employee_id.firstname,'\r\n'])
                else:
                    employees.append(j.employee_id.full_name)
            txt_str = txt_str + detalle_str
            res = {'employees':employees,'txt_str':txt_str}
            return res

    def fill_nbr_lead_ceros(self, cadena, longitud, es_monto):
        total_str = ''
        str_temp = ''
        rango = 0

        if cadena and cadena > 0:
            if es_monto:
                cadena *= 100
            str_temp = str(cadena).split('.')[0]

        if longitud > 0:
            rango = longitud - len(str_temp)

        for i in range(rango):
            total_str = total_str + '0'
        total_str = total_str + str_temp

        return total_str

    def fill_name_trail_blank(self, name, longitud):
        name_str = name
        for i in range(longitud - len(name)):
            name_str = name_str + ' '
        return name_str

    # este metodo se utiliza para obtener el monto para la generacion de los archivos txt y tambien para obtener el sueldo promedio
    # en unperiodo determindo
    # ejemplo de uso para sueldo promedio del mes: monto2 = self.get_amount(cr, uid, None,lista_de_codigos_de_concepto, employee_id, fecha_ini_mes,fecha_fin_mes,False)
    # ejemplo de uso para generacion de txt : monto = self.get_amount(cr, uid,payslip_id,lista_de_codigos_de_concepto)
    def get_amount(self, cr, uid, slip_id, code=None):
        amount = 0.0
        promedio = 0.0
        domain_cat = []
        domain_psl = []
        cat_ids = None
        if code:
            domain_cat.append(('code', 'in', code))
            cat_ids = self.pool.get('hr.salary.rule.category').search(cr, uid,domain_cat)
            domain_psl.append(('category_id', 'in', cat_ids))
        if slip_id:
            domain_psl.append(('slip_id', '=', slip_id))

        payslip_line_obj = self.pool.get('hr.payslip.line')
        payslip_line_ids = payslip_line_obj.search(cr, uid, domain_psl)
        payslip_line_net_obj = payslip_line_obj.browse(cr, uid, payslip_line_ids)

        if payslip_line_net_obj:
            for i in payslip_line_net_obj:
                amount = amount + i.amount
                promedio = amount

        return promedio

hr_payroll_generate_txt()
