from parsing import ParseMap, SaveMap, ParseCon
from pathfinding import StateMachine
from visualization import GraphRepresentation
import sys


def main() -> None:
    """
    Run the complete Fly-in application workflow.

    Parses and validates the input map, prepares the connection data,
    runs the drone pathfinding simulation, and starts the graphical
    representation of the results.
    """
    try:
        ParseMap()
        SaveMap()

        ParseCon()

        StateMachine()

        GraphRepresentation()
    except KeyboardInterrupt:
        sys.exit("\nERROR: Keyboard Interrupted")


if __name__ == "__main__":
    main()
