# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime
from datetime import *
import time
from datetime import datetime, timedelta
from datetime import date, datetime, timedelta

class Doctor(models.Model):
    _name = "parapharma.doctor"


    name = fields.Char("Nombre de doctor")
    birthdate = fields.Date("Fecha de cumpleaños")
    hobby = fields.Char("Interes/hobby")
    description = fields.Char("Descripción de cliente")
 	comments = fields.Text("Observaciones")
 	addres = fields.Text("Dirección")
 	especialidad_id = fields.Many2one("parapharma.specialidad", "Especialidad")


 class Profile(models.Model):
 	_name = "parapharma.specialidad"

 	name = fields.Char("Especialidad")






    
