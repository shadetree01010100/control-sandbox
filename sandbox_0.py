import time
import pygame
from colors import *
from controller_0 import Controller
from driver_0 import Driver


class Sandbox:

    WINDOW_TITLE = 'control sandbox'
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT= 600
    FONT_SIZE = 24
    X_SCALE = 10
    HISTOGRAM_SIZE = WINDOW_WIDTH // X_SCALE
    STEP_INTERVAL = 0.1  # seconds

    def __init__(self, controller, driver):
        self.driver = driver()
        self.controller = controller(self.driver)
        self.set_point = self.WINDOW_HEIGHT // 2
        self.set_points = []
        self.process = 0.0
        self.process_values = []
        self.control_values = []
        self.running = False
        self.lmb_state = False
        self.rmb_state = False

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(self.WINDOW_TITLE)
        self.surface = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.font = pygame.font.Font(None, self.FONT_SIZE)

    def run(self):
        self.running = True
        while self.running:
            self._handle_user_input()
            self.process, control_value = self.controller.step(
                self.process, self.set_point)

            # scale control_value to fit window
            center = self.WINDOW_HEIGHT // 2
            scaled_control_value = center * control_value + (center - 1)

            # update historgram series
            self.control_values = self.control_values[-self.HISTOGRAM_SIZE:]
            self.process_values = self.process_values[-self.HISTOGRAM_SIZE:]
            self.set_points = self.set_points[-self.HISTOGRAM_SIZE:]
            self.process_values.append(self.process)
            self.set_points.append(self.set_point)
            self.control_values.append(scaled_control_value)

            self._draw_sandbox(control_value)
            time.sleep(self.STEP_INTERVAL)

        # user exit
        pygame.display.quit()

    def _draw_line(self, start, stop, color=WHITE, width=3):
        # Y axis is upside down
        start = (start[0], (self.WINDOW_HEIGHT - 1) - start[1])
        stop = (stop[0], (self.WINDOW_HEIGHT - 1) - stop[1])
        pygame.draw.line(self.surface, color, start, stop, width)

    def _draw_sandbox(self, control_value):
        self.surface.fill(D_GRAY)
        self._draw_text(
            'process: {}'.format(round(self.process, 1)), 1, color=WHITE)
        self._draw_text(
            'set point: {}'.format(self.set_point), 2, color=RED)
        self._draw_text(
            'control: {}'.format(round(control_value, 3)), 4, color=GREEN)
        for r in range(self.HISTOGRAM_SIZE):
            if r == 0:
                continue
            try:
                self._draw_line(
                    ((r - 1) * self.X_SCALE, self.process_values[r - 1]),
                    (r * self.X_SCALE, self.process_values[r]))
                self._draw_line(
                    ((r - 1) * self.X_SCALE, self.set_points[r - 1]),
                    (r * self.X_SCALE, self.set_points[r]),
                    color=RED)
                self._draw_line(
                    ((r - 1) * self.X_SCALE, self.control_values[r - 1]),
                    (r * self.X_SCALE, self.control_values[r]),
                    color=GREEN)
            except IndexError:
                # fewer then HISTOGRAM_SIZE points are buffered so far
                break
        pygame.display.update()

    def _draw_text(self, text, line_num=0, coords=(0, 0), color=WHITE):
        if line_num:
            coords = (2, (line_num - 1) * self.FONT_SIZE // 2 + line_num * 2)
        antialias = True
        text = self.font.render(text, antialias, color)
        self.surface.blit(text, coords)

    def _handle_user_input(self):
        for event in pygame.event.get():
                lmb, mmb, rmb = pygame.mouse.get_pressed()
                mx, my = pygame.mouse.get_pos()
                # Y axis is upside down
                my = (self.WINDOW_HEIGHT - 1) - my

                # left mouse, change set_point
                if lmb:
                    if not self.lmb_state:  # do a thing on click
                        self.lmb_state = my
                        new_set_point = self.set_point
                    delta = my - self.lmb_state
                    new_set_point = self.set_point + delta
                    # clamp range
                    new_set_point = min(new_set_point, self.WINDOW_HEIGHT - 1)
                    new_set_point = max(new_set_point, 0)
                    self.set_point = new_set_point
                    # set state
                    self.lmb_state = my
                if not lmb:
                    if self.lmb_state:  # do a thing on release
                        self.lmb_state = False

                # right mouse, directly change process
                if rmb:
                    if not self.rmb_state:  # do a thing on click
                        self.rmb_state = my
                        new_process = self.process
                    delta = my - self.rmb_state
                    new_process = self.process + delta
                    self.process = new_process
                    # clamp range
                    self.process = min(self.process, self.WINDOW_HEIGHT - 1)
                    self.process = max(self.process, 0)
                    # set state
                    self.rmb_state = my
                if not rmb:
                    if self.rmb_state:  # do a thing on release
                        self.rmb_state = False

                # check for exit commands
                # any key, ctrl-C, or close pygame window
                if event.type in [pygame.QUIT, pygame.KEYDOWN]:
                    self.running = False
                    break

if __name__ == '__main__':
    s = Sandbox(Controller, Driver)
    s.run()
