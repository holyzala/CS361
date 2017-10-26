import Commands

commands = {"quit": Commands.quit}

if __name__ == "__main__":
    while True:
        inp = input("> ")
        split = inp.split(" ")
        try:
            commands[split[0].lower()](split)
        except KeyError:
            print("Invalid command")
