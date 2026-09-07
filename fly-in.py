from parsing import ParseMap, SaveMap, ParseCon
from pathfinding import StateMachine
from visualization import GraphRepresentation


def main() -> None:
    # Parse .txt file
    ParseMap()
    SaveMap()

    # Parse connections for pathfinding
    ParseCon()

    # Pathfinding
    StateMachine()

    # Visualization
    GraphRepresentation()


if __name__ == "__main__":
    main()
