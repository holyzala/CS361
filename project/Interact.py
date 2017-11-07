import CLI


if __name__ == "__main__":
    cli = CLI.CLI(CLI.COMMANDS)
    while True:
        print(cli.command(input("> ")))