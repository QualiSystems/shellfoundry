from __future__ import annotations

import unittest

from shellfoundry.utilities.filters import (
    GEN_ONE,
    GEN_TWO,
    LAYER_ONE,
    CompositeFilter,
    GenOneFilter,
    GenTwoFilter,
    LayerOneFilter,
    NoFilter,
)


class TestFilters(unittest.TestCase):
    def test_no_filter_returns_true(self):
        # Act
        nf = NoFilter()

        # Assert
        self.assertTrue(nf.passes("gen1/template"))
        self.assertTrue(nf.passes("gen2/template"))
        self.assertTrue(nf.passes("layer-1-switch"))

    def test_gen1_filter_returns_true_for_gen1_only(self):
        # Act
        gf = GenOneFilter()

        # Assert
        self.assertTrue(gf.passes("gen1/template"))
        self.assertFalse(gf.passes("gen2/template"))
        self.assertFalse(gf.passes("layer-1-switch"))

    def test_gen2_filter_returns_true_for_gen2_only(self):
        # Act
        gf = GenTwoFilter()

        # Assert
        self.assertFalse(gf.passes("gen1/template"))
        self.assertTrue(gf.passes("gen2/template"))
        self.assertFalse(gf.passes("layer-1-switch"))

    def test_layer1_filter_returns_true_for_layer1_only(self):
        # Act
        lf = LayerOneFilter()

        # Assert
        self.assertFalse(lf.passes("gen1/template"))
        self.assertFalse(lf.passes("gen2/template"))
        self.assertTrue(lf.passes("layer-1-switch"))

    def test_composite_filter_return_true_if_template_type_is_gen1_match_template_name(
        self,
    ):
        # Act
        cf = CompositeFilter(GEN_ONE)

        # Assert
        self.assertTrue(cf.passes("gen1/template"))
        self.assertFalse(cf.passes("gen2/template"))
        self.assertFalse(cf.passes("layer-1-switch"))

    def test_composite_filter_return_true_if_template_type_is_gen2_match_template_name(
        self,
    ):
        # Act
        cf = CompositeFilter(GEN_TWO)

        # Assert
        self.assertFalse(cf.passes("gen1/template"))
        self.assertTrue(cf.passes("gen2/template"))
        self.assertFalse(cf.passes("layer-1-switch"))

    def test_composite_filter_return_true_if_template_type_is_layer1_match_template_name(  # noqa: E501
        self,
    ):
        # Act
        cf = CompositeFilter(LAYER_ONE)

        # Assert
        self.assertFalse(cf.passes("gen1/template"))
        self.assertFalse(cf.passes("gen2/template"))
        self.assertTrue(cf.passes("layer-1-switch"))

    def test_composite_filter_returns_true_for_all_by_default(self):
        # Act
        cf = CompositeFilter()

        # Assert
        self.assertTrue(cf.passes("gen1/template"))
        self.assertTrue(cf.passes("gen2/template"))
        self.assertTrue(cf.passes("layer-1-switch"))
