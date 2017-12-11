from django.shortcuts import render
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team

GM = GMFactory().get_gm()


def index(request):
    return render(request, 'index.html', {"message": ""})


def validate(request):
    message = "XXX"
    if request.POST["username"] == GM.username:
        if GM.login(request.POST['username'], request.POST['password']) is None:
            message = "Invalid password"
    else:
        try:
            u = Team.objects.get(username=request.POST["username"])
        except Team.DoesNotExist:
            message = "No user named " + request.POST["username"]
        else:
            if u.login(request.POST['username'], request.POST['password']) is None:
                message = "Invalid password"
    if message == "XXX":
        teamlist = []
        game_id = Team.objects.get(username=request.POST["username"]).game_id
        for team in Team.objects.filter(game_id=game_id).order_by('-points'):
            username = team.username
            teamlist.append(username)
        context = {"huntUser": request.POST["username"], "teamlist" : teamlist}
        return render(request, "teamPage.html", context)
    return render(request, "login.html", {"message": message})


def terminal(request):
    cli = CLI(COMMANDS)
    cli.game_maker = GM
    if request.POST['huntUser'] != GM.username:
        cli.game = Team.objects.get(username=request.POST['huntUser']).game
    else:
        cli.game = GM.game
    output = cli.command(request.POST["command"], request.POST['huntUser'])
    context = {"huntUser": request.POST["huntUser"], "output": output}
    return render(request, "teamPage.html", context)


def login(request):
    return render(request, "login.html")

def teamPage(request):
    return render(request, "teamPage.html")