from django.shortcuts import render, redirect
from .CLI import CLI, COMMANDS
from .Team import Team
from .StringConst import login_success

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
            u = Team.objects.get(name=request.POST["huntUser"])
        except Team.DoesNotExist:
            message = "No user named " + request.POST["huntUser"]
        else:
            if u.login(request.POST['huntUser'], request.POST['password']) is None:
                message = "Invalid password"
    if message == "XXX":
        context = {"huntUser": request.POST["huntUser"]}
        return render(request, "terminal.html", context)
    else:
        return render(request, "index.html", {"message": message})


def terminal(request):
    output = cli.command(request.POST["command"])
    context = {"huntUser": request.POST["huntUser"], "output": output}
    return render(request, "terminal.html", context)


def logout(request):
    cli.command("logout")
    return redirect("/")
