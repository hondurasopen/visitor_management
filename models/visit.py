# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime
from datetime import *
import time
from datetime import datetime, timedelta
from datetime import date, datetime, timedelta

class Doctor(models.Model):
    _name = "parapharma.visita"
    _rec_name = "doctor_id"

    date = fields.Date("Fecha de visita")
    doctor_id = fields.Many2one("parapharma.doctor", "Médico", required=True)
    especialidad_id = fields.Many2one("parapharma.especialidad", "Especialidad", required=True)
    comments = fields.Text("Observaciones")
    location = fields.Text("Ubicación", required=True)
    competence_id = fields.Char("Afinidad Con Competencia", required=True)
    user_id = fields.Many2one("res.users", "Visitador")

    @api.onchange("doctor_id")
    def onchangedoctor(self):
        if self.doctor_id:
            self.especialidad_id = self.doctor_id.especialidad_id
            self.location = self.doctor_id.location
            self.competence_id = self.doctor_id.competence_id



    
