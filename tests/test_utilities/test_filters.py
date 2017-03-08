import unittest

from shellfoundry.utilities import GEN_ONE, GEN_TWO, LAYER_ONE, NO_FILTER
from shellfoundry.utilities.filters import *


class TestFilters(unittest.TestCase):
    def test_no_filter_returns_true(self):
        # Act
        nf = NoFilter()

        # Assert
        self.assertTrue(nf.filter('gen1/template'))
        self.assertTrue(nf.filter('gen2/template'))
        self.assertTrue(nf.filter('layer-1-switch'))

    def test_gen1_filter_returns_true_for_gen1_only(self):
        # Act
        gf = GenOneFilter()

        # Assert
        self.assertTrue(gf.filter('gen1/template'))
        self.assertFalse(gf.filter('gen2/template'))
        self.assertFalse(gf.filter('layer-1-switch'))

    def test_gen2_filter_returns_true_for_gen2_only(self):
        # Act
        gf = GenTwoFilter()

        # Assert
        self.assertFalse(gf.filter('gen1/template'))
        self.assertTrue(gf.filter('gen2/template'))
        self.assertFalse(gf.filter('layer-1-switch'))

    def test_layer1_filter_returns_true_for_layer1_only(self):
        # Act
        lf = LayerOneFilter()

        # Assert
        self.assertFalse(lf.filter('gen1/template'))
        self.assertFalse(lf.filter('gen2/template'))
        self.assertTrue(lf.filter('layer-1-switch'))

    def test_composite_filter_return_true_if_template_type_is_gen1_match_template_name(self):
        # Act
        cf = CompositeFilter(GEN_ONE)

        # Assert
        self.assertTrue(cf.filter('gen1/template'))
        self.assertFalse(cf.filter('gen2/template'))
        self.assertFalse(cf.filter('layer-1-switch'))

    def test_composite_filter_return_true_if_template_type_is_gen2_match_template_name(self):
        # Act
        cf = CompositeFilter(GEN_TWO)

        # Assert
        self.assertFalse(cf.filter('gen1/template'))
        self.assertTrue(cf.filter('gen2/template'))
        self.assertFalse(cf.filter('layer-1-switch'))

    def test_composite_filter_return_true_if_template_type_is_layer1_match_template_name(self):
        # Act
        cf = CompositeFilter(LAYER_ONE)

        # Assert
        self.assertFalse(cf.filter('gen1/template'))
        self.assertFalse(cf.filter('gen2/template'))
        self.assertTrue(cf.filter('layer-1-switch'))

    def test_composite_filter_returns_true_for_all_by_default(self):
        # Act
        cf = CompositeFilter()

        # Assert
        self.assertTrue(cf.filter('gen1/template'))
        self.assertTrue(cf.filter('gen2/template'))
        self.assertTrue(cf.filter('layer-1-switch'))
