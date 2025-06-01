from django.urls import path
from . import views

urlpatterns = [
	path("", views.CreateGroupView),
	path("<int:pk>/", views.UpdateGroupView.as_view()),
	path("<int:pk>/members/", views.GroupMembersView.as_view()),
	path("<int:pk>/members/<int:pk>/")
]