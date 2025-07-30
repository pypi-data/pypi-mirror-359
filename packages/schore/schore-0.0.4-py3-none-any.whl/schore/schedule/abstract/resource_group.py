from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .resource import ResourceT


class ResourceGroup(Generic[ResourceT], ABC):
    """
    Abstract base class representing a group of resources in a scheduling system.

    A ResourceGroup is a container for multiple resources (such as machines, workers, etc.)
    that can be managed and scheduled together. Subclasses define whether the group operates
    in parallel (as in a parallel machine environment) or sequentially (as in a flow line).
    The group is responsible for managing the collection of resources and providing
    information such as the group name and makespan.

    Subclasses must implement:
        - The `name` property (str)
        - The `resources` property (list[ResourceT])
        - The `add_resource(res: ResourceT)` method

    Example:
        class MachineGroup(ResourceGroup[Machine]):
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

    # Abstract getters

    @property
    @abstractmethod
    def name(self) -> str:
        """The name or unique identifier of the resource group."""
        ...

    @property
    @abstractmethod
    def resources(self) -> list[ResourceT]:
        """
        The list of resources contained in this group.

        Returns:
            list[ResourceT]: All resources currently managed by this group.
        """
        ...

    # Abstract setters

    @abstractmethod
    def add_resource(self, res: ResourceT) -> None:
        """Add a resource to the group.

        Args:
            res (ResourceT): The resource to add.

        Side effects:
            - Modifies the internal resource list.
        """
        ...

    # Getters

    @property
    def makespan(self) -> int:
        """
        Returns:
            int: The largest makespan value among the group's resources,
                or 0 if the group is empty.
        """
        return max((res.makespan for res in self.resources), default=0)


ResourceGroupT = TypeVar("ResourceGroupT", bound=ResourceGroup)
"""
Type variable for generics involving ResourceGroup subclasses.

Ensures type safety for functions or classes operating
on any subclass of ResourceGroup.
"""
