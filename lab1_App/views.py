import datetime
from django.http import HttpRequest, HttpResponse
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from lab1_App import models
from django.db.models import Q, F

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def index(request):
    teams = models.Teams.objects.all().order_by("-points", "-won")
    teams_matches = {}
    for team in teams:
        last_5 = models.Matches.objects.filter(Q(team1=team.id) | Q(team2=team.id)).order_by("date", "time")[:5]
        if len(last_5) > 0:
            teams_matches.update({team : last_5})

    matches = models.Matches.objects.all().order_by("-date", "-time")

    ranking = [i for i in range(1, len(matches) + 1)]

    return render(
        request,
        "index.html",
        context={
            "ranking": ranking,
            "teams": teams,
            "teams_matches": teams_matches,
            "matches": matches,
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
            "ADMIN_EMAIL": ADMIN_EMAIL
        },
    )

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def details(request, match_id):
    if not request.session:
        return redirect("/login")

    match = models.Matches.objects.filter(id=match_id).first()
    comments = models.Comments.objects.filter(match_id=match_id).order_by("-changed")
        
    return render(
        request,
        "details.html",
        context={
            "match": match,
            "comments": comments,
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
            "ADMIN_EMAIL": ADMIN_EMAIL
        },
    )

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    if not models.Users.objects.filter(email=request.session.get("user")["userinfo"]["name"]).exists():
        # create new user if email is not in database
        new_user = models.Users(email=request.session.get("user")["userinfo"]["name"], name=request.session.get("user")["userinfo"]["nickname"])
        new_user.save()

    return redirect(request.build_absolute_uri(reverse("index")))


## COMMENTS ## 

def add_comment(request, match_id):
    if not request.session:
        return redirect("/login")

    if request.method == "POST":
        comment = request.POST["comment"]
        user = models.Users.objects.filter(email=request.session.get("user")["userinfo"]["name"])[0]
        match = models.Matches.objects.get(pk=match_id)

        new_comment = models.Comments(user=user, match=match, comment=comment)
        new_comment.save()

    return redirect("/details/" + match_id)


def edit_comment(request, comment_id):
    if not request.session:
        return redirect("/login")


    comment = models.Comments.objects.get(id=comment_id)
    match_id = comment.match.id

    if request.method == "POST":
        comment_text = request.POST["comment"]
        models.Comments.objects.filter(id=comment.id).update(comment=comment_text, changed=datetime.datetime.now())

    return redirect("/details/" + str(match_id))
    
def delete_comment(request, comment_id):
    if not request.session:
        return redirect("/login")

    comment = models.Comments.objects.get(id=comment_id)
    match_id = comment.match.id

    comment.delete()

    return redirect("/details/" + str(match_id))


## MATCHES ##

def add_match(request):
    if not request.session:
        return redirect("/login")

    if request.method == "POST":
        team1 = request.POST["team1"]
        team2 = request.POST["team2"]
        goals1 = request.POST["goals1"] if "goals1" in request.POST else None
        goals2 = request.POST["goals2"] if "goals2" in request.POST else None
        date = request.POST["date"]
        time = request.POST["time"]

        if team1 == team2:
            return redirect("/")

        team1 = models.Teams.objects.filter(id=team1).first()
        team2 = models.Teams.objects.filter(id=team2).first()

        new_match = models.Matches(team1=team1, team2=team2, goals1=goals1, goals2=goals2, date=date, time=time)
        new_match.save()

        # update stats for teams
        update_statistics()

    return redirect("/")

def edit_match(request, match_id):
    if not request.session:
        return redirect("/login")

    if request.method == "POST":
        team1 = request.POST["team1"]
        team2 = request.POST["team2"]
        goals1 = request.POST["goals1"] if "goals1" in request.POST else None
        goals2 = request.POST["goals2"] if "goals2" in request.POST else None
        date = request.POST["date"]
        time = request.POST["time"]

        if team1 == team2:
            return redirect("/")

        team1 = models.Teams.objects.filter(id=team1).first()
        team2 = models.Teams.objects.filter(id=team2).first()

        models.Matches.objects.filter(id=match_id).update(team1=team1, team2=team2, goals1=goals1, goals2=goals2, date=date, time=time)

        # update stats for teams
        update_statistics()

    return redirect("/")

def delete_match(request, match_id):
    if not request.session:
        return redirect("/login")

    match = models.Matches.objects.get(id=match_id)

    match.delete()

    update_statistics()

    return redirect("/")


## BL ##

def update_statistics():
    teams = models.Teams.objects.all()

    for team in teams:
        played = 0
        points = 0
        won = 0
        lost = 0

        wins1 = models.Matches.objects.filter(team1=team, goals1__gt=F("goals2"))
        wins2 = models.Matches.objects.filter(team2=team, goals2__gt=F("goals1"))

        points += (len(wins1) + len(wins2)) * 2
        won += len(wins1) + len(wins2)

        draws1 = models.Matches.objects.filter(team1=team, goals1=F("goals2"))
        draws2 = models.Matches.objects.filter(team2=team, goals2=F("goals1"))

        points += len(draws1) + len(draws2)

        losses1 = models.Matches.objects.filter(team1=team, goals1__lt=F("goals2"))
        losses2 = models.Matches.objects.filter(team2=team, goals2__lt=F("goals1"))

        lost += len(losses1) + len(losses2)

        played = len(wins1) + len(wins2) + len(draws1) + len(draws2) + len(losses1) + len(losses2)

        models.Teams.objects.filter(id=team.id).update(won=won, lost=lost, points=points, played=played)

        

