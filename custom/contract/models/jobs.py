#  -*- coding: utf-8 -*-

from odoo import models, fields, api



class jobs(models.Model):
    # _name = 'contract.contract'
    # _description = 'contract.contract'
    _inherit='hr.job'
    handover = fields.Integer( string="Handover duration")
  
