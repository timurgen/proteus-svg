from unittest import TestCase
import xml.etree.ElementTree as XMLParse
from proteus_lib import color_utils


class Test(TestCase):
    valid_object_white = XMLParse.Element('Presentation', attrib={'R': '1', 'G': '1', 'B': '1'})
    valid_object_black = XMLParse.Element('Presentation', attrib={'R': '0', 'G': '0', 'B': '0'})

    invalid_obj_1 = XMLParse.Element('NotPresentation')
    invalid_obj_2 = XMLParse.Element('Presentation')
    invalid_obj_3 = XMLParse.Element('Presentation', attrib={'R': '255', 'G': '255', 'B': '255'})

    def test_rgb_to_hex_string_must_pass_white(self):
        self.assertEqual(color_utils.rgb_to_hex_string(255, 255, 255), '#FFFFFF')

    def test_rgb_to_hex_string_must_pass_black(self):
        self.assertEqual(color_utils.rgb_to_hex_string(0, 0, 0), '#000000')

    def test_rgb_to_hex_string_must_fail_1(self):
        with self.assertRaises(ValueError):
            color_utils.rgb_to_hex_string(-1, -1, -1)

    def test_rgb_to_hex_string_must_fail_3(self):
        with self.assertRaises(ValueError):
            color_utils.rgb_to_hex_string(256, 256, 256)

    def test_compute_rgb_must_pass_white(self):
        self.assertEqual(color_utils.compute_rgb(1.0, 1.0, 1.0), (255, 255, 255))

    def test_compute_rgb_must_pass_black(self):
        self.assertEqual(color_utils.compute_rgb(0.0, 0.0, 0.0), (0, 0, 0))

    def test_fetch_color_from_presentation_must_pass_white(self):
        self.assertEqual(color_utils.fetch_color_from_presentation(self.valid_object_white), '#FFFFFF')

    def test_fetch_color_from_presentation_must_pass_black(self):
        self.assertEqual(color_utils.fetch_color_from_presentation(self.valid_object_black), '#000000')

    def test_fetch_color_from_presentation_must_fail_1(self):
        with self.assertRaises(ValueError):
            color_utils.fetch_color_from_presentation(self.invalid_obj_1)

    def test_fetch_color_from_presentation_must_fail_2(self):
        with self.assertRaises(KeyError):
            color_utils.fetch_color_from_presentation(self.invalid_obj_2)

    def test_fetch_color_from_presentation_must_fail_3(self):
        with self.assertRaises(ValueError):
            color_utils.fetch_color_from_presentation(self.invalid_obj_3)
