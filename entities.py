from __future__ import annotations
from typing import List
from sprites import PersonSprite, ElevatorSprite


class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    Remember to add additional documentation to this class docstring
    as you add new attributes (and representation invariants).

    === Attributes ===
    passengers: A list of the people currently on this elevator
    current_floor: The floor the elevator is on.
    max_capacity: maximum number of people that will fit in the elevator.

    === Representation invariants ===
    len(self.passengers) <= self.max_capacity
    1 <= self.current_floor
    """

    passengers: List[Person]
    current_floor: int
    max_capacity: int

    def __init__(self, capacity: int) -> None:
        """Initializes an elevator."""
        ElevatorSprite.__init__(self)
        self.passengers = []
        self.current_floor = 1
        self.max_capacity = capacity

    def fullness(self) -> float:
        """Return the fraction that this elevator is filled.

        The value returned should be a float between 0.0 (completely empty) and
        1.0 (completely full).
        """
        return len(self.passengers) / self.max_capacity

    def is_empty(self) -> bool:
        """Return whether the elevator is empty. """
        return len(self.passengers) == 0

    def is_full(self) -> bool:
        """Return whether the elevator is at full capacity. """
        return len(self.passengers) == self.max_capacity

    def get_direction(self, target: int) -> int:
        """Returns an int the elevator should go to get to a target floor."""
        if target > self.current_floor:
            return 1
        if target < self.current_floor:
            return -1
        else:
            return 0

    def move(self, direction: int) -> None:
        """Move the elevator given an int for direction.

        Preconditions:
            direction is either -1, 0, 1
        """
        self.current_floor += direction

    def load(self, passenger: Person) -> None:
        """Load a passenger into the elevator."""
        self.passengers.append(passenger)

    def unload(self, passenger: Person) -> None:
        """Unload a passenger from the elevator."""
        self.passengers.remove(passenger)


class Person(PersonSprite):
    """A person in the elevator simulation.

    === Attributes ===
    start: the floor this person started on
    target: the floor this person wants to go to
    wait_time: the number of rounds this person has been waiting

    === Representation invariants ===
    self.start >= 1
    self.target >= 1
    self.wait_time >= 0
    self.start != self.target
    """
    start: int
    target: int
    wait_time: int

    def __init__(self, start: int, target: int) -> None:
        """Initializes a passenger. """
        self.wait_time = 0
        PersonSprite.__init__(self)
        self.start = start
        self.target = target

    def get_anger_level(self) -> int:
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
            - Level 0: waiting 0-2 rounds
            - Level 1: waiting 3-4 rounds
            - Level 2: waiting 5-6 rounds
            - Level 3: waiting 7-8 rounds
            - Level 4: waiting >= 9 rounds
        """
        if self.wait_time <= 2:
            return 0
        if self.wait_time <= 4:
            return 1
        if self.wait_time <= 6:
            return 2
        if self.wait_time <= 8:
            return 3
        else:
            return 4


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['sprites'],
        'max-nested-blocks': 4,
        'disable': ['R0201'],
        'max-attributes': 12
    })
