import shlex

from .CLI import CLI, COMMANDS

if __name__ == "__main__":
    cli = CLI(COMMANDS)
    while True:
        inp = input("> ")
        tokenized = shlex.split(inp)
        try:
            if tokenized[0].lower() == 'print':
                if tokenized[1].lower() == 'cli':
                    print(vars(cli))
                elif tokenized[1].lower() == 'game':
                    if cli.game:
                        print(vars(cli.game))
                    else:
                        print(None)
                elif tokenized[1].lower() == 'gamemaker':
                    print(vars(cli.game_maker))
                elif tokenized[1].lower() == 'team':
                    if cli.game:
                        print(vars(cli.game.teams[tokenized[2]]))
                    else:
                        print(None)
                elif tokenized[1].lower() == 'landmark':
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
