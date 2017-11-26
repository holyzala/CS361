from django.shortcuts import render, redirect
from .CLI import CLI, COMMANDS
from .StringConst import login_success

cli = CLI(COMMANDS)


def index(request):
    return render(request, 'index.html', {"message":""})


def validate(request):
    rtn = cli.command("login {} {}".format(request.POST['huntUser'], request.POST['password']))
    if rtn != login_success:
        return render(request, 'index.html', {'message': rtn})
    context = {"huntUser": request.POST["huntUser"]}
    return render(request, "terminal.html", context)


def terminal(request):
    output = cli.command(request.POST["command"])
    context = {"huntUser": request.POST["huntUser"], "output": output}
    return render(request, "terminal.html", context)


def logout(request):
    cli.command("logout")
    return redirect("/")
