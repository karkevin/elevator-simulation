from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    stats: a dictionary storing data to calculate statistics at the end of
             the simulation.
    """

    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    stats: Dict[str, Any]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.arrival_generator = config["arrival_generator"]

        self.elevators = []
        for dummy in range(config["num_elevators"]):
            self.elevators += [Elevator(config["elevator_capacity"])]

        self.moving_algorithm = config["moving_algorithm"]

        self.num_floors = config.get('num_floors')

        self.waiting = {i: [] for i in range(1, config["num_floors"] + 1)}

        self.stats = {
            "num_iterations": None,
            "total_people": 0,
            "total_completed": 0,
            "times": []
        }

        self.visualizer = Visualizer(self.elevators,
                                     self.num_floors,
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        self.stats["num_iterations"] = num_rounds

        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Stage 5: increase wait time for people still waiting
            self._increase_all_wait_times()

            # Pause for 1 second
            self.visualizer.wait(0)

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        arrivals = self.arrival_generator.generate(round_num)
        for floor in arrivals.keys():
            for person in arrivals[floor]:
                self.stats["total_people"] += 1
                self.waiting[floor].append(person)
        self.visualizer.show_arrivals(arrivals)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            for passenger in reversed(elevator.passengers):
                if passenger.target == elevator.current_floor:
                    self.stats["total_completed"] += 1
                    self.stats["times"].append(passenger.wait_time)
                    elevator.unload(passenger)
                    self.visualizer.show_disembarking(passenger, elevator)

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for elevator in self.elevators:
            floor = elevator.current_floor
            people_on_floor = self.waiting[floor]
            while not elevator.is_full() and len(people_on_floor) != 0:
                passenger = people_on_floor.pop(0)
                elevator.load(passenger)
                self.visualizer.show_boarding(passenger, elevator)

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        directions = self.moving_algorithm.move_elevators(
            self.elevators, self.waiting, self.num_floors)
        for elevator, direction in zip(self.elevators, directions):
            if direction == Direction.UP:
                elevator.move(1)
            elif direction == Direction.DOWN:
                elevator.move(-1)

        self.visualizer.show_elevator_moves(self.elevators, directions)

    def _increase_all_wait_times(self) -> None:
        """Increases all the wait times for all the people currently active."""
        for floor in self.waiting.keys():
            for passenger in self.waiting[floor]:
                passenger.wait_time += 1
        for elevator in self.elevators:
            for passenger in elevator.passengers:
                passenger.wait_time += 1

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        stats = self.stats
        return {
            'num_iterations': stats["num_iterations"],
            'total_people': stats["total_people"],
            'people_completed': stats["total_completed"],
            'max_time': max(stats["times"]) if stats["times"] else -1,
            'min_time': min(stats["times"]) if stats["times"] else -1,
            'avg_time': int(sum(stats["times"]) / len(stats["times"]))
                        if stats["times"] else -1
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics.

    Precondition:
        config.'num_floors' >= 2
    """
    config = {
        'num_floors': 100,
        'num_elevators': 6,
        'elevator_capacity': 4,
        'num_people_per_round': None,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.FileArrivals(100, "csv_file.csv"),
        'moving_algorithm': algorithms.ShortSighted(),
        'visualize': False
    }

    sim = Simulation(config)
    stats = sim.run(5000)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4
    })
