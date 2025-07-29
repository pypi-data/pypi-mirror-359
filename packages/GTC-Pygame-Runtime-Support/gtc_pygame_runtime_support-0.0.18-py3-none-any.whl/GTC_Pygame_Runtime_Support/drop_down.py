import pygame
from pygame.draw_py import clip_line
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(2)

from GTC_Pygame_Runtime_Support.basic_class import *
from GTC_Pygame_Runtime_Support.button import SimpleButtonWithImage, FeedbackButton
from GTC_Pygame_Runtime_Support.page import PlainPage
from GTC_Pygame_Runtime_Support.slider import VerticalSlideBar
from GTC_Pygame_Runtime_Support.supported_types import *
from typing import Union


class SimpleDropDown(BasicDropDown):
    def __init__(self, size, pos, screen, font_type: str = 'SimHei', font_size: Union[str, int] = 'auto', show_amount=5, click_index=0):
        super().__init__(size, pos, screen)
        self._click_index = click_index
        self.buttons = []
        self.show_amount = show_amount
        self.page = None
        self.font_size: int
        self.slider = None
        if font_size == 'auto':
            self.font_size = size[1] - 4
        else:
            self.font_size = font_size
        self.text_pos = (size[0] // 2, size[1] // 2)
        self.font_type = font_type
        self.button = FeedbackButton(self._size, self._pos, '<无>', self.font_size, screen, bg_color=(255, 255, 255), text_color=(0, 0, 0),
                                     border_color=(255, 255, 255))
        self.selecting = 0

    def operate(self, mouse_pos, mouse_press):
        if mouse_press[self._click_index] and (not self.page.in_area(mouse_pos) and not self.page.sliding) and not self.button.in_area(
                mouse_pos) and (self.slider is None or (not self.slider.in_area(mouse_pos) and (not self.slider.sliding))):
            self.state = 'up'
        if self.state == 'down':
            if self.last_state == 'up':
                self.buttons.clear()
                i = 0
                self.page = PlainPage([self._size[0], int(self._size[1] * min(len(self.items), self.show_amount + 0.5))],
                                      [self._size[0], self._size[1] * len(self.items)], [self._pos[0], self._pos[1] + self._size[1]], self._screen,
                                      acc=1.2, wheel_support=False)
                self.page.surface.fill((0, 0, 0, 0))
                self.page.set_as_background()
                if len(self.items) > self.show_amount:
                    self.slider = VerticalSlideBar((self._size[0] // 10, self.page.size[1]),
                                                   (self._pos[0] + self._size[0], self._pos[1] + self._size[1]), self._screen,
                                                   8)  # self.slider.set_movable_width((self.page.size[1] ** 2) / self.page.real_size[1])
                else:
                    self.slider = None
                for item in self.items:
                    item: str
                    self.buttons.append(SimpleButtonWithImage([0, self._size[1] * i], self.page.surface, self._size,
                                                              text=(item, self.text_pos, self.font_size, (0, 0, 0)), font=self.font_type,
                                                              border_radius=0, border_width=1))
                    self.page.add_button_trusteeship(self.buttons[-1])
                    i += 1
                self.page.pos_y = 2 * len(self.items) * self._size[1]  # print(self.page.pos_y)
            # virtual_pos = [mouse_pos[0] - self._pos[0], mouse_pos[1] - self._pos[1] - self._size[1]]
            # print(virtual_pos)
            self.page.operate(mouse_pos, mouse_press)
            if self.slider is not None:
                self.slider.operate(mouse_pos, mouse_press)
                if not self.slider.sliding:
                    self.slider.slide_pos = -(self.page.pos_y + self.page.delta) / (self.page.real_size[1] - self.page.size[1]) * (
                                self.slider.slide_range[1] - self.slider.slide_range[0]) + self.slider.slide_range[0]
                else:
                    self.page.delta = 0
                    self.page.pos_y = -self.slider.percent * (self.page.real_size[1] - self.page.size[1])
            i = 1
            self.last_state = self.state
            self.button.operate(mouse_pos, mouse_press)
            if self.button.on_click:
                self.state = 'down' if self.state == 'up' else 'up'
            else:
                for butt in self.buttons:
                    butt: SimpleButtonWithImage
                    if butt.on_click:
                        self.selecting = i
                        self.button.change_text(self.items[i - 1])
                        print(self.items[i - 1])
                    i += 1
        else:
            self.last_state = self.state
            self.button.operate(mouse_pos, mouse_press)
            if self.button.on_click:
                self.state = 'down' if self.state == 'up' else 'up'


if __name__ == '__main__':
    pygame.init()
    sc = pygame.display.set_mode((800, 600))
    sdd = SimpleDropDown([200, 80], [150, 50], sc)
    sdd.items = ['ma', 'quan', 'yuan', 'da', 'sha', 'bi', 'bi', 'bi']
    sdd.state = 'down'
    clock = pygame.time.Clock()
    while True:
        sc.fill((30, 200, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        sdd.operate(pygame.mouse.get_pos(), pygame.mouse.get_pressed(3))
        clock.tick(60)
        pygame.display.flip()
