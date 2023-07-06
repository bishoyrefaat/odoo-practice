from odoo import models, fields, api
from datetime import timedelta, date
from dateutil.relativedelta import *


class holiday_type(models.Model):
    _name = 'contract.holiday'
    # _inherits={'hr.leave.type':"holiday_type_id"}
    
    name = fields.Many2one( 'hr.leave.type',string="Holiday type" )
    daycount= fields.Integer( string="Days off" )
    
    
    def name_get(self):
        ret=[]
        
        for rec in self:
            out=str(rec.name.name) +" "+ str(rec.daycount)
            print(out)
            ret.append((rec.id , out ))
            print(ret)
        return ret
