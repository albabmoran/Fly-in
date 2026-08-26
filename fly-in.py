from parsing import ParseMap, SaveMap, ParseCon


def main() -> None:
    # Parse .txt file
    parse_map = ParseMap()
    parse_map.read_and_validate()
    save_map = SaveMap()
    save_map.check_map()
    save_map.convert_to_json()

    # Parse connections for pathfinding
    parse_con = ParseCon()
    parse_con.extract_from_json()
    parse_con.convert_connections()
    parse_con.convert_to_json()


if __name__ == "__main__":
    main()
