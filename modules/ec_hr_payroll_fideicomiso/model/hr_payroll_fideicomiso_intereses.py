# coding: utf-8

from openerp import fields, models, api
from openerp.osv import osv
from openerp.exceptions import Warning
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payroll_fideicomiso_intereses(models.Model):
    _name = 'hr.payroll.fideicomiso.intereses'
    _description = 'tambla de interese de fideicomiso'

    MESES = [('1', 'Enero'),
             ('2', 'Febrero'),
             ('3', 'Marzo'),
             ('4', 'Abril'),
             ('5', 'Mayo'),
             ('6', 'Junio'),
             ('7', 'Julio'),
             ('8', 'Agosto'),
             ('9', 'Septiembre'),
             ('10', 'Octubre'),
             ('11', 'Noviembre'),
             ('12', 'Diciembre')]

    anio = fields.Integer('Anio tasa de interes')
    mes = fields.Selection(MESES,'Mes tasa de interes')
    tasa = fields.Float('Tasa Interes',digits=(3,2), help=u'Tasa de Interés activa')
    numero_gaceta  = fields.Char('Numero gaceta', size=7, help=u'Número de gaceta oficial donde se publicó la tasa de interés')
    fecha_gaceta = fields.Date('Fecha gaceta')
    activa_pasiva = fields.Float('Tasa activa', digits=(3,2), help='Promedio entre tasa activa y pasiva')

    @api.v7
    def get_tasa(self, cr, uid,fecha, context=None):
        tasa = 0.0
        fecha = datetime.strptime(fecha,DEFAULT_SERVER_DATE_FORMAT)
        interes_id = self.search(cr, uid, [('anio','=',fecha.year),('mes','=',str(fecha.month))], context=context)
        for i in self.browse(cr, uid,interes_id, context=context):
            tasa = i.activa_pasiva

        return tasa
