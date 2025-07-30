from abc import ABC
from typing import TypeVar

from .resource import ResourceT
from .resource_group import ResourceGroup


class ParallelResourceGroup(ResourceGroup[ResourceT], ABC):
    """
    Abstract base class representing a group of resources in parallel.


    This class defines the common interface for a group of resources that operate in parallel,
    such as parallel machines, teams of workers, or any entities that can process activities
    independently.
    It is intended to be subclassed with concrete implementations
    providing the actual resource list and group name.

    Subclasses must implement:
        - The `name` property (str)
        - The `resources` property (list[ResourceT])
        - The `add_resource(res: ResourceT)` method

    Example:
        class MachineGroup(ParallelResourceGroup[Machine]):
            def __init__(self, name):
                self._name = name
                self._resources = []

            @property
            def name(self):
                return self._name

            @property
            def resources(self):
                return self._resources

            def add_resource(self, res: Machine) -> None:
                self._resources.append(res)
    """

    # Getters

    def get_earliest_start_resource_name_and_time(
        self, duration: int, release_t: int = 0
    ) -> tuple[str, int]:
        """
        Find the resource that can start a new activity at the earliest possible time.

        This method examines all resources in the group and determines which resource
        can schedule a new activity (of given `duration`) at the earliest start time
        (not before `release_t`). If multiple resources can start at the same earliest time,
        the first such resource in the list is selected.

        Args:
            duration (int): Duration of the new activity (must be positive).
            release_t (int, optional): Earliest time the activity may start. Defaults to 0.

        Returns:
            tuple[str, int]: A tuple of (resource name, earliest feasible start time).

        Raises:
            ValueError: If `duration` is not positive.
            ValueError: If no resource is available to start the activity.

        Example:
            >>> group.get_earliest_start_resource_name_and_time(5, release_t=10)
            ('ResourceA', 12)

        Notes:
            - All contained resources must implement `get_earliest_start_time` and `name`.
            - This method does not modify any internal state.
            - In case of a tie, the first matching resource is chosen.
        """
        if duration <= 0:
            raise ValueError("Duration must be greater than 0")

        earliest_start = float("inf")
        earliest_resource_name: str | None = None

        for res in self.resources:
            start_time = res.get_earliest_start_time(duration, release_t)
            if start_time < earliest_start:
                earliest_start = start_time
                earliest_resource_name = res.name

        if earliest_resource_name is not None:
            return earliest_resource_name, int(earliest_start)
        raise ValueError("No resource available to start the activity")


ParallelResourceGroupT = TypeVar("ParallelResourceGroupT", bound=ParallelResourceGroup)
"""
Type variable for generics involving ParallelResourceGroup subclasses.

Ensures type safety for functions or classes operating
on any subclass of ParallelResourceGroup.
"""
