#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import json
import re
import datetime


# Regex pattern definitions
from jrnl.util import date2string, datetime2string

date_pattern = r'\d\d\d\d\-\d\d\-\d\d'
status_regex_dict = {
    r'\[ \]': 'incomplete',
    r'\{%s\}(?!\[)' % date_pattern: 'incomplete',
    r'\[x\]': 'complete',
    r'\{%s\}\[x\]' % date_pattern: 'complete',
    r'\{%(date)s\}\[%(date)s\]' % dict(date=date_pattern): 'complete',
}
content_pattern = r' ?(?P<content>.*)'

any_todos_regex = r''
# Or's together all possible status patterns.
i = 0
for pattern in status_regex_dict.iterkeys():
    if i > 0:
        any_todos_regex = r'{}|'.format(any_todos_regex)
    any_todos_regex = r'{}(?:{})'.format(any_todos_regex, pattern)
    i += 1
any_todos_regex = re.compile(r'(?P<all>(?:%s)%s)' % (any_todos_regex, content_pattern), re.MULTILINE)


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

        regex = re.compile(r'.*%s(?P<date>%s)%s.*' % (start_pattern, date_pattern, end_pattern))
        match = regex.match(self.text_repr)
        if not match:
            return None
        date_string = match.group('date')
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    def parse_text_repr(self):
        if not isinstance(self.text_repr, (str, unicode)):
            return

        # Sets status
        for pattern, status in status_regex_dict.iteritems():
            if re.compile(pattern).match(self.text_repr):
                self.status = status

        if self.is_complete:
            self.completed_date = self.extract_date(r'\[', r'\]')

        self.due_date = self.extract_date(r'\{', r'\}')

        match = any_todos_regex.match(self.text_repr)
        if match is not None:
            self.content = match.group('content')

    @classmethod
    def parse_entry_todos(cls, entry):
        """
        :type entry: Entry.Entry
        :rtype: list[Todo]
        """
        fulltext = entry.get_fulltext(lower=False)
        todos_matches = [m.group('all') for m in re.finditer(any_todos_regex, fulltext)]
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
