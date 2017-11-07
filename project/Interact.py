import CLI


if __name__ == "__main__":
    cli = CLI.CLI(CLI.commands)
    while True:
        print(cli.command(input("> ")))