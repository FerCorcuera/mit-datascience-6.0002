"""Modern tests for MIT 6.0002 Fall 2016 Problem Set 3.

The original test runner depended on a CPython 3.5 ``test.pyc`` answer key and
APIs removed from modern Python. These tests are based on the public problem
set specification instead and do not contain a reference implementation.

Run every test:
    poetry run python -B ps3_tests_f16.py

Run one problem at a time:
    poetry run python -B ps3_tests_f16.py 1
    poetry run python -B ps3_tests_f16.py 2
    poetry run python -B ps3_tests_f16.py 3
    poetry run python -B ps3_tests_f16.py 4
    poetry run python -B ps3_tests_f16.py 5
"""

from __future__ import annotations

import random
import sys
import types
import unittest
from unittest import mock


def _install_optional_dependency_stubs() -> None:
    """Keep optional GUI and plotting dependencies out of unit tests."""

    visualizer = types.ModuleType("ps3_visualize")

    class RobotVisualization:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Visualization is disabled during automated tests")

    visualizer.RobotVisualization = RobotVisualization
    sys.modules["ps3_visualize"] = visualizer

    movement = types.ModuleType("ps3_verify_movement27")

    def test_robot_movement(*args, **kwargs):
        raise RuntimeError("Movement visualization is disabled during automated tests")

    movement.test_robot_movement = test_robot_movement
    sys.modules["ps3_verify_movement27"] = movement

    pylab = types.ModuleType("pylab")
    for function_name in ("plot", "title", "legend", "xlabel", "ylabel", "show"):
        setattr(pylab, function_name, lambda *args, **kwargs: None)
    sys.modules["pylab"] = pylab


_install_optional_dependency_stubs()

import ps3  # noqa: E402 -- imported after installing the GUI stubs


class Problem1PositionTests(unittest.TestCase):
    """Sanity checks for the provided Position implementation."""

    def test_cardinal_movements(self) -> None:
        origin = ps3.Position(1.0, 1.0)
        expected = {
            0: (1.0, 2.0),
            90: (2.0, 1.0),
            180: (1.0, 0.0),
            270: (0.0, 1.0),
        }

        for direction, coordinates in expected.items():
            with self.subTest(direction=direction):
                new_position = origin.get_new_position(direction, 1.0)
                self.assertAlmostEqual(new_position.get_x(), coordinates[0])
                self.assertAlmostEqual(new_position.get_y(), coordinates[1])


class Problem1RectangularRoomTests(unittest.TestCase):
    def test_initializes_every_tile_with_the_requested_dirt(self) -> None:
        room = ps3.RectangularRoom(3, 4, 2)
        for x in range(3):
            for y in range(4):
                with self.subTest(tile=(x, y)):
                    self.assertEqual(room.get_dirt_amount(x, y), 2)
                    self.assertFalse(room.is_tile_cleaned(x, y))

    def test_zero_dirt_tiles_start_clean(self) -> None:
        room = ps3.RectangularRoom(2, 3, 0)
        self.assertEqual(room.get_num_cleaned_tiles(), 6)
        for x in range(2):
            for y in range(3):
                self.assertTrue(room.is_tile_cleaned(x, y))

    def test_cleaning_uses_the_tile_below_the_float_position(self) -> None:
        room = ps3.RectangularRoom(3, 3, 2)
        room.clean_tile_at_position(ps3.Position(1.99, 2.01), 1)
        self.assertEqual(room.get_dirt_amount(1, 2), 1)

    def test_dirt_never_becomes_negative(self) -> None:
        room = ps3.RectangularRoom(2, 2, 2)
        room.clean_tile_at_position(ps3.Position(0.4, 1.7), 100)
        self.assertEqual(room.get_dirt_amount(0, 1), 0)
        self.assertTrue(room.is_tile_cleaned(0, 1))

    def test_negative_capacity_adds_dirt(self) -> None:
        room = ps3.RectangularRoom(1, 1, 0)
        room.clean_tile_at_position(ps3.Position(0.5, 0.5), -3)
        self.assertEqual(room.get_dirt_amount(0, 0), 3)
        self.assertFalse(room.is_tile_cleaned(0, 0))

    def test_clean_tile_count_tracks_distinct_fully_clean_tiles(self) -> None:
        room = ps3.RectangularRoom(2, 2, 2)
        room.clean_tile_at_position(ps3.Position(0.2, 0.2), 1)
        self.assertEqual(room.get_num_cleaned_tiles(), 0)
        room.clean_tile_at_position(ps3.Position(0.8, 0.8), 1)
        self.assertEqual(room.get_num_cleaned_tiles(), 1)
        room.clean_tile_at_position(ps3.Position(0.3, 0.4), 5)
        self.assertEqual(room.get_num_cleaned_tiles(), 1)

    def test_room_boundaries_are_lower_inclusive_upper_exclusive(self) -> None:
        room = ps3.RectangularRoom(3, 4, 1)
        cases = (
            (0.0, 0.0, True),
            (2.999, 3.999, True),
            (-0.001, 1.0, False),
            (1.0, -0.001, False),
            (3.0, 1.0, False),
            (1.0, 4.0, False),
        )
        for x, y, expected in cases:
            with self.subTest(position=(x, y)):
                self.assertIs(room.is_position_in_room(ps3.Position(x, y)), expected)

    def test_subclass_only_methods_remain_unimplemented(self) -> None:
        room = ps3.RectangularRoom(2, 2, 1)
        with self.assertRaises(NotImplementedError):
            room.get_num_tiles()
        with self.assertRaises(NotImplementedError):
            room.is_position_valid(ps3.Position(0.5, 0.5))
        with self.assertRaises(NotImplementedError):
            room.get_random_position()


