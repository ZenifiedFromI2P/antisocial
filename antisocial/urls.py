"""antisocial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
import bootstraps.views as bsview
import posts.views as pviews
import feeds.views as feeds

urlpatterns = [
    url(r'^$', bsview.index),
    url(r'^new/group$', bsview.StrapGroup.as_view()),
    url(r'^new/user$', bsview.UserKG.as_view()),
    url(r'^stream$', pviews.Stream.as_view()),
    url(r'^new/post$', pviews.NewPost.as_view()),
    url(r'^feeds/(?P<key>[a-zA-Z0-9+/]+={0,2}$)', feeds.Feedstream.as_view()),
    url(r'^new/feedpost$', feeds.NewFP.as_view())
]
