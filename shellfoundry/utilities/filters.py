#!/usr/bin/python
# -*- coding: utf-8 -*-
from . import (
    GEN_ONE,
    GEN_ONE_FILTER,
    GEN_TWO,
    GEN_TWO_FILTER,
    LAYER_ONE,
    LAYER_ONE_FILTER,
    NO_FILTER,
)


class CompositeFilter(object):
    def __init__(self, template_type=None):
        self.template_type = template_type or NO_FILTER
        self.filters = {
            GEN_ONE: GenOneFilter,
            GEN_TWO: GenTwoFilter,
            LAYER_ONE: LayerOneFilter,
            NO_FILTER: NoFilter,
        }

    def filter(self, template_name):  # noqa: A003
        return self.filters.get(self.template_type, NoFilter)().filter(template_name)


class GenOneFilter(object):
    def filter(self, template_name):  # noqa: A003
        return GEN_ONE_FILTER in template_name


class GenTwoFilter(object):
    def filter(self, template_name):  # noqa: A003
        return GEN_TWO_FILTER in template_name


class LayerOneFilter(object):
    def filter(self, template_name):  # noqa: A003
        return LAYER_ONE_FILTER in template_name


class NoFilter(object):
    def filter(self, template_name):  # noqa: A003
        return True
