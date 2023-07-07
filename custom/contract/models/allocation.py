from odoo import models, fields, api



class allocation(models.Model):
    # _name = 'contract.contract'
    # _description = 'contract.contract'
    _inherit='hr.leave.allocation'
    contract_id = fields.Many2one( 'hr.contract',ondelete="cascade")
  
