from django.shortcuts import render
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team

GM = GMFactory().get_gm()


def index(request):
    return render(request, 'index.html', {"message": ""})


def validate(request):
    message = "XXX"
    if request.POST["huntUser"] == GM.username:
        if GM.login(request.POST['huntUser'], request.POST['password']) is None:
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
    cli = CLI(COMMANDS)
    cli.game_maker = GM
    if request.POST['huntUser'] != GM.username:
        cli.game = Team.objects.get(username=request.POST['huntUser']).game
    else:
        cli.game = GM.game
    output = cli.command(request.POST["command"], request.POST['huntUser'])
    context = {"huntUser": request.POST["huntUser"], "output": output}
    return render(request, "terminal.html", context)
