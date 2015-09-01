class AbsentYamlError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidConfig(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NonUserEditableError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
