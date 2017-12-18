from datetime import timedelta

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .CLI import CLI, COMMANDS
from .models import GMFactory, Team, Landmark, Game

GM = GMFactory().get_gm()


@require_http_methods(["GET"])
def index(request):
    user = request.session.get('username')
    if user is None:
        return render(request, 'login.html')
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
                return redirect('/gamemaker')
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
    team = Team.objects.get(username=request.session.get('username'))
    command = ''
    output = ''
    if request.method == 'POST':
        if request.POST.get("logoutbutton"):
            return redirect('/logout')
        if request.POST.get("changeteam"):
            command += 'editteam'
            if request.POST.get('changeusername'):
                command += f' name {request.POST["changeusername"]}'
            if request.POST.get('changepassword'):
                command += f' password {request.POST["changepassword"]}'
        elif request.POST.get("quitQuestion"):
            command += f'giveup {team.username} {team.password}'
        elif request.POST.get("answerQuestion"):
            command += f' answer \'{request.POST.get("commandline", None)}\''
        output = CLI(COMMANDS).command(command, user)
        if request.POST.get('changeusername'):
            request.session['username'] = request.POST["changeusername"]
    userpage = Team.objects.get(username=request.session.get('username'))
    teamlist = userpage.game.teams.order_by('-points')
    teamhistory = userpage.history.all()
    context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory, 'output': output}
    return render(request, 'teamPage.html', context)


def editTeam(request):
    context = {'teamName': request.GET['name']}
    return render(request, "editTeam.html", context)


def editTeamAction(request):
    cli = CLI(COMMANDS)
    user = request.session.get('username')
    game = request.session.get('game_name')
    command = f'load {Game.objects.get(name=game).name}'
    cli.command(command, user)
    if user is None or user != GM.username:
        return HttpResponseForbidden()
    if request.method == 'POST':
        if request.POST.get('old_name') == 'NewTeam':
            addInput = 'addteam'
            addInput += f' {request.POST["usernameedit"]}'
            addInput += f' {request.POST["passwordedit"]}'
            cli.command(addInput, user)
            return redirect('/')
        if request.POST.get('deleteteam'):
            deleteInput = f' removeteam {request.POST.get("old_name")}'
            cli.command(deleteInput, user)
            return redirect('/')
        commandInput = 'editteam'
        if request.POST.get("usernameedit"):
                commandInput += f' name {request.POST["usernameedit"]}'
        if request.POST.get("passwordedit"):
                commandInput += f' password {request.POST["passwordedit"]}'
        cli.command(commandInput, request.POST.get('old_name'))

        return redirect('/')


def logout(request):
    del request.session['username']
    return redirect('/')


@require_http_methods(['GET', 'POST'])
def editLandmark(request):
    if request.session.get('username') != GM.username:
        return HttpResponseForbidden()
    if request.method == 'GET':
        return edit_landmark_get(request)
    return edit_landmark_post(request)


def edit_landmark_post(request):
    landmark_old_name = request.POST.get('landmark_name')
    game = request.session.get('game_name')
    gamecommand = "load " + game
    cli = CLI(COMMANDS)
    cli.command(gamecommand, GM.username)
    command = ''
    if request.POST.get('deletelandmark'):
        command += 'removelandmark '
        command += f' {landmark_old_name}'
        cli.command(command, GM.username)
    if request.POST.get('editLandmark'):
        if landmark_old_name != 'NewLandmark':
            command += 'editlandmark '
            command += f' { landmark_old_name }'
            if request.POST.get('editLMname'):
                command += f' name \'{ request.POST["editLMname"] }\''
            if request.POST.get('editLMclue'):
                command += f' clue \'{ request.POST["editLMclue"] }\''
            if request.POST.get('editLMquestion'):
                command += f' question \'{ request.POST["editLMquestion"] }\''
            if request.POST.get('editLManswer'):
                command += f' answer \'{ request.POST["editLManswer"] }\''
        else:
            command += 'addlandmark '
            command += f' \'{ request.POST["editLMname"] }\''
            command += f' \'{ request.POST["editLMclue"] }\''
            command += f' \'{ request.POST["editLMquestion"] }\''
            command += f' \'{ request.POST["editLManswer"] }\''
        cli.command(command, GM.username)
    return redirect('/')


def edit_landmark_get(request):
    landmark_name = request.GET['landmark']
    game_name = request.session.get('game_name')
    landmark = None
    if landmark_name != 'NewLandmark':
        landmark = Landmark.objects.get(name=landmark_name)

    context = {'game_name': game_name, 'landmark_name': landmark_name, 'landmark': landmark}
    return render(request, 'editLandmark.html', context)


@require_http_methods(['GET'])
def game_page(request):
    username = request.session.get('username')
    if username != GM.username:
        return HttpResponseForbidden()
    game_name = request.session.get('game_name')
    game = "NewGame"
    teams = []
    if game_name is not None and game_name != game:
        game = Game.objects.get(name=game_name)
        teams = game.teams.all()

    context = {'username': username, 'game': game, 'teamlist': teams, 'games': Game.objects.all()}
    return render(request, 'gamePage.html', context)


@require_http_methods(['POST'])
def save_game(request):
    username = request.session.get('username')
    if username != GM.username:
        return HttpResponseForbidden()

    game_name = request.POST['game_name']
    is_new = request.POST.get('NewSubmit')
    if not is_new:
        status = int(request.POST['game_status'])
    penalty_value = request.POST['game_penalty_value']
    penalty_time = request.POST['game_penalty_time']
    timer = request.POST['game_timer']
    points = request.POST['game_points']
    game = None
    if not is_new:
        game = Game.objects.get(name=game_name)
        cur_status = 0
        if game.started:
            cur_status = 1
        if game.ended:
            cur_status = 2

        if cur_status == 0 and status == 1:
            cli = CLI(COMMANDS)
            cli.command(f'load {game_name}', GM.username)
            cli.command('start', GM.username)
        if cur_status != 2 and status == 2:
            game.ended = True
            game.full_clean()
            game.save()
    else:
        game = Game.objects.create(name=game_name, started=False, ended=False, penalty_value=0, penalty_time=0,
                                   timer=None, landmark_points=0)
    game.refresh_from_db()
    game.penalty_time = penalty_time
    game.penalty_value = penalty_value
    game.landmark_points = points
    if timer != 'None':
        timer_split = timer.split(':')
        game.timer = timedelta(hours=int(timer_split[0]), minutes=int(timer_split[1]), seconds=int(timer_split[2]))
    game.full_clean()
    game.save()

    return redirect('/')


@require_http_methods(['POST'])
def choose_game(request):
    request.session['game_name'] = request.POST['selected_game']
    return redirect('/')
