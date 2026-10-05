from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    path(
        "course/<int:course_id>/",
        views.course_details,
        name="course_details"
    ),

    path(
        "submit/<int:lesson_id>/",
        views.submit,
        name="submit"
    ),

    path(
        "course/<int:course_id>/submission/<int:submission_id>/result/",
        views.show_exam_result,
        name="show_exam_result"
    ),
]
