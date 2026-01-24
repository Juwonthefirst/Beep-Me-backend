from django.urls import path
from . import views

urlpatterns = [
    path("", views.CreateGroupView.as_view()),
    path("permissions/", views.PermissionsView.as_view()),
    path("<int:pk>/", views.RetrieveUpdateGroupView.as_view()),
    path("<int:pk>/leave/", views.leave_group),
    path("<int:pk>/members/", views.GroupMembersView.as_view()),
    path("<int:pk>/notifications/", views.GroupNotificationView.as_view()),
    path("<int:pk>/members/delete/", views.delete_group_members),
    path("<int:pk>/members/add/", views.add_group_members),
    path(
        "<int:group_id>/members/<int:member_id>/",
        views.RetrieveGroupMemberView.as_view(),
    ),
    path("<int:pk>/roles/", views.RolesView.as_view()),
    path("<int:group_id>/roles/<int:pk>/", views.EditRolesView.as_view()),
]
