# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning
from datetime import datetime
from datetime import *
import time
from datetime import datetime, timedelta
from datetime import date, datetime, timedelta

class PlanificacionSemanal(models.Model):
    _name = "doff.planificacion.semanal"
    _order = "name desc"
    _inherit = ['mail.thread']
    _rec_name = "planificacion"

    def get_default_user(self):
        return self.env.user.id   
    
    name = fields.Date("Fecha inicial", track_visibility='onchange')
    fecha_final = fields.Date("Fecha final", track_visibility='onchange')
    
    week_year = fields.Char("Semana del Año",track_visibility='onchange')
    responsable = fields.Many2one("res.users", "Gerente de Operaciones", default=get_default_user,track_visibility='onchange')
    year_month = fields.Char("Mes del Año",track_visibility='onchange')
    planificacion = fields.Char("Planificación")
    state = fields.Selection([('draft', 'Borrador'), ('aprobado', 'Aprobada'), ('progreso', 'En Progreso'), ('finalizada', 'Finalizada')], 
        "Estado", default='draft', track_visibility='onchange')
    porc_cumplimiento = fields.Float("Cumplimiento")
    prod_esperada = fields.Float("Producción Esperada", compute='get_total_prd_esperada')
    prod_real = fields.Float("Producción real")

    doff_planificacion_semanal_detail_ids = fields.One2many("doff.planificacion.semanal.detail","doff_planificacion_semanal_id","doff_planificacion_semanal_detail_ids")
    doff_planificacion_semanal_info_ids = fields.One2many("doff.planificacion.semanal.info","doff_planificacion_semanal_id","doff_planificacion_semanal_info_ids")
    num_tabaqueros_material = fields.Integer("Tabaqueros Material")
    num_tabaqueros_picadura = fields.Integer("Tabaqueros Picadura")
    prod_esperada_material = fields.Float("Producción Material")
    prod_esperada_picadura = fields.Float("Producción Picadura")
    dias = fields.Integer("# dias")

    plan_mp_id = fields.Many2one("doff.planificacion.semanal.mp", "Requerimientos de Material")


    @api.multi
    def set_prod(self):
        for l in self.doff_planificacion_semanal_detail_ids:
            l.prod_esperada = l.num_tabaqueros * l.prom_production
            l.tipo_material = l.product_id.tipo_material
            for l in self.doff_planificacion_semanal_detail_ids:
                if l.product_id.tipo_material == 'material':
                    self.num_tabaqueros_material += l.num_tabaqueros
                    self.prod_esperada_material += l.prod_esperada
                if l.product_id.tipo_material == 'picadura':
                    self.num_tabaqueros_picadura += l.num_tabaqueros
                    self.prod_esperada_picadura += l.prod_esperada

    @api.multi
    def set_borrador(self):
        self.prod_real = 0
        self.porc_cumplimiento = 0
        for l in self.plan_mp_id.plan_mp_ids:
            l.unlink()
        if self.plan_mp_id:
            self.plan_mp_id.unlink()
        self.write({'state': 'draft'})


    @api.multi
    def unlink(self):
        if self.state == 'finalizada' or self.state == 'progreso':
            raise Warning(('No puede borrar estos registros ya que ya siendo procesados'))
        return super(PlanificacionSemanal, self).unlink()


    @api.multi
    def set_finalizar(self):
    	self.write({'state': 'finalizada'})


    @api.multi
    def set_plan_semanal(self):
        if self.doff_planificacion_semanal_detail_ids:
            fecha_i = datetime.strptime(self.name, '%Y-%m-%d')
            fecha_f = datetime.strptime(self.fecha_final, '%Y-%m-%d')
            resta = fecha_f - fecha_i
            self.dias = resta.days + 1
            obj_products = self.env["doff.planificacion.semanal.info"]
            self.doff_planificacion_semanal_info_ids.unlink()
            prod_esperada_material = 0
            prod_esperada_picadura = 0
            self.num_tabaqueros_material = 0
            self.num_tabaqueros_picadura = 0
            for l in self.doff_planificacion_semanal_detail_ids:
                if l.product_id.tipo_material == 'material':
                    self.num_tabaqueros_material += l.num_tabaqueros
                    prod_esperada_material += l.prod_esperada
                if l.product_id.tipo_material == 'picadura':
                    self.num_tabaqueros_picadura += l.num_tabaqueros
                    prod_esperada_picadura += l.prod_esperada
                vals = {
                    'doff_planificacion_semanal_id': self.id,
                    'product_id': l.product_id.id,
                    'sku': l.product_id.default_code,
                    'description': l.product_id.name,
                    'tipo_material': l.product_id.tipo_material,
                    'prod_esperada': l.prod_esperada * self.dias,
                }
                id_ls = obj_products.create(vals)
            self.prod_esperada_material = prod_esperada_material * self.dias
            self.prod_esperada_picadura = prod_esperada_picadura * self.dias
            self.create_requirment_pm()
            self.write({'state': 'aprobado'})


    @api.multi
    def create_requirment_pm(self):
        if self.doff_planificacion_semanal_detail_ids:
            for l in self.plan_mp_id.plan_mp_ids:
                l.unlink()
            if self.plan_mp_id:
                self.plan_mp_id.unlink()
            obj_plan_mp = self.env["doff.planificacion.semanal.mp"]
            obj_plan_mp_ln = self.env["doff.planificacion.semanal.mp.summary"]
            vals = {
                'plan_id': self.id,
                'name': self.planificacion,
                'state': 'draft', 
            }
            id_plan_mp = obj_plan_mp.create(vals)
            for l in self.doff_planificacion_semanal_detail_ids:
                num_fundas = int(round( (l.prod_esperada * self.dias) / 200) ) 
                vals_l = {
                    'plan_mp_id': id_plan_mp.id, 
                    'product_id': l.product_id.id,
                    'cantidad_cigarros': l.prod_esperada * self.dias,
                    'num_fundas': num_fundas,
                }
                for bom in l.product_id.bom_ids:
                    if bom.bom_active:
                        for receta_lines in bom.bom_line_ids:
                            if receta_lines.product_id.tipo_materia_id.name == 'Liga':
                                vals_l["funda_id"] = receta_lines.product_id.id
                                vals_l["peso_liga"] = int(round(((l.prod_esperada * self.dias) / bom.product_qty ) * receta_lines.weight_lbs))
                            if receta_lines.product_id.tipo_materia_id.name == 'Capa_rezagada':
                                vals_l["capa_id"] = receta_lines.product_id.id
                                vals_l["hojas_capas"] = int(round(( (l.prod_esperada * self.dias) / bom.product_qty) * receta_lines.product_qty))
                            if receta_lines.product_id.tipo_materia_id.name == 'Banda':
                                vals_l["banda_id"] = receta_lines.product_id.id
                                vals_l["hojas_banda"] = int(round(( (l.prod_esperada * self.dias) / bom.product_qty) * receta_lines.product_qty))

                id_plan_ln = obj_plan_mp_ln.create(vals_l) 

            self.plan_mp_id = id_plan_mp.id


    @api.one
    @api.depends("doff_planificacion_semanal_detail_ids.prom_production", "doff_planificacion_semanal_detail_ids.num_tabaqueros")
    def get_total_prd_esperada(self):
        if self.doff_planificacion_semanal_detail_ids:
            for l in self.doff_planificacion_semanal_detail_ids:
                self.prod_esperada += (l.prom_production * float(l.num_tabaqueros))

            self.prod_esperada = self.prod_esperada * self.dias


    @api.onchange("name")
    def onchangefecha(self):
        if self.name:
            varialble_string = datetime.strptime(self.name, '%Y-%m-%d')
            self.week_year = varialble_string.isocalendar()[1]
            self.year_month = varialble_string.strftime("%B")
            self.planificacion = "Semana " + str(self.week_year)

    @api.multi
    def set_prod_diaria(self):
        if self.doff_planificacion_semanal_info_ids:
            obj_line_prd = self.env["doff.pureria.supervisar.linea.sku"].search([('obj_parent.date_production', '>=', self.name), 
            	('obj_parent.date_production', '<=', self.fecha_final), ('obj_parent.state', '=', 'aprobado')])
            for l in self.doff_planificacion_semanal_info_ids:
            	l.prod_real = 0
            	self.prod_real = 0
            for obj_product in obj_line_prd:
            	lin = self.env["doff.planificacion.semanal.info"].search([('product_id', '=', obj_product.product_id.id), 
                    ('doff_planificacion_semanal_id', '=', self.id)])
            	if lin:
                    lin.prod_real += obj_product.total_production
                    lin.porc_cumplimiento = ( lin.prod_real / lin.prod_esperada ) * 100
                    self.prod_real += obj_product.total_production
            if self.prod_esperada > 0:
                acumulado = 0
                for info in self.doff_planificacion_semanal_info_ids:
                    if info.porc_cumplimiento > 100:
                        acumulado += 100
                    else:
                        acumulado += info.porc_cumplimiento
                self.porc_cumplimiento = acumulado / len(self.doff_planificacion_semanal_info_ids)



