#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import json
import re
import datetime


# Regex pattern definitions
from jrnl.util import date2string, datetime2string

DATE_PATTERN = r'\d\d\d\d\-\d\d\-\d\d'  # YEAR-MONTH-DAY  e.g. 1984-01-24
STATUS_REGEX_DICT = {
    r'\[ \]': 'incomplete',
    r'\{%s\}(?!\[)' % DATE_PATTERN: 'incomplete',
    r'\[x\]': 'complete',
    r'\{%s\}\[x\]' % DATE_PATTERN: 'complete',
    r'\{%(date)s\}\[%(date)s\]' % dict(date=DATE_PATTERN): 'complete',
}
CONTENT_PATTERN = r' ?(?P<content>.*)'

ANY_TODOS_REGEX = r''
# Or's together all possible status patterns.
i = 0
for pattern in STATUS_REGEX_DICT.iterkeys():
    if i > 0:
        ANY_TODOS_REGEX = r'{}|'.format(ANY_TODOS_REGEX)
    ANY_TODOS_REGEX = r'{}(?:{})'.format(ANY_TODOS_REGEX, pattern)
    i += 1
ANY_TODOS_REGEX = re.compile(r'(?P<all>(?:%s)%s)' % (ANY_TODOS_REGEX, CONTENT_PATTERN), re.MULTILINE)


class Todo:

    def __init__(self, text_repr, entry):
        self.text_repr = text_repr
        self.entry = entry

        self.status = None
        self.completed_date = None
        self.due_date = None
        self.content = None

        self.parse_text_repr()

    @property
    def is_complete(self):
        return self.status == 'complete'

    def extract_date(self, start_pattern=None, end_pattern=None):
        """
        Extracts a date from the text_repr, isolating which date if specified by the start and end patterns.
        :rtype: datetime.date
        """
        if start_pattern is None:
            start_pattern = r''
        if end_pattern is None:
            end_pattern = r''

        regex = re.compile(r'.*%s(?P<date>%s)%s.*' % (start_pattern, DATE_PATTERN, end_pattern))
        match = regex.match(self.text_repr)
        if not match:
            return None
        date_string = match.group('date')
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    def parse_text_repr(self):
        if not isinstance(self.text_repr, (str, unicode)):
            return

        # Sets status
        for pattern, status in STATUS_REGEX_DICT.iteritems():
            if re.compile(pattern).match(self.text_repr):
                self.status = status

        if self.is_complete:
            self.completed_date = self.extract_date(r'\[', r'\]')

        self.due_date = self.extract_date(r'\{', r'\}')

        match = ANY_TODOS_REGEX.match(self.text_repr)
        if match is not None:
            self.content = match.group('content')

    @classmethod
    def parse_entry_todos(cls, entry):
        """
        :type entry: Entry.Entry
        :rtype: list[Todo]
        """
        fulltext = entry.get_fulltext(lower=False)
        todos_matches = [m.group('all') for m in re.finditer(ANY_TODOS_REGEX, fulltext)]
        todos = []
        for match in todos_matches:
            todos.append(Todo(match, entry))
        return todos

    def to_dict(self):
        return {
            'text_repr': self.text_repr,
            'status': self.status,
            'content': self.content,
            'completed_date': date2string(self.completed_date),
            'due_date': date2string(self.due_date),
        }

    def to_item_format(self):
        ret = "* {}".format(self.content)
        ret += "\n    Entry: {}".format(datetime2string(self.entry.date, self.entry.journal))
        ret += "\n           {}".format(self.entry.title)
        if self.due_date:
            ret += "\n    Due: {}".format(date2string(self.due_date))
        if self.completed_date:
            ret += "\n    Completed: {}".format(date2string(self.completed_date))
        return ret

    def __unicode__(self):
        return self.text_repr

    def __repr__(self):
        return "<Todo '{}'>".format(self.text_repr)
