from django.urls import path
from . import views

urlpatterns = [
	path("", views.CreateGroupView.as_view()),
	path("<int:pk>/", views.UpdateGroupView.as_view()),
	path("<int:pk>/members/", views.GroupMembersView.as_view()),
	path("<int:pk>/notifications/", views.GroupNotificationView.as_view()),
	path("<int:pk>/members/delete/", views.delete_group_members),
	path("<int:pk>/members/add/", views.add_group_members),
	path("<int:pk>/members/<int:member_id>/", views.GroupMemberRoleView.as_view()),
	path("<int:pk>/roles/", views.RolesView.as_view()),
	path("<int:pk>/roles/<int:role_id>/", views.EditRolesView.as_view()),
]