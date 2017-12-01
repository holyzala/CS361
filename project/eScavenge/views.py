from django.shortcuts import render
from .CLI import CLI, COMMANDS
from .models import Team

cli = CLI(COMMANDS)


def index(request):
    return render(request, 'index.html', {"message":""})


def validate(request):
    message = "XXX"
    if request.POST["huntUser"] == cli.game_maker.username:
        if cli.game_maker.login(request.POST['huntUser'], request.POST['password']) is None:
            message = "Invalid password"
    else:
        try:
            u = Team.objects.get(username=request.POST["huntUser"])
        except Team.DoesNotExist:
            message = "No user named " + request.POST["huntUser"]
        else:
            if u.login(request.POST['huntUser'], request.POST['password']) is None:
                message = "Invalid password"
    if message == "XXX":
        context = {"huntUser": request.POST["huntUser"]}
        return render(request, "terminal.html", context)
    return render(request, "index.html", {"message": message})


def terminal(request):
    output = cli.command(request.POST["command"], request.POST['huntUser'])
    context = {"huntUser": request.POST["huntUser"], "output": output}
    return render(request, "terminal.html", context)
