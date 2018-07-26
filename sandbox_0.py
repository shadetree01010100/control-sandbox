import time
import pygame
from colors import *
from driver_0 import Driver


WINDOW_TITLE = 'control sandbox'
WINDOW_WIDTH = 1200
WINDOW_HEIGHT= 600
FONT_SIZE = 24
X_SCALE = 10
HISTOGRAM_SIZE = WINDOW_WIDTH // X_SCALE + 1
STEP_INTERVAL = 0.1  # seconds

pygame.init()
pygame.font.init()
surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
font = pygame.font.Font(None, FONT_SIZE)

def draw_line(start, stop, color=WHITE, width=3):
    # Y axis is upside down
    start = (start[0], (WINDOW_HEIGHT - 1) - start[1])
    stop = (stop[0], (WINDOW_HEIGHT - 1) - stop[1])
    pygame.draw.line(surface, color, start, stop, width)

def draw_text(text, line_num=0, coords=(0, 0), color=WHITE):
    if line_num:
        coords = (2, (line_num - 1) * FONT_SIZE // 2 + line_num * 2)
    antialias = True
    text = font.render(text, antialias, color)
    surface.blit(text, coords)

running = True
lmb_state = False
rmb_state = False
set_point = WINDOW_HEIGHT // 2
set_points = []
process = 0.0
process_values = []
control_values = []
while running:
    for event in pygame.event.get():
        lmb, mmb, rmb = pygame.mouse.get_pressed()
        mx, my = pygame.mouse.get_pos()
        # Y axis is upside down
        my = (WINDOW_HEIGHT - 1) - my

        # left mouse, change set_point
        if lmb:
            if not lmb_state:  # do a thing on click
                lmb_state = my
                new_set_point = set_point
            delta = my - lmb_state
            new_set_point = set_point + delta
            set_point = new_set_point
            # clamp range
            set_point = min(set_point, WINDOW_HEIGHT - 1)
            set_point = max(set_point, 0)
            # set state
            lmb_state = my
        if not lmb:
            if lmb_state:  # do a thing on release
                lmb_state = False

        # right mouse, directly change process
        if rmb:
            if not rmb_state:  # do a thing on click
                rmb_state = my
                new_process = process
            delta = my - rmb_state
            new_process = process + delta
            process = new_process
            # clamp range
            process = min(process, WINDOW_HEIGHT - 1)
            process = max(process, 0)
            # set state
            rmb_state = my
        if not rmb:
            if rmb_state:  # do a thing on release
                rmb_state = False

        # check for exit commands
        # any key, ctrl-C, or close pygame window
        if event.type in [pygame.QUIT, pygame.KEYDOWN]:
            running = False
            break

    # track stuff
    process_values.append(process)
    process_values = process_values[-HISTOGRAM_SIZE:]
    set_points.append(set_point)
    set_points = set_points[-HISTOGRAM_SIZE:]

    # controller
    # outputs to driver dependent on error
    PROGRAM_GAIN = 0.006
    error = set_point - process
    control = error * PROGRAM_GAIN
    # clamp
    control = min(control, 1)
    control = max(control, -1)
    # scale
    control_value = WINDOW_HEIGHT // 2 * control + (WINDOW_HEIGHT // 2 - 1)
    control_values.append(control_value)
    control_values = control_values[-HISTOGRAM_SIZE:]

    # draw this sumbitch
    surface.fill(D_GRAY)
    draw_text('process: {}'.format(round(process, 1)), 1, color=WHITE)
    draw_text('set point: {}'.format(set_point), 2, color=RED)
    for r in range(HISTOGRAM_SIZE):
        if r == 0:
            continue
        try:
            draw_line(
                ((r - 1) * X_SCALE, process_values[r - 1]),
                (r * X_SCALE, process_values[r]))
            draw_line(
                ((r - 1) * X_SCALE, set_points[r - 1]),
                (r * X_SCALE, set_points[r]),
                color=RED)
            draw_line(
                ((r - 1) * X_SCALE, control_values[r - 1]),
                (r * X_SCALE, control_values[r]),
                color=GREEN)
        except:
            break

    # driver
    # takes input from -1 to 1, where 0 = no change
    # affects process at some rate of change
    MAX_ROC = 50  # per step
    step = control * MAX_ROC
    process += step
    draw_text('control: {}'.format(round(control, 3)), 4, color=GREEN)
    # process decay
    DECAY = 0.0  # per step
    process += DECAY
    process = round(process, 1)

    pygame.display.update()
    time.sleep(STEP_INTERVAL)

pygame.display.quit()
