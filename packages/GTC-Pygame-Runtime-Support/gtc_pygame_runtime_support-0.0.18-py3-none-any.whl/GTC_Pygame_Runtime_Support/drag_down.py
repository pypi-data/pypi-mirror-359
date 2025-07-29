import pygame
from future.standard_library import import_

from GTC_Pygame_Runtime_Support.basic_class import *
from GTC_Pygame_Runtime_Support.button import SimpleButtonWithImage
from GTC_Pygame_Runtime_Support.supported_types import *

class SimpleDropDown(BasicDropDown):
    def __init__(self, pos, size, screen, column_width, column_height, font_type, font_size=14, click_index=0):
        super().__init__(pos, size, screen)
        self._click_index = click_index
        self.buttons = []

    def operate(self, mouse_pos, mouse_press):
        if self.state == 'down':
            if self.last_state == 'up':
                self.buttons.clear()
                i = 0
                for item in self.items:
                    self.buttons.append(SimpleButtonWithImage())
                    i += 1
