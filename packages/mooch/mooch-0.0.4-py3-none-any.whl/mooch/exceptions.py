class RequirementError(Exception):
    def __init__(self, *args):  # noqa: ANN002
        super().__init__(*args)


class LocationError(Exception):
    def __init__(self, *args):  # noqa: ANN002
        super().__init__(*args)
