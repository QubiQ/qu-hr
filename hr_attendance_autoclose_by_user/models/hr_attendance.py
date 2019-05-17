# -*- coding: utf-8 -*-
# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.model
    def check_for_incomplete_attendances(self):
        stale_attendances = self.search(
            [('check_out', '=', False)])
        reason = self.env['hr.attendance.reason'].search(
            [('code', '=', 'S-CO')], limit=1)
        call_super = False
        for att in stale_attendances:
            check_in = datetime.strptime(
                    att.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
            intervals = att.employee_id.calendar_id.\
                get_working_intervals_of_day(check_in)
            if intervals:
                date_end_day = intervals[-1][-1]
                if date_end_day <= fields.datetime.now():
                    vals = {'check_out': intervals[-1][-1]}
                    if reason:
                        vals['attendance_reason_ids'] = [(4, reason.id)]
                    att.write(vals)
            else:
                call_super = True
        if call_super:
            super(HrAttendance, self).check_for_incomplete_attendances()
