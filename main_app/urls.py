from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.model_form_upload, name='index'),
    path('post/ajax/translate', views.post_model_form_upload, name="post_translate"),
]
