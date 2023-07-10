# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date
from dateutil.relativedelta import *
from . import duration


class contract(models.Model):
    # _name = 'contract.contract'
    # _description = 'contract.contract'
    _inherit='hr.contract'
    # _inherits = {"contract.duration": "duration_id"}
    duration_id = fields.Many2one('contract.duration',string= 'Duration of the contract',required=1)
    handover = fields.Integer( string="Handover duration",related='job_id.handover')
    hourly = fields.Monetary( string="Hourly rate",compute="_compute_hourly")
    holiday_allocation=fields.One2many("hr.leave.allocation","contract_id",
                                        invisible=True)
    warnings = fields.Integer( string="Max warnings",related='duration_id.warnings')
    annual = fields.Integer( string="Annual days off",related='duration_id.annual' )
    critical = fields.Integer( string="critical days off",related='duration_id.critical')
    date_end=fields.Date(compute='_compute_enddate')
     
    @api.model
    def create(self,values):
        # ann_id,crit_id=self.get_vacation_types()
        # print("=========================")
        print(self.env.ref('hr_holidays.holiday_status_cl').id)
        
        ann_id=self.env.ref('hr_holidays.holiday_status_cl').id
        crit_id=self.env.ref('contract.holiday_status_fcl').id
        print(ann_id)
        if values['duration_id']!=False:
            list=[(0,0,{'name':"Contract Annual"  ,'holiday_type':'employee' 
                    ,'employee_id':values['employee_id'] ,'date_from': values['date_start'] 
                    ,'date_to': values['date_end'] ,'holiday_status_id':ann_id
                    ,'allocation_type':'regular' ,'number_of_days':self.duration_id.search([('id','=',values["duration_id"])]).annual  }),
                (0,0,{'name':"Contract Critical"  ,'holiday_type':'employee' 
                    ,'employee_id':values['employee_id'] ,'date_from': values['date_start'] 
                    ,'date_to': values['date_end'] ,'holiday_status_id':crit_id
                    ,'allocation_type':'regular','number_of_days':self.duration_id.search([('id','=',values["duration_id"])]).critical  })]
            values['holiday_allocation']=list

        
        print(values)
        ret=super(contract,self).create(values)
        return ret
        
    
    def write(self,values):
        ret=super(contract,self).write(values)
        print(values)
        # ann_id,crit_id=self.get_vacation_types()
        ann_id=self.env.ref('hr_holidays.holiday_status_cl').id
        crit_id=self.env.ref('contract.holiday_status_fcl').id
        if values['duration_id']!=False:
            list=[(1,self.holiday_allocation[0].id,{'name':"Contract Annual"  ,'holiday_type':'employee' 
                    ,'employee_id':self.employee_id.id ,'date_from': self.date_start
                    ,'date_to': self.date_end ,'holiday_status_id':ann_id
                    ,'allocation_type':'regular' ,'number_of_days':self.duration_id.annual   }),
                (1,self.holiday_allocation[1].id,{'name':"Contract Critical"  ,'holiday_type':'employee' 
                    ,'employee_id':self.employee_id.id ,'date_from': self.date_start 
                    ,'date_to': self.date_end ,'holiday_status_id':crit_id
                    ,'allocation_type':'regular','number_of_days':self.duration_id.critical   })]
            values['holiday_allocation']=list

        
        print(values)
        ret=super(contract,self).write(values)
        return ret
  

    @api.depends('duration_id')
    def _compute_enddate(self): 
        for rec in self:  
            rec.date_end=rec.date_start+relativedelta(months=+rec.duration_id.months)

    
    @api.depends('wage','resource_calendar_id')
    def _compute_hourly(self):
        for rec in self:
            wage=rec.wage
            weekly=rec.resource_calendar_id.hours_per_day
        rec.hourly=wage/(weekly*4.0*5)

    
    @api.model
    def cron_send_email(self):
        template_obj = self.env.ref('contract.1week_notice_email_template')
        #print(template_obj)
        rec_obj=self.env['hr.contract'].search([]).filtered(lambda x: x.date_end == fields.date.today()+relativedelta(days=7))
        print(rec_obj)

        for rec in rec_obj:
            
            template_obj.send_mail(rec.id)
        
            