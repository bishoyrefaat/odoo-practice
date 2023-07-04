# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date
from dateutil.relativedelta import *


class contract(models.Model):
    # _name = 'contract.contract'
    # _description = 'contract.contract'
    _inherit='hr.contract'
   

    duration=fields.Selection([('6months','6 Months'),('year','Year')],
                             string="duraction" , default='6months')
    annual = fields.Integer( string="Annual days off" )
    critical = fields.Integer( string="critical days off")
    warnings = fields.Integer( string="Max warnings")
    handover = fields.Integer( string="Handover duration")
    hourly = fields.Monetary( string="Hourly rate")

   
    @api.onchange('duration')
    def onchange_duration(self):
        if self.duration == "year" :
            self.annual=14
            self.critical=8
            self.warnings=3
            self.date_end=self.date_start+relativedelta(years=+1)
        elif self.duration == "6months":
            self.annual=6
            self.critical=3
            self.warnings=2
            self.date_end=self.date_start+relativedelta(months=+6)
            print(self.date_end)

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id.name =="Human Resources Manager":
            self.handover=30
        else:
            self.handover=14

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
      res['duration']='6months'
      res['handover']='14'
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
            # print(rec.name)
            # print(rec.hr_responsible_id.email)
            # print(rec.hr_responsible_id.name)

            body = template_obj.body_html
            body=body.replace('--variable_dynamic_1--',str(rec.name))
            body=body.replace('--variable_dynamic_2--',str(rec.employee_id.name))
            mail_values = {
            'subject': template_obj.subject,
            'body_html': body,
            'email_to': rec.hr_responsible_id.email,
            # 'email_cc':';'.join(map(lambda x: x, email_cc)),
            # 'email_from': template_obj.email_from,
            }
            if rec.hr_responsible_id.email!= false :
                create_and_send_email = self.env['mail.mail'].create(mail_values).send()