
from django.urls import path
from .views import NoticeList, NoticeDetailView, NoticeUpdateView, NoticeCreate, NoticeDelete, NoticeComment

urlpatterns = [
    path('', NoticeList.as_view()),
    path('announce_create', NoticeCreate.as_view()),
    path('<int:pk>', NoticeDetailView.as_view()),
    path('<int:pk>/edit', NoticeUpdateView.as_view()),
    path('<int:pk>/delete', NoticeDelete.as_view()),
    path('<int:pk>/comments', NoticeComment.as_view()),
]