class PlanificacionSemanalDetail(models.Model):
    _name = "doff.planificacion.semanal.detail"
    _order = "prioridad"

    product_id = fields.Many2one("product.product","Código producción")
    code = fields.Char("SKU", related="product_id.default_code")
    name = fields.Char("Descripción", related="product_id.name")
    #vitola = fields.Char("Vitola")
    vitola = fields.Many2one("doff.category.size.line", "Vitola", related='product_id.vitola_id')
    prom_production = fields.Float("Promedio producción", default=350)
    num_tabaqueros = fields.Integer("# Parejas")
    prod_esperada = fields.Float("Producción Esperada")
    tipo_material = fields.Selection([('material', 'Long Filler'), ('picadura', 'Short Filler')], string='Tipo Material')
    prioridad = fields.Selection([('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')], string='Prioridad', default='Media')

    doff_planificacion_semanal_id = fields.Many2one("doff.planificacion.semanal","Plan semanal")

    @api.onchange("num_tabaqueros", "prom_production")
    def onchange_pro_esperada(self):
        self.prod_esperada = (self.num_tabaqueros * self.prom_production)


    @api.onchange('product_id')
    def getInfo(self):
        if self.product_id:
            # self.vitola = self.product_id.vitola_id.size_articles
            self.tipo_material = self.product_id.tipo_material


class PlanificacionSemanalInfo(models.Model):
    _name = "doff.planificacion.semanal.info"
    _order = "porc_cumplimiento asc"

    product_id = fields.Many2one("product.product", "Producto")
    sku = fields.Char("SKU")
    description = fields.Char("Descripción")
    #vitola = fields.Char("Vitola")
    vitola = fields.Many2one("doff.category.size.line", "Vitola", related='product_id.vitola_id')
    tipo_material = fields.Selection([('material', 'Long Filler'), ('picadura', 'Short Filler')], string='Tipo Material')
    prod_esperada = fields.Float("Producción esperada")
    prod_real = fields.Float("Producción real")
    porc_cumplimiento = fields.Float("%")
    comments = fields.Char("Comentarios")

    doff_planificacion_semanal_id = fields.Many2one("doff.planificacion.semanal","doff_planificacion_semanal_id")



    
