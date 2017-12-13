from django.shortcuts import render
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team

GM = GMFactory().get_gm()


# def index(request)
#    check session if has user, then return to teampage.html
#   if no session
#      return render


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


def teamPage(request):
    user = request.session.get('username')
    command = ''
    if request.method == 'POST':
        if request.POST.get("changeteam"):
            command += 'editteam'
            if 'changeteam' in request.POST:
                command += f' name { request.POST["changeusername"]  }'
            if 'changepassword' in request.POST:
                command += f' password {request.POST["changepassword"] }'
            del request.session['username']
            request.session.modified = True
            request.session['username'] = request.POST["changeusername"]
        elif request.POST.get("quitQuestion"):
            command += ' giveup'
        elif request.POST.get("answerQuestion"):
            command += f' answer {request.POST.get( "commandline", None ) }'
        CLI(COMMANDS).command(command, user)
    userpage = Team.objects.get(username=request.session.get('username'))
    teamlist = userpage.game.teams.order_by('-points')
    teamhistory = userpage.history.all()
    context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory, 'command': command}
    return render(request, 'teamPage.html', context)
