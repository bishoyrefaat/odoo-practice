# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date
from dateutil.relativedelta import *
from . import duration


class contract(models.Model):
    # _name = 'contract.contract'
    # _description = 'contract.contract'
    _inherit='hr.contract'
    _inherits = {"contract.duration": "duration_id"}
    duration_id = fields.Many2one('contract.duration',string= 'Duration of the contract')

    
    # annual = fields.Integer( string="Annual days off" )
    # critical = fields.Integer( string="critical days off")
    # warnings = fields.Integer( string="Max warnings")
    handover = fields.Integer( string="Handover duration")
    hourly = fields.Monetary( string="Hourly rate")


    @api.onchange('duration_id')
    def onchange_duration(self):
    #     if self.duration == "year" :
    #         self.annual=14
    #         self.critical=8
    #         self.warnings=3
    #         self.date_end=self.date_start+relativedelta(years=+1)
    #     elif self.duration == "6months":
    #         self.annual=6
    #         self.critical=3
    #         self.warnings=2
    #         self.date_end=self.date_start+relativedelta(months=+6)
    #         print(self.date_end)
        # self.annual=self.duration.annual
        # self.critical=self.duration.critical
        # self.warnings=self.duration.warnings
        
        self.date_end=self.date_start+relativedelta(months=+self.duration_id.months)

    @api.onchange('job_id')
    def onchange_job_id(self):
            
            self.handover=self.job_id.handover
        

    def hourly_rate_calc(self, weeklyhours , wage):
        if weeklyhours==0:
            return 0.0
        return  wage/(4 *weeklyhours) 
    
       

    @api.onchange('wage')
    def onchange_wage(self):
        self.hourly=self.hourly_rate_calc(self.resource_calendar_id.hours_per_day, self.wage)
    

    @api.onchange('resource_calendar_id')
    def onchange_resource_calender_id(self):
        print(self.resource_calendar_id.hours_per_day)
        self.hourly=self.hourly_rate_calc(self.resource_calendar_id.hours_per_day, self.wage)


        
    @api.model
    def default_get(self, fields):
      res=super(contract,self).default_get(fields)
      res['handover']=self.job_id.handover
      return res
    
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
            print(rec.id)
            print(rec.name)
            print(rec.hr_responsible_id.email)
            print(rec.hr_responsible_id.name)
            if rec.hr_responsible_id.email :
                body = template_obj.body_html
                base_url = "http://localhost:8069/web#id="+str(rec.id)+"&cids=1&menu_id=273&action=436&model=hr.contract&view_type=form"
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
            