class _MinimalRoom:
    """Small room double used to test Robot independently from Problem 2."""

    def get_random_position(self) -> ps3.Position:
        return ps3.Position(1.25, 2.5)

    def clean_tile_at_position(self, position, capacity) -> None:
        """Accept implementations that clean the robot's initial tile."""


class Problem1RobotTests(unittest.TestCase):
    def test_robot_initial_state_and_accessors(self) -> None:
        robot = ps3.Robot(_MinimalRoom(), 1.5, 2)
        position = robot.get_robot_position()
        self.assertIsInstance(position, ps3.Position)
        self.assertEqual((position.get_x(), position.get_y()), (1.25, 2.5))
        self.assertGreaterEqual(robot.get_robot_direction(), 0.0)
        self.assertLess(robot.get_robot_direction(), 360.0)

    def test_robot_position_and_direction_can_be_changed(self) -> None:
        robot = ps3.Robot(_MinimalRoom(), 1.0, 1)
        position = ps3.Position(0.25, 0.75)
        robot.set_robot_position(position)
        robot.set_robot_direction(123.5)
        self.assertIs(robot.get_robot_position(), position)
        self.assertEqual(robot.get_robot_direction(), 123.5)

    def test_base_robot_leaves_movement_to_subclasses(self) -> None:
        robot = ps3.Robot(_MinimalRoom(), 1.0, 1)
        with self.assertRaises(NotImplementedError):
            robot.update_position_and_clean()


class Problem2EmptyRoomTests(unittest.TestCase):
    def test_number_of_accessible_tiles(self) -> None:
        self.assertEqual(ps3.EmptyRoom(5, 7, 1).get_num_tiles(), 35)

    def test_position_validity_matches_room_boundaries(self) -> None:
        room = ps3.EmptyRoom(3, 4, 1)
        self.assertTrue(room.is_position_valid(ps3.Position(0.0, 0.0)))
        self.assertTrue(room.is_position_valid(ps3.Position(2.999, 3.999)))
        self.assertFalse(room.is_position_valid(ps3.Position(-0.01, 1.0)))
        self.assertFalse(room.is_position_valid(ps3.Position(3.0, 1.0)))

    def test_random_positions_are_position_objects_and_valid(self) -> None:
        room = ps3.EmptyRoom(5, 10, 1)
        random.seed(60002)
        for _ in range(250):
            position = room.get_random_position()
            self.assertIsInstance(position, ps3.Position)
            self.assertTrue(room.is_position_valid(position))


