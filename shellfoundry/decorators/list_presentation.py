#!/usr/bin/python
# -*- coding: utf-8 -*-


import click
import json

from os import linesep
from terminaltables import AsciiTable
from textwrap import wrap
from functools import wraps


def echo_list(func):
    @wraps(func)
    def wrapper(**kwargs):
        templates = func(**kwargs)
        template_rows = [['Template Name', 'CloudShell Ver.', 'Description']]
        for template in templates.values():
            cs_ver_txt = str(template.min_cs_ver) + " and up"
            template_rows.append(
                [template.name, cs_ver_txt,
                 template.description])  # description is later wrapped based on the size of the console

        table = AsciiTable(template_rows)
        table.outer_border = False
        table.inner_column_border = False
        max_width = table.column_max_width(2)

        if max_width <= 0:  # verify that the console window is not too small, and if so skip the wrapping logic
            click.echo(table.table)
            return

        row = 1
        for template in templates.values():
            wrapped_string = linesep.join(wrap(template.description, max_width))
            table.table_data[row][2] = wrapped_string
            row += 1

        output = table.table
        click.echo(output)

        # if self.show_info_msg:
        #     click.echo('''
        # As of CloudShell 8.0, CloudShell uses 2nd generation shells, to view the list of 1st generation shells use: shellfoundry list --gen1.
        # For more information, please visit our devguide: https://qualisystems.github.io/devguide/''')
    return wrapper


def to_json(func):
    @wraps(func)
    def wrapper(**kwargs):
        templates = func(**kwargs)
        template_list = []
        for template in templates.values():
            template = template[0]
            template_list.append({"name": template.name,
                                  # "min_cs_version": template.min_cs_ver,
                                  "description": template.description})

        return json.dumps(template_list)
    return wrapper
