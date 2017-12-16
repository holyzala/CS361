from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team, Landmark

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


def editLandmark(request):
#    landmark = request.GET['landmark']
#    game = request.GET['game']
    landmark = 'A1'
    game = 'game1'
    user = 'gamemaker'
    gamecommand = "load " + game
    cli = CLI(COMMANDS)
    cli.command(gamecommand, user)
    command = ''
    if request.method == 'POST':
      if request.POST.get('deletelandmark'):
        command += 'removelandmark '
        #if request.POST.get('landmarkname'):
        command += f' {landmark}'
        cli.command(command, user)

      if request.POST.get('editLandmark'):
          command += 'editlandmark '
          command += f' { landmark }'
          if request.POST.get('editLMname'):
              command += f' name { request.POST["editLMname"] }'
          if request.POST.get('editLMclue'):
              command += f' clue { request.POST["editLMclue"] }'
          if request.POST.get('editLMquestion'):
              command += f' question { request.POST["editLMquestion"] }'
          if request.POST.get('editLManswer'):
              command += f' answer { request.POST["editLManswer"] }'
          if request.POST.get('editLMgame'):
              command += f' game { request.POST["editLMgame"] }'
          cli.command(command, user)

    return render(request, 'editLandmark.html')