class Problem2FurnishedRoomTests(unittest.TestCase):
    @staticmethod
    def make_room() -> ps3.FurnishedRoom:
        room = ps3.FurnishedRoom(4, 3, 1)
        room.furniture_tiles = [(1, 1), (2, 1)]
        return room

    def test_tile_and_position_furniture_detection(self) -> None:
        room = self.make_room()
        self.assertTrue(room.is_tile_furnished(1, 1))
        self.assertTrue(room.is_position_furnished(ps3.Position(2.9, 1.1)))
        self.assertFalse(room.is_tile_furnished(0, 0))
        self.assertFalse(room.is_position_furnished(ps3.Position(0.9, 0.9)))

    def test_valid_position_must_be_inside_and_unfurnished(self) -> None:
        room = self.make_room()
        self.assertTrue(room.is_position_valid(ps3.Position(0.5, 0.5)))
        self.assertFalse(room.is_position_valid(ps3.Position(1.5, 1.5)))
        self.assertFalse(room.is_position_valid(ps3.Position(4.0, 0.5)))

    def test_number_of_tiles_excludes_furniture(self) -> None:
        self.assertEqual(self.make_room().get_num_tiles(), 10)

    def test_random_positions_never_land_on_furniture(self) -> None:
        room = self.make_room()
        random.seed(60002)
        for _ in range(250):
            position = room.get_random_position()
            self.assertIsInstance(position, ps3.Position)
            self.assertTrue(room.is_position_valid(position))

    def test_generated_furniture_stays_inside_and_does_not_fill_room(self) -> None:
        random.seed(60002)
        for _ in range(25):
            room = ps3.FurnishedRoom(6, 5, 1)
            room.add_furniture_to_room()
            self.assertGreater(len(room.furniture_tiles), 0)
            self.assertLess(len(room.furniture_tiles), 30)
            for x, y in room.furniture_tiles:
                self.assertTrue(0 <= x < 6 and 0 <= y < 5)


class Problem3StandardRobotTests(unittest.TestCase):
    def test_valid_move_updates_position_and_cleans_destination(self) -> None:
        room = ps3.EmptyRoom(4, 4, 2)
        robot = ps3.StandardRobot(room, 1.0, 1)
        robot.set_robot_position(ps3.Position(1.5, 1.5))
        robot.set_robot_direction(90.0)

        before = room.get_dirt_amount(2, 1)
        robot.update_position_and_clean()

        position = robot.get_robot_position()
        self.assertAlmostEqual(position.get_x(), 2.5)
        self.assertAlmostEqual(position.get_y(), 1.5)
        self.assertEqual(robot.get_robot_direction(), 90.0)
        self.assertEqual(room.get_dirt_amount(2, 1), max(0, before - 1))

    def test_invalid_move_stays_still_and_does_not_clean(self) -> None:
        room = ps3.EmptyRoom(3, 3, 2)
        robot = ps3.StandardRobot(room, 1.0, 1)
        robot.set_robot_position(ps3.Position(1.5, 2.5))
        robot.set_robot_direction(0.0)
        before = room.get_dirt_amount(1, 2)

        random.seed(60002)
        robot.update_position_and_clean()

        position = robot.get_robot_position()
        self.assertEqual((position.get_x(), position.get_y()), (1.5, 2.5))
        self.assertEqual(room.get_dirt_amount(1, 2), before)
        self.assertGreaterEqual(robot.get_robot_direction(), 0.0)
        self.assertLess(robot.get_robot_direction(), 360.0)

    def test_robot_cannot_land_on_furniture(self) -> None:
        room = ps3.FurnishedRoom(4, 3, 2)
        room.furniture_tiles = [(2, 1)]
        robot = ps3.StandardRobot(room, 1.0, 1)
        robot.set_robot_position(ps3.Position(1.5, 1.5))
        robot.set_robot_direction(90.0)
        before = room.get_dirt_amount(1, 1)

        robot.update_position_and_clean()

        position = robot.get_robot_position()
        self.assertEqual((position.get_x(), position.get_y()), (1.5, 1.5))
        self.assertEqual(room.get_dirt_amount(1, 1), before)


