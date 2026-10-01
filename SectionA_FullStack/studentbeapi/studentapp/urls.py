from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    StudentProfileViewSet,
    DocumentViewSet,
    conversation_ask,
    create_conversation,
)
router = DefaultRouter()

router.register("profile", StudentProfileViewSet, basename="profile")
router.register("documents",DocumentViewSet, basename="documents")

urlpatterns = router.urls
urlpatterns += [
    path("conversation/ask/", conversation_ask, name="conversation_ask"),
    path("conversations/", create_conversation, name="create_conversation"),
]