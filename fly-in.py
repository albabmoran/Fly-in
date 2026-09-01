from parsing import ParseMap, SaveMap, ParseCon
from pathfinding import StateMachine


def main() -> None:
    # Parse .txt file
    ParseMap()
    SaveMap()

    # Parse connections for pathfinding
    ParseCon()

    # Pathfinding
    StateMachine()


if __name__ == "__main__":
    main()