class Problem4FaultyRobotTests(unittest.TestCase):
    def tearDown(self) -> None:
        ps3.FaultyRobot.set_faulty_probability(0.15)

    def test_fault_probability_is_configurable(self) -> None:
        room = ps3.EmptyRoom(3, 3, 1)
        robot = ps3.FaultyRobot(room, 1.0, 1)
        ps3.FaultyRobot.set_faulty_probability(0.25)
        with mock.patch.object(ps3.random, "random", side_effect=(0.24, 0.25)):
            self.assertTrue(robot.gets_faulty())
            self.assertFalse(robot.gets_faulty())

    def test_faulty_timestep_changes_direction_without_moving_or_cleaning(self) -> None:
        room = ps3.EmptyRoom(4, 4, 2)
        robot = ps3.FaultyRobot(room, 1.0, 1)
        robot.set_robot_position(ps3.Position(1.5, 1.5))
        robot.set_robot_direction(90.0)
        before = room.get_dirt_amount(1, 1)

        with mock.patch.object(robot, "gets_faulty", return_value=True):
            random.seed(60002)
            robot.update_position_and_clean()

        position = robot.get_robot_position()
        self.assertEqual((position.get_x(), position.get_y()), (1.5, 1.5))
        self.assertEqual(room.get_dirt_amount(1, 1), before)
        self.assertGreaterEqual(robot.get_robot_direction(), 0.0)
        self.assertLess(robot.get_robot_direction(), 360.0)

    def test_nonfaulty_timestep_uses_standard_movement(self) -> None:
        room = ps3.EmptyRoom(4, 4, 2)
        robot = ps3.FaultyRobot(room, 1.0, 1)
        robot.set_robot_position(ps3.Position(1.5, 1.5))
        robot.set_robot_direction(90.0)
        before = room.get_dirt_amount(2, 1)

        with mock.patch.object(robot, "gets_faulty", return_value=False):
            robot.update_position_and_clean()

        position = robot.get_robot_position()
        self.assertAlmostEqual(position.get_x(), 2.5)
        self.assertAlmostEqual(position.get_y(), 1.5)
        self.assertEqual(room.get_dirt_amount(2, 1), max(0, before - 1))


class _SequentialCleaningRobot:
    """Deterministic robot double for run_simulation orchestration tests."""

    constructor_calls: list[tuple[float, int]] = []

    def __init__(self, room, speed, capacity):
        self.room = room
        self.capacity = capacity
        self.constructor_calls.append((speed, capacity))
        if not hasattr(room, "_test_next_tile"):
            room._test_next_tile = 0

    def update_position_and_clean(self) -> None:
        tile_index = self.room._test_next_tile
        self.room._test_next_tile += 1
        width = int(self.room.width)
        height = int(self.room.height)
        if tile_index >= width * height:
            return
        x = tile_index // height
        y = tile_index % height
        self.room.clean_tile_at_position(ps3.Position(x + 0.5, y + 0.5), self.capacity)


class Problem5SimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        _SequentialCleaningRobot.constructor_calls.clear()

    def test_one_robot_cleans_one_new_tile_per_timestep(self) -> None:
        result = ps3.run_simulation(
            1, 1.0, 1, 2, 2, 1, 0.5, 3, _SequentialCleaningRobot
        )
        self.assertEqual(result, 2.0)

    def test_all_robots_move_once_per_timestep(self) -> None:
        result = ps3.run_simulation(
            2, 1.0, 1, 2, 2, 1, 1.0, 2, _SequentialCleaningRobot
        )
        self.assertEqual(result, 2.0)

    def test_zero_coverage_requires_no_timesteps(self) -> None:
        result = ps3.run_simulation(
            1, 1.0, 1, 2, 2, 1, 0.0, 2, _SequentialCleaningRobot
        )
        self.assertEqual(result, 0.0)

    def test_requested_robot_type_speed_and_capacity_are_used(self) -> None:
        ps3.run_simulation(3, 0.5, 2, 2, 2, 2, 0.5, 2, _SequentialCleaningRobot)
        self.assertEqual(len(_SequentialCleaningRobot.constructor_calls), 6)
        self.assertTrue(
            all(call == (0.5, 2) for call in _SequentialCleaningRobot.constructor_calls)
        )


PROBLEM_TESTS: dict[str, tuple[type[unittest.TestCase], ...]] = {
    "1": (Problem1PositionTests, Problem1RectangularRoomTests, Problem1RobotTests),
    "2": (Problem2EmptyRoomTests, Problem2FurnishedRoomTests),
    "3": (Problem3StandardRobotTests,),
    "4": (Problem4FaultyRobotTests,),
    "5": (Problem5SimulationTests,),
}


def _suite_for_problem_numbers(problem_numbers: list[str]) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for problem_number in problem_numbers:
        for test_case in PROBLEM_TESTS[problem_number]:
            suite.addTests(loader.loadTestsFromTestCase(test_case))
    return suite


if __name__ == "__main__":
    requested_problems = sys.argv[1:]
    if requested_problems and all(
        number in PROBLEM_TESTS for number in requested_problems
    ):
        result = unittest.TextTestRunner(verbosity=2).run(
            _suite_for_problem_numbers(requested_problems)
        )
        raise SystemExit(not result.wasSuccessful())

    unittest.main(verbosity=2)
