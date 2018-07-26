class Controller:

    PROGRAM_GAIN = 0.006

    def __init__(self, driver):
        self.driver = driver

    def step(self, process, set_point):
        error = set_point - process
        control_value = error * self.PROGRAM_GAIN
        # clamp
        control_value = min(control_value, 1)
        control_value = max(control_value, -1)
        # scale
        process = self.driver.set(process, control_value)
        return process, control_value
