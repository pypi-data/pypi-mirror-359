from schore.schedule.abstract import ActivityT, Resource


class Machine(Resource[ActivityT]):
    def __init__(self, name: str) -> None:
        """Initialize a Machine.

        Args:
            name (str): The name of the machine.
        """
        super().__init__()
        self._name: str = name
        """The name of the machine."""

    @property
    def name(self) -> str:
        """Returns the name of the machine."""
        return self._name
