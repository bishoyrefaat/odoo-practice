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
    
    # def get_vacation_types(self)->list:
    #     # print("++++++++++++++++++++++++++++++")
    #     obj=self.env['hr.leave.type']
    #     crit_id=obj.search([('name','=','Critical Days Off')])
    #     ann_id=obj.search([('name','=','Annual Days Off')])
        
    #     if ann_id.id==False:
    #         print("creating annual day off type...")
    #         obj.create({'name':'Annual Days Off','leave_validation_type': 'no_validation'
    #                     ,'employee_requests':'no','requires_allocation':'yes',
    #                      'request_unit':'day','time_type':'leave'})
    #     if crit_id.id==False:
    #         print("creating critical day off type...")
    #         obj.create({'name':'Critical Days Off','leave_validation_type': 'no_validation',
    #                     'employee_requests':'no','requires_allocation':'yes',
    #                     'request_unit':'day','time_type':'leave'}) 
    #     crit_id=obj.search([('name','=','Critical Days Off')],limit=1).id
    #     ann_id=obj.search([('name','=','Annual Days Off')],limit=1).id
    #     print(str(crit_id)+"    "+str(ann_id))
    #     return [ann_id,crit_id]  
  
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
        # print("=============="+str(self.date_start))
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
        template_obj = self.env['mail.template'].sudo().search([('name','=','1week Email Template')], limit=1)
        # query = """ SELECT employee_id FROM hr_contract 
        # WHERE date_end > CURRENT_DATE::date + '6 month'::interval"""
        # self.env.cr.execute(query)
        # rec_obj=self.env.cr.fetchall()
        #rec_obj=self.env['hr.contract'].search([('date_end','>=',fields.date.today()+relativedelta(months=-5))]) #condition for testing puroses only
        rec_obj=self.env['hr.contract'].search([('date_end','=',fields.date.today()+relativedelta(days=-7))])
       
        print(rec_obj)
        for rec in rec_obj:
           
            if rec.hr_responsible_id.email :
                body = template_obj.body_html
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')+"/web#id="+str(rec.id)+"&cids=1&menu_id=273&action=436&model=hr.contract&view_type=form"
                body=body.replace('--variable_dynamic_0--',base_url)
                body=body.replace('--variable_dynamic_1--',str(rec.name))
                body=body.replace('--variable_dynamic_2--',str(rec.date_end))
                body=body.replace('--variable_dynamic_3--',str(rec.employee_id.name))
                mail_values = {
                'subject': template_obj.subject,
                'body_html': body,
                'email_to': rec.hr_responsible_id.email,
                # 'email_cc':';'.join(map(lambda x: x, email_cc)),
                # 'email_from': template_obj.email_from,
                }
                
                create_and_send_email = self.env['mail.mail'].create(mail_values).send()
            