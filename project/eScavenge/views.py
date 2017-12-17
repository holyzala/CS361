from django.shortcuts import render, redirect
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
            command += ' giveup'
        elif request.POST.get("answerQuestion"):
            command += f' answer {request.POST.get( "commandline", None ) }'
        CLI(COMMANDS).command(command, user)
        if request.POST.get('changeusername'):
            request.session['username'] = request.POST["changeusername"]
    userpage = Team.objects.get(username=request.session.get('username'))
    teamlist = userpage.game.teams.order_by('-points')
    teamhistory = userpage.history.all()
    context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory, 'command': command}
    return render(request, 'teamPage.html', context)

def editTeam(request):
    context = {'team' : 'Team1'}
    return render(request, "editTeam.html", context)

def editTeamAction(request):
    user = GM.username
    cli = CLI(COMMANDS)
    #user = request.session.get('username')
    gamecommand = "load game1"

    cli.command(gamecommand, user)

    #if user is None or user != GM.username:
        #return redirect('/')

    if request.method == 'POST':
        '''
            #deleteInput = ''
            #if request.POST['deleteteam']:
                #deleteInput = 'removeteam ' <code for the current team>

            #li.command(commandInput, user)
        '''
        deleteInput = 'removeteam'

        if request.POST.get("deleteteam"):
            deleteInput += ' team1'
            cli.command(deleteInput, user)
            return redirect('/')
        

        commandInput = 'editteam team1'

        if request.POST["usernameedit"]:
                commandInput += f' name {request.POST["usernameedit"]}'

        if request.POST["passwordedit"]:
                commandInput += f' password {request.POST["passwordedit"]}'

        cli.command(commandInput, user)

        return redirect('/')