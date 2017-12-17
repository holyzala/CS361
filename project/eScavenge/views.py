from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team, Game
from django.http import HttpResponseForbidden

GM = GMFactory().get_gm()


@require_http_methods(["GET"])
def index(request):
    user = request.session.get( 'username' )
    if user is None:
        return render(request, 'login.html' )
    if user == GM.username:
        return redirect("/gamemakerPage")
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
                return redirect("/gamemakerPage")
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

def gamemakerPage(request):
    username = request.session.get('username')
    message = ''
    cli = CLI(COMMANDS)
    if username != GM.username:
        return HttpResponseForbidden()
    if (request.method == 'POST'):
        if (request.POST.get("selectGame")):
            request.session['curgame'] = request.POST["gameObject"]
    if('curgame' in request.session.keys()):
        curgame = request.session.get('curgame')
        try:
            gameteam = Game.objects.get(name = curgame).teams.all()
        except:
            gameteam = []
            message = "No Teams Yet!"
        try: 
            gamemarks = Game.objects.get(name = curgame).landmarks.all()
        except:
            gamemarks = []
            message = message + " No Landmarks Yet!"
        gamestatus = "NOT WORKING YET"
        if (Game.objects.get(name = curgame).started is False and Game.objects.get(name = curgame).ended is False):
            gamestatus = "Waiting To Start"
        elif (Game.objects.get(name = curgame).started is True and Game.objects.get(name = curgame).ended is True):
            gamestatus = "Game Ended"
        elif(Game.objects.get(name = curgame).started is True and Game.objects.get(name = curgame).ended is False):
            gamestatus = "Game is Running"
        else:
           gamestatus = "Uknown Error"
    else:
        gamestatus = "No Game Selected"
        curgame = False
        gameteam = False
        gamemarks = False
    games = Game.objects.all()
    markcount = len(gamemarks)
    teamcount = len(gameteam)
    if (request.method == 'POST'):
        if request.POST.get("gmlogout"):
            del request.session['username']
            del request.session['curgame']
            return redirect('/')
        elif request.POST.get("startGame"):
            if (curgame is False):
                message = 'You have not selected a game yet!'
            else:
                command = "load " + curgame
                cli.command(command,"gamemaker")
                cli.command("start","gamemaker")
        elif request.POST.get("endGame"):
            if (curgame is False):
                message = 'You have not selected a game yet!'
            else:
                command = "load " + curgame
                cli.command(command,"gamemaker")
                cli.command("end","gamemaker")

    gamecontext = {'games': games ,'curgame': curgame, 'message':message, 'gameteam': gameteam, 'gamemarks':gamemarks, 'gamestatus':gamestatus, 'markcount':markcount,'teamcount':teamcount}
    return render(request, "gamemakerPage.html",gamecontext)