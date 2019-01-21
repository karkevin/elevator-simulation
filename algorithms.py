import csv
from enum import Enum
import random
from typing import Dict, List, Optional, Tuple

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.
        """
        people_waiting = {}
        if self.num_people is None:
            return people_waiting
        info = []
        for dummy in range(self.num_people):
            info.append(tuple(random.sample(range(1, self.max_floor + 1), 2)))
        for start, target in info:
            if start in people_waiting:
                people_waiting[start].append(Person(start, target))
            else:
                people_waiting[start] = [Person(start, target)]

        return people_waiting


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    === Attributes ===
    _data_store: Stores all the info from the CSV file.
    """

    _data_store: Dict[int, List[Tuple[int, int]]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)
        self._data_store = {}

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                clean = [int(i) for i in line]
                self._data_store[clean[0]] = [(clean[i], clean[i + 1])
                                              for i in range(1, len(clean), 2)]

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.
        """
        people_waiting = {}
        if round_num not in self._data_store:
            return people_waiting
        info = self._data_store[round_num]
        for start, target in info:
            if start in people_waiting:
                people_waiting[start].append(Person(start, target))
            else:
                people_waiting[start] = [Person(start, target)]

        return people_waiting

###############################################################################
# Elevator moving algorithms
###############################################################################


class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError

    @staticmethod
    def _is_people_waiting(waiting: Dict[int, List[Person]]) -> bool:
        """Help function; checks if there are any people waiting on any
        of the floors.
        """
        for arr in waiting.values():
            if len(arr) != 0:
                return True
        return False

    @staticmethod
    def _options(value: int) -> Direction:
        """Helper function; returns a Direction object based on an integer."""
        options = {
            1: Direction.UP,
            0: Direction.STAY,
            -1: Direction.DOWN
        }
        return options[value]


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Moves elevators at random."""
        ret = []
        for elevator in elevators:
            if elevator.current_floor == 1:
                ret.append(self._options(random.randint(0, 1)))
            elif elevator.current_floor == max_floor:
                ret.append(self._options(random.randint(-1, 0)))
            else:
                ret.append(self._options(random.randint(-1, 1)))
        return ret


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Moves elevator in accordance with the push passenger algorithm."""
        direction_list = []
        people_waiting = self._is_people_waiting(waiting)

        lowest_floor = self._get_lowest_floor_with_people(waiting)

        for elevator in elevators:
            if elevator.is_empty():
                if people_waiting:
                    direction_list.append(
                        self._options(elevator.get_direction(lowest_floor)))
                else:
                    direction_list.append(self._options(0))
            else:
                target_floor = elevator.passengers[0].target
                direction_list.append(
                    self._options(elevator.get_direction(target_floor)))

        return direction_list

    @staticmethod
    def _get_lowest_floor_with_people(waiting: Dict[int, List[Person]]) -> int:
        """Returns the lowest floor with people waiting."""
        lowest_floor = max([*waiting])
        for floor in [*waiting]:
            if waiting[floor] != [] and floor < lowest_floor:
                lowest_floor = floor
        return lowest_floor


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Moves elevator in accordance with the short-sighted algorithm."""
        direction_list = []
        people_waiting = self._is_people_waiting(waiting)
        for elevator in elevators:
            current = elevator.current_floor
            if elevator.is_empty():
                if people_waiting:
                    closest = self._get_closest_waiting_floor(current, waiting)
                    direction_list.append(
                        self._options(elevator.get_direction(closest)))
                else:
                    direction_list.append(self._options(0))
            else:
                target = self._get_closest_target_floor(elevator)
                direction_list.append(
                    self._options(elevator.get_direction(target)))

        return direction_list

    @staticmethod
    def _get_closest_waiting_floor(current: int,
                                   waiting: Dict[int, List[Person]]) -> int:
        """Finds the closest floor with people waiting given the elevator's
        current floor.

        In the event of the two closest floors being equidistant, the lower
        floor is returned.
        """
        floors_with_waiting = []
        for floor in [*waiting]:
            if waiting[floor]:
                floors_with_waiting.append(floor)
        closest = floors_with_waiting[0]
        for floor in floors_with_waiting[1:]:
            if abs(floor - current) < abs(closest - current):
                closest = floor
            elif abs(floor - current) == abs(closest - current):
                closest = min(floor, closest)
        return closest

    @staticmethod
    def _get_closest_target_floor(elevator: Elevator) -> int:
        """Finds the closest target floor of the people in the elevator.

        In the event of the two closest floors being equidistant, the lower
        floor is returned.
        """
        current = elevator.current_floor
        target = elevator.passengers[0].target
        for passenger in elevator.passengers[1:]:
            passenger_floor = passenger.target
            if abs(passenger_floor - current) < abs(target - current):
                target = passenger_floor
            elif abs(passenger_floor - current) == abs(target - current):
                target = min(passenger_floor, target)
        return target


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201'],
        'max-attributes': 12
    })
