import CLI
import shlex


if __name__ == "__main__":
    cli = CLI.CLI(CLI.COMMANDS)
    while True:
        inp = input("> ")
        tokenized = shlex.split(inp.lower())
        try:
            if tokenized[0] == 'print':
                if tokenized[1] == 'cli':
                    print(vars(cli))
                elif tokenized[1] == 'game':
                    if cli.game:
                        print(vars(cli.game))
                    else:
                        print(None)
                elif tokenized[1] == 'gamemaker':
                    print(vars(cli.game_maker))
                elif tokenized[1] == 'team':
                    if cli.game:
                        print(vars(cli.game.teams[tokenized[2]]))
                    else:
                        print(None)
                elif tokenized[1] == 'landmark':
                    if cli.game:
                        for landmark in cli.game.landmarks:
                            if landmark.clue == tokenized[2]:
                                print(vars(landmark))
                    else:
                        print(None)
                continue
        except IndexError:
            continue

        print(cli.command(inp))
