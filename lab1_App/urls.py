from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("details/<match_id>", views.details, name="details"),
    path("add_match", views.add_match, name="add_match"),
    path("edit_match/<match_id>", views.edit_match, name="edit_match"),
    path("delete_match/<match_id>", views.delete_match, name="delete_match"),
    path("add_comment/<match_id>", views.add_comment, name="add_comment"),
    path("edit_comment/<comment_id>", views.edit_comment, name="edit_comment"),
    path("delete_comment/<comment_id>", views.delete_comment, name="delete_comment"),
]
