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
#    Change: jeduardo **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################

from openerp import fields, models, api
from openerp.exceptions import Warning
# from openerp.osv import fields, osv
import re

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = "hr.contract"


    #ASIGNACIONES
    bono_nocturno_check = fields.Boolean('Bono Nocturno')
    bono_nocturno_value = fields.Char('Bono Nocturno Valor', size=5, help="Acepta valores entre 00:00 y 23:59")
    bono_nocturno = fields.Float('Bono Nocturno',digits=(10,2))
    dias_sueldo_pend_check = fields.Boolean('Dias de Pueldo Pendiente')
    dias_sueldo_pend_value = fields.Integer('Dias de Pueldo Pendiente Valor', size=2)
    feriados_check = fields.Boolean('Feriados')
    feriados_value = fields.Integer('Feriados Valor', size=2)
    feriados_no_lab_check = fields.Boolean('Feriado no Laborado')
    feriados_no_lab_value = fields.Integer('Feriado no Laborado Valor', size=2)
    hrs_extra_diurno_check = fields.Boolean('Horas Extraordinarias Diurnas')
    hrs_extra_diurno_value = fields.Char('Horas Extraordinarias Diurnas Valor', size=5, help="Acepta valores entre 00:00 y 23:59")
    hrs_extra_diurno = fields.Float('Horas Extraordinarias Diurnas',digits=(10,2))
    retro_sueldo_check = fields.Boolean('Retroactivo de Sueldo')
    retro_sueldo_value = fields.Float('Retroactivo de Sueldo Valor', digits=(10,2))
    asignacion_salarial_check = fields.Boolean('Asignacion Salarial check')
    asignacion_salarial_value = fields.Float('Asignacion Salarial value', digits=(10,2))
    asignacion_no_salarial_check = fields.Boolean('Asignacion no Salarial check')
    asignacion_no_salarial_value = fields.Float('Asignacion no Salarial value', digits=(10,2))
    # DEDUCCIONES
    hrs_no_lab_check = fields.Boolean('Horas no Laboradas')
    hrs_no_lab_value = fields.Char('Horas no Laboradas Valor', size=5, help="Acepta valores entre 00:00 y 23:59")
    hrs_no_lab = fields.Float('Horas No laboradas', digits=(10, 2))
    inasistencia_injustificada_check = fields.Boolean('Inasistencia Injustufucada')
    inasistencia_injustificada_value = fields.Char('Inasistencia Injustufucada Valor', size=5, help="Acepta valores entre 00:00 y 23:59")
    inasistencia_injustificada = fields.Float('Inasistencia injustificada', digits=(10, 2))
    permiso_no_remunerado_dias_check = fields.Boolean('Permiso no Remunerado (dias)')
    permiso_no_remunerado_dias_value = fields.Integer('Permiso no Remunerado (dias) Valor', size=2)
    permiso_no_remunerado_hrs_check = fields.Boolean('Permiso no Remunerado (hrs)')
    permiso_no_remunerado_hrs_value = fields.Char('Permiso no Remunerado (hrs) Valor', size=5, help="Acepta valores entre 00:00 y 23:59")
    permiso_no_remunerado_hrs = fields.Float('Permiso no remuneradpo', digits=(10, 2))
    retencion_faov_check = fields.Boolean('Retencion FAOV')
    retencion_fondo_ahorro_check = fields.Boolean('Retencion Fondo de Ahorro')
    retencion_islr_check = fields.Boolean('Retencion ISLR')
    retencion_islr_value = fields.Float('Retencion ISLR Valor', digits=(2,2))
    # 'retencion_pie_check = fields.Boolean('Retencion P.I.E.')
    # 'retencion_sso_check = fields.Boolean('Retencion S.S.O.')
    deduccion_salarial_check = fields.Boolean('Deduccion Salarial check')
    deduccion_salarial_value = fields.Float('Deduccion Salarial value', digits=(10, 2))
    deduccion_no_salarial_check = fields.Boolean('Deduccion no Salarial check')
    deduccion_no_salarial_value = fields.Float('Deduccion no Salarial value', digits=(10, 2))


    def write(self, cr, uid, ids, values, context=None):
        if context is None: context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]
        self.validate_changed_fields(cr, uid, ids, values, 'write', context)
        res = super(hr_contract, self).write(cr, uid, ids, values, context)
        return res

    def create(self, cr, uid, values, context=None):
        if context is None: context = {}
        res = {}
        self.validate_changed_fields(cr, uid, None, values, 'create', context)
        res = super(hr_contract, self).create(cr, uid, values, context)
        return res

    def validate_changed_fields(self, cr, uid, ids, values, come_from, context=None):
        validar_value = False
        # BONO NOCTURNO
        bono_nocturno_check = values.get('bono_nocturno_check', False)
        if bono_nocturno_check:
            validar_value = True
        else:
            validar_value = False
        bono_nocturno_value = values.get('bono_nocturno_value', False)
        if bono_nocturno_value or validar_value:
            self.onchange_horas(cr, uid, None, bono_nocturno_value, 'bono_nocturno_value', come_from, context=context)
        # HORAS EXTRA DIURNO
        hrs_extra_diurno_check = values.get('hrs_extra_diurno_check', False)
        if hrs_extra_diurno_check:
            validar_value = True
        else:
            validar_value = False
        hrs_extra_diurno_value = values.get('hrs_extra_diurno_value', False)
        if hrs_extra_diurno_value or validar_value:
            self.onchange_horas(cr, uid, None, hrs_extra_diurno_value, 'hrs_extra_diurno_value',come_from, context=context)
        #else:
        #    if context.get('come_from', False) == 'write':
            #    self.onchange_horas(cr, uid, None, hrs_extra_diurno_value, 'hrs_extra_diurno_value', context=context)
        # HORAS NO LABORADAS
        hrs_no_lab_check = values.get('hrs_no_lab_check', False)
        if hrs_no_lab_check:
            validar_value = True
        else:
            validar_value = False
        hrs_no_lab_value = values.get('hrs_no_lab_value', False)
        if hrs_no_lab_value or validar_value:
            self.onchange_horas(cr, uid, None, hrs_no_lab_value, 'hrs_no_lab_value',come_from, context=context)
        # INASISTENCIA INJUSTIFICADA
        inasistencia_injustificada_check = values.get('inasistencia_injustificada_check', False)
        if inasistencia_injustificada_check:
            validar_value = True
        else:
            validar_value = False
        inasistencia_injustificada_value = values.get('inasistencia_injustificada_value', False)
        if inasistencia_injustificada_value or validar_value:
            self.onchange_horas(cr, uid, None, inasistencia_injustificada_value, 'inasistencia_injustificada_val',come_from, context=context)
        # PERMISO NO REMUNERADO
        permiso_no_remunerado_hrs_check = values.get('permiso_no_remunerado_hrs_check', False)
        if permiso_no_remunerado_hrs_check:
            validar_value = True
        else:
            validar_value = False
        permiso_no_remunerado_hrs_value = values.get('permiso_no_remunerado_hrs_value', False)
        if permiso_no_remunerado_hrs_value or validar_value:
            self.onchange_horas(cr, uid, None, permiso_no_remunerado_hrs_value, 'permiso_no_remunerado_hrs_value',come_from, context=context)
        return True

    @api.multi
    def restore_all_fields(self, ids):
        contract_fields = {}
        if not hasattr(ids, '__iter__'):
            contract_id = [ids]
        else:
            contract_id = ids.get('contract_id',False)
        c_id = 0
        for contract in self.browse(contract_id[0]):
            #ASIGNACIONES
            c_id = contract.id
            if contract.bono_nocturno_check:
                contract_fields.update({'bono_nocturno_check':False,'bono_nocturno_value':"'0'",'bono_nocturno':0.0})
            if contract.dias_sueldo_pend_check:
               contract_fields.update({'dias_sueldo_pend_check':False,'dias_sueldo_pend_value':0})
            if contract.feriados_check:
                contract_fields.update({'feriados_check':False,'feriados_value':0})
            if contract.feriados_no_lab_check:
                contract_fields.update({'feriados_no_lab_check':False,'feriados_no_lab_value':0})
            if contract.hrs_extra_diurno_check:
                contract_fields.update({'hrs_extra_diurno_check':False,'hrs_extra_diurno_value':"'0'",'hrs_extra_diurno':0.0})
            if contract.retro_sueldo_check:
                contract_fields.update({'retro_sueldo_check':False,'retro_sueldo_value':0.0})
            if contract.asignacion_salarial_check:
                contract_fields.update({'asignacion_salarial_check': False, 'asignacion_salarial_value': 0.0})
            if contract.asignacion_no_salarial_check:
                contract_fields.update({'asignacion_no_salarial_check': False, 'asignacion_no_salarial_value': 0.0})
            #DEDUCCIONES
            if contract.hrs_no_lab_check:
                contract_fields.update({'hrs_no_lab_check':False,'hrs_no_lab_value':"'0'",'hrs_no_lab':0.0})
            #
            if contract.inasistencia_injustificada_check:
                contract_fields.update({'inasistencia_injustificada_check':False,'inasistencia_injustificada_value':"'0'",'inasistencia_injustificada':0.0})
            #
            if contract.permiso_no_remunerado_dias_check:
                contract_fields.update({'permiso_no_remunerado_dias_check':False,'permiso_no_remunerado_dias_value':0})
            if contract.permiso_no_remunerado_hrs_check:
                contract_fields.update({'permiso_no_remunerado_hrs_check':False,'permiso_no_remunerado_hrs_value':"'0'",'permiso_no_remunerado_hrs':0.0})
            if contract.deduccion_salarial_check:
                contract_fields.update({'deduccion_salarial_check': False, 'deduccion_salarial_value':"'0'"})
            if contract.deduccion_no_salarial_check:
                contract_fields.update({'deduccion_no_salarial_check': False, 'deduccion_no_salarial_value':"'0'"})
        if contract_fields:
            sql_update_clause = 'update hr_contract set '
            sql_where_clause = ' where id in %s'
            sql_middle_cluase = ''
            sql_string = ''
            for clave, valor in contract_fields.items():
                sql_middle_cluase = sql_middle_cluase + clave + '=' + str(valor) + ', '
            sql_middle_cluase = sql_middle_cluase[:-2]
            sql_string = sql_update_clause + sql_middle_cluase + sql_where_clause
            self.env.cr.execute(sql_string, (tuple([c_id]),))
                # self.write(contract_id,contract_fields)

    def validate_extra_hrs(self, field, value):
        res = {}
        extra_hrs_obj = re.compile(r"""^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$""", re.X)
        if extra_hrs_obj.search(value):
            res = {
                field: value
            }
        return res

    def onchange_horas(self, cr, uid, ids, value, field, come_from=None, context=None):
        res = {}
        valor = 0.0
        if 'float' not in field:
            if value:
                res = self.validate_extra_hrs(field, value)
                if not res:
                    raise Warning(('El formato de las horas es incorrecto, Solo acepta valores entre 00:00 y 23:59. \n'
                                   'Ej: 20:55. Por favor intente de nuevo'))
                valor = self.convert_time_to_value(value)
                test = field[:-len('_value')]
                res.update({field[:-len('_value')]:valor})
            else:
                if come_from:
                    raise Warning(('Ha seleccionado el campo %s, pero no ha introducido ningún valor.\n '
                                   'No puede guardar el campo vacío. Por favor intente de nuevo')%(self.get_name_field(cr, uid, field, context=context)))
        return {'value': res}

    def get_name_field(self, cr, uid, field, context=None):
        nombre = ''
        field_obj = self.pool.get('ir.model.fields')
        field_id = field_obj.search(cr, uid,[('model','=','hr.contract'),('name','=',field)] , context=context)
        if field_id:
            nombre = field_obj.read(cr, uid,field_id, ['field_description'], context=context)
            nombre = str(nombre[0]['field_description']).split('Valor')[0]
        return nombre

    def convert_time_to_value(self,time=None):
        result = horas = temp_value = 0.0
        if time:
            t = time.split(':')
            horas = float(t[0])
            temp_value = float(t[1])/60.0
            result = horas + temp_value
        return result

