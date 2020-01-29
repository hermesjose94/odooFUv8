# coding: utf-8
from openerp import models, fields, api, _

class hr_employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee Studies"


    active_studies = fields.Boolean("Estudia Actualmente")
    career_id = fields.Many2one('hr.career', 'Carrera')
    lang_id = fields.Many2one('res.lang', 'Idiomas')
    courses = fields.Boolean(string="Cursos")
    courses_ids = fields.One2many('hr.course', 'employee_id', 'Cursos')
    stadies = fields.Boolean(string="Estudios")
    studies_ids = fields.One2many('hr.stadies', 'employee_id', 'Estudios')


class hr_carrera(models.Model):

    @api.multi
    def _get_carrera_position(self):
        res = []
        for employee in self:
            if employee.carrera_id:
                res.append(employee.carrera_id.id)
        return res

    _name = "hr.career"
    _description = "Carrera Description"

    name = fields.Char('Carrera Name', size=128, required=True, select=True)
    employee_ids = fields.One2many('hr.employee', 'career_id', 'Employees')



class hr_curso(models.Model):
    _name = "hr.course"

    name_instituto = fields.Char(string="Institucion", size=256)
    name_curso = fields.Char(string="Nombre del Curso", size=256)
    name_titulo = fields.Char(string="Titulo o Certificado", size=256)
    duracion = fields.Char(string="Duracion", size=60)
    graduado = fields.Boolean(string="Graduado")
    date_culminacion = fields.Date(string="Fecha de Culminacion")
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")


    _defaults = {
        'graduado': False,
    }

class hr_estudio (models.Model):

    _name = "hr.stadies"

    name_nivel = fields.Selection([('educacion_basica', 'Educación Basica'),
             ('bachiller', 'Bachiller'),
             ('tecnico_medio', 'Tecnico Medio'),
             #('tsu','T.S.U.'),
             ('universitario', 'Universitario'),
             ('licenciado', 'Licenciado'),
             #('maestria', 'Maestria'),
             #('doctorado', 'Doctorado'),
             #('postdoctorado', 'Postdoctorado')
                                   ],
                                  'Nivel Educativo')
    name_institute = fields.Char(string="Colegio/Institucion", size=256)
    anos_aprobado = fields.Integer(string="Años Aprobados", size=256)
    si_graduado = fields.Boolean(string="Graduado")
    fecha_culminacion = fields.Date(string="Fecha de Culminacion")
    nombre_titulo = fields.Selection([('educacion_basica', 'Educación Basica'),
             ('bachiller', 'Bachiller'),
             ('tecnico_medio', 'Tecnico Medio'),
             #('tsu','T.S.U.'),
             ('universitario', 'Universitario'),
             ('licenciado', 'Licenciado'),
             #('maestria', 'Maestria'),
             #('doctorado', 'Doctorado'),
             #('postdoctorado', 'Postdoctorado')
                                   ], string='Titulo o Certificado Obtenido')
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")
