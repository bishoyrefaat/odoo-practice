# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date
from dateutil.relativedelta import *


class duration(models.Model):
    _name = 'contract.duration'
    _description = 'contract.duration'
    _sql_constraints = [   ('unique_duration_name', 'unique(name)',
                      'Choose another name - it has to be unique!')]
   
    name = fields.Char(string="duration name" , required=1 )
    warnings = fields.Integer( string="Max warnings")
    months = fields.Integer(string='Contract duration (months)' )
    annual = fields.Integer( string="Annual days off" )
    critical = fields.Integer( string="critical days off")
    # holiday_type_id=fields.Many2many("contract.holiday","duration_holiday_rels",
    #                                  "duration_id","holiday_id",string="Available vacation type",
    #                                  readonly=False)
    
   
    

