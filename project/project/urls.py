"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from eScavenge import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^chooseGame', views.choose_game, name='choosegame'),
    url(r'^editLandmark', views.editLandmark, name='editlandmark'),
    url(r'^editTeam$', views.editTeam, name='editTeam'),
    url(r'^editTeamAction', views.editTeamAction, name='editTeamAction'),
    url(r'^gamemaker', views.game_page, name='gamemaker'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^teamPage', views.teamPage, name='teamPage'),
    url(r'^saveGame', views.save_game, name='savegame'),
]
