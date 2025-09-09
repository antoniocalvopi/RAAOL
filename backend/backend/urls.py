from django.contrib import admin
from django.urls import path, include
from pipeline.views import PipelineRunView, main_view, PipelineStreamView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pipeline/', main_view, name='main_view'),
    path("api/pipeline/run/", PipelineRunView.as_view(), name="pipeline_run"),
    path("api/pipeline/stream/", PipelineStreamView.as_view(), name="pipeline_stream"),
    path("", include("crawling.urls")),
    path("", include("collection.urls")),
    path("", include("cleaning.urls")),
    path("", include("classifying.urls")),
    path("", include("delivering.urls")),
]