hr_contract()

class hr_payslip(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    @api.multi
    def hr_verify_sheet(self):
        # if context is None: context = {}
        # if not hasattr(ids, '__iter__'): ids = [ids]
        res = super(hr_payslip, self).hr_verify_sheet()
        is_payoff = self.env.context.get('come_from', False)
        if not  is_payoff:
            contract_id = self.read(['contract_id'])
            contract_obj = self.env['hr.contract']
            if contract_id[0]['contract_id']:
                contract_obj.restore_all_fields(contract_id[0])
            else:
                raise Warning(("La nomina no se ejecuto. El Empleado %s no tiene contrato.")%(self.employee_id.name))
        return res
hr_payslip()

class hr_payslip_run(models.Model):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'

    # def close_payslip_run(self, cr, uid, ids, context=None):
    #     if context is None: context = {}
    #     if not hasattr(ids, '__iter__'): ids = [ids]
    #     res = super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context)
    #     slip_ids_obj = self.browse(cr, uid, ids)
    #     contract_obj = self.pool.get('hr.contract')
    #     hr_payslip_obj = self.pool.get('hr.payslip')
    #     for slip_id in hr_payslip_obj.browse(cr, uid, slip_ids_obj[0].slip_ids.id):
    #         contract_id = slip_id.contract_id.id
    #         contract_obj.restore_all_fields(cr, uid, contract_id, context)
    #     return res
    @api.multi
    def close_payslip_run(self):
        # if context is None: context = {}
        # if not hasattr(ids, '__iter__'): ids = [ids]
        res = super(hr_payslip_run, self).close_payslip_run()
        for slip_run in self.browse(self.ids):
            for slip in slip_run.slip_ids:
                slip.contract_id.restore_all_fields(slip.contract_id.id)
        return res
hr_payslip_run()
