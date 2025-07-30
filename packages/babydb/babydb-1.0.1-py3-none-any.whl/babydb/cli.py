import shlex
from .core import SimpleDB

def run_cli():
    db = SimpleDB()
    print("Simple Key-Value Database")
    print("=========================")
    print("Available Commands:")
    print("\nAuthentication:")
    print("  - login <username> <password>")
    print("  - logout")
    print("\nData Operations:")
    print("  - create <key> <value>")
    print("  - upload <key> <file_path>")
    print("  - get_file <key> [index]")
    print("  - download_file <key> [index] [dest_path]")
    print("  - read <key>")
    print("  - update <key> <value>")
    print("  - delete <key>")
    print("  - list")
    print("\nQuery Operations:")
    print("  - find = <value> [sortby <field>] [limit <n>]")
    print("  - find > <value> [sortby <field>] [limit <n>]")
    print("  - find < <value> [sortby <field>] [limit <n>]")
    print("  - find contains <value> [sortby <field>] [limit <n>]")
    print("  - find fulltext <value> [sortby <field>] [limit <n>]")
    print("  - find <field> = <value> [sortby <field>] [limit <n>]")
    print("  - join <key1> <key2> [field]")
    print("\nAggregation Operations:")
    print("  - max <key>")
    print("  - min <key>")
    print("  - sum <key>")
    print("  - avg <key>")
    print("\nData Import/Export:")
    print("  - import_csv <file>")
    print("  - export_csv <file>")
    print("\nTransaction Management:")
    print("  - begin")
    print("  - commit")
    print("  - rollback")
    print("\nDebugging:")
    print("  - inspect_index [word]")
    print("\nOther Commands:")
    print("  - help")
    print("  - exit")
    print("\nNotes:")
    print("  - Database is stored compressed as database.json.gz")
    print("  - Files are stored compressed in files/")
    print("  - Must log in to perform operations (default users: admin/admin123, user/user123)")
    print("  - Admin role required for delete, upload, import_csv, and export_csv")
    print("  - Use quotes for values with spaces")
    print("  - CSV format: key,value")
    print("=========================")

    while True:
        try:
            input_str = input("> ")
            parts = shlex.split(input_str)
        except (ValueError, EOFError, KeyboardInterrupt):
            print("Exiting...")
            break

        if not parts:
            continue

        command = parts[0].lower()
        try:
            if command == "login" and len(parts) == 3:
                print(db.login(parts[1], parts[2]))
            elif command == "logout" and len(parts) == 1:
                print(db.logout())
            elif command == "create" and len(parts) >= 3:
                print(db.create(parts[1], " ".join(parts[2:])))
            elif command == "upload" and len(parts) == 3:
                print(db.upload(parts[1], parts[2]))
            elif command == "get_file" and len(parts) in (2, 3):
                index = parts[2] if len(parts) == 3 else None
                print(db.get_file(parts[1], index))
            elif command == "download_file" and len(parts) in (3, 4):
                index = parts[2] if len(parts) == 4 else None
                dest_path = parts[3] if len(parts) == 4 else None
                print(db.download_file(parts[1], index, dest_path))
            elif command == "read" and len(parts) == 2:
                print(db.read(parts[1]))
            elif command == "update" and len(parts) >= 3:
                print(db.update(parts[1], " ".join(parts[2:])))
            elif command == "delete" and len(parts) == 2:
                print(db.delete(parts[1]))
            elif command == "find" and len(parts) >= 2:
                print(db.find(" ".join(parts[1:])))
            elif command == "join" and len(parts) in (3, 4):
                field = parts[3] if len(parts) == 4 else None
                print(db.join(parts[1], parts[2], field))
            elif command == "max" and len(parts) == 2:
                print(db.max(parts[1]))
            elif command == "min" and len(parts) == 2:
                print(db.min(parts[1]))
            elif command == "sum" and len(parts) == 2:
                print(db.sum(parts[1]))
            elif command == "avg" and len(parts) == 2:
                print(db.avg(parts[1]))
            elif command == "import_csv" and len(parts) == 2:
                print(db.import_csv(parts[1]))
            elif command == "export_csv" and len(parts) == 2:
                print(db.export_csv(parts[1]))
            elif command == "begin" and len(parts) == 1:
                print(db.begin())
            elif command == "commit" and len(parts) == 1:
                print(db.commit())
            elif command == "rollback" and len(parts) == 1:
                print(db.rollback())
            elif command == "list" and len(parts) == 1:
                print(db.list_all())
            elif command == "inspect_index" and len(parts) in (1, 2):
                word = parts[1] if len(parts) == 2 else None
                print(db.inspect_inverted_index(word))
            elif command == "help" and len(parts) == 1:
                print("Simple Key-Value Database")
                print("=========================")
                print("Available Commands:")
                print("\nAuthentication:")
                print("  - login <username> <password>")
                print("  - logout")
                print("\nData Operations:")
                print("  - create <key> <value>")
                print("  - upload <key> <file_path>")
                print("  - get_file <key> [index]")
                print("  - download_file <key> [index] [dest_path]")
                print("  - read <key>")
                print("  - update <key> <value>")
                print("  - delete <key>")
                print("  - list")
                print("\nQuery Operations:")
                print("  - find = <value> [sortby <field>] [limit <n>]")
                print("  - find > <value> [sortby <field>] [limit <n>]")
                print("  - find < <value> [sortby <field>] [limit <n>]")
                print("  - find contains <value> [sortby <field>] [limit <n>]")
                print("  - find fulltext <value> [sortby <field>] [limit <n>]")
                print("  - find <field> = <value> [sortby <field>] [limit <n>]")
                print("  - join <key1> <key2> [field]")
                print("\nAggregation Operations:")
                print("  - max <key>")
                print("  - min <key>")
                print("  - sum <key>")
                print("  - avg <key>")
                print("\nData Import/Export:")
                print("  - import_csv <file>")
                print("  - export_csv <file>")
                print("\nTransaction Management:")
                print("  - begin")
                print("  - commit")
                print("  - rollback")
                print("\nDebugging:")
                print("  - inspect_index [word]")
                print("\nOther Commands:")
                print("  - help")
                print("  - exit")
                print("\nNotes:")
                print("  - Database is stored compressed as database.json.gz")
                print("  - Files are stored compressed in files/")
                print("  - Must log in to perform operations (default users: admin/admin123, user/user123)")
                print("  - Admin role required for delete, upload, import_csv, and export_csv")
                print("  - Use quotes for values with spaces")
                print("  - CSV format: key,value")
                print("=========================")
            elif command == "exit" and len(parts) == 1:
                print("Exiting...")
                break
            else:
                print("Invalid command. Type 'help' for a list of commands.")
        except Exception as e:
            print(f"Error in command processing: {e}")

if __name__ == "__main__":
    run_cli()