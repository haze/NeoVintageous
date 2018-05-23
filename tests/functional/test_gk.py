# Copyright (C) 2018 The NeoVintageous Team (NeoVintageous).
#
# This file is part of NeoVintageous.
#
# NeoVintageous is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NeoVintageous is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NeoVintageous.  If not, see <https://www.gnu.org/licenses/>.

from NeoVintageous.tests import unittest


class Test_gk(unittest.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.settings().set('word_wrap', True)
        self.settings().set('wrap_width', 4)

    def test_gk(self):
        self.eq('123\n4|56\nx\n', 'gk', '1|23\n456\nx\n')
        self.eq('1234|56\nx\n', 'gk', '1|23456\nx\n')

    def test_l_gk(self):
        self.eq('123\n|456\n|x', 'l_gk', '|123\n456\n|x')
        self.eq('x\n123456\n|123456\n|y', 'l_gk', 'x\n|123456\n123456\n|y')