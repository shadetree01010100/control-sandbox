class Driver:

    MAX_ROC = 10  # per step

    def set(self, process, input):
        step = input * self.MAX_ROC
        process += step
        return int(process)
