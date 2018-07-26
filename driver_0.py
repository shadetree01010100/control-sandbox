class Driver:

    MAX_ROC = 50  # per step

    def set(self, process, input):
        step = input * self.MAX_ROC
        process += step
        return process
