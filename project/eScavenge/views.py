from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team

GM = GMFactory().get_gm()


@require_http_methods(["GET"])
def index(request):
    user = request.session.get( 'username' )
    if user is None:
        return render(request, 'login.html' )
    if user == GM.username:
        return redirect("/gamemaker")
    return redirect("/teamPage")


@require_http_methods(["POST"])
def login(request):
    message = ""
    if request.method == 'POST':
        if request.POST["username"] == GM.username:
            if GM.login(request.POST['username'], request.POST['password']) is None:
                message = "Invalid password"
            else:
                request.session['username'] = request.POST["username"]
                return render(request, 'gamemaker.html')
        try:
            u = Team.objects.get(username=request.POST["username"])
        except Team.DoesNotExist:
            message = "No user named " + request.POST["username"]
        else:
            if u.login(request.POST['username'], request.POST['password']) is None:
                message = "Invalid password"
        if message == "":
            request.session['username'] = request.POST["username"]
            userpage = Team.objects.get(username=request.session.get('username'))
            teamlist = userpage.game.teams.order_by('-points')
            teamhistory = userpage.history.all()
            context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory}
            return render(request, 'teamPage.html', context)
    return render(request, 'login.html', {'message': message})


@require_http_methods(["GET", "POST"])
def teamPage(request):
    user = request.session.get('username')
    command = ''
    if request.method == 'POST':
        if request.POST.get("logoutbutton"):
            del request.session['username']
            return redirect('/')
        if request.POST.get("changeteam"):
            command += 'editteam'
            if request.POST.get('changeusername'):
                command += f' name { request.POST["changeusername"]  }'
            if request.POST.get('changepassword'):
                command += f' password {request.POST["changepassword"] }'
        elif request.POST.get("quitQuestion"):
            team = Team.objects.get(username=user)
            command += f' giveup {user} {team.password}'
        elif request.POST.get("answerQuestion"):
            command += f' answer \'{request.POST.get( "commandline", None ) }\''
        CLI(COMMANDS).command(command, user)
        if request.POST.get('changeusername'):
            request.session['username'] = request.POST["changeusername"]
    userpage = Team.objects.get(username=request.session.get('username'))
    teamlist = userpage.game.teams.order_by('-points')
    teamhistory = userpage.history.all()
    context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory, 'command': command}
    return render(request, 'teamPage.html', context)
