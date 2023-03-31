from Errors.runtime_error import Runtime_error

class PoxReturn(Runtime_error):
    def __init__(self, value) -> None:
        self.value = value
