# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_trumba import get_calendar_by_name


class TestCalendarParse(TestCase):

    def test_ical_parsing(self):
        calendar = get_calendar_by_name('sea_acad-comm')
        events = calendar.walk('vevent')
        self.assertEqual(len(events), 4)
        self.assertIsNotNone(events[0]['DESCRIPTION'])

        self.assertRaises(DataFailureException,
                          get_calendar_by_name,
                          'sea_none')

    def test_ical_parsing_err(self):
        calendar = get_calendar_by_name('sea_err')
        self.assertEqual(len(calendar.walk('vevent')), 1)
        # can't reprod the issue
        # https://github.com/collective/icalendar/commit/
        # 4f5f70bd5b863e0997ff93e2f9cf9187413730a3
