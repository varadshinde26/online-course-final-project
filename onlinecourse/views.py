from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Course, Lesson, Question, Choice, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {
            "course": course,
            "lessons": course.lessons.all()
        }
    )


@login_required
def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    questions = lesson.questions.prefetch_related("choices").all()

    score = 0
    results = []

    for question in questions:
        selected_choice_id = request.POST.get(
            f"question_{question.id}"
        )

        selected_choice = None

        if selected_choice_id:
            try:
                selected_choice = Choice.objects.get(
                    id=selected_choice_id,
                    question=question
                )
            except Choice.DoesNotExist:
                selected_choice = None

        Submission.objects.create(
            user=request.user,
            question=question,
            selected_choice=selected_choice
        )

        correct = (
            selected_choice is not None
            and selected_choice.is_correct
        )

        if correct:
            score += 1

        results.append(
            {
                "question": question,
                "selected_choice": selected_choice,
                "correct": correct,
            }
        )

    total = questions.count()

    request.session["exam_score"] = score
    request.session["exam_total"] = total
    request.session["exam_results"] = [
        {
            "question": result["question"].question_text,
            "selected": (
                result["selected_choice"].choice_text
                if result["selected_choice"]
                else "Not answered"
            ),
            "correct": result["correct"],
        }
        for result in results
    ]

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "score": score,
            "total": total,
            "results": results,
            "lesson": lesson,
        }
    )


@login_required
def show_exam_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    submissions = Submission.objects.filter(
        user=request.user,
        question__lesson=lesson
    ).select_related(
        "question",
        "selected_choice"
    )

    score = sum(
        1
        for submission in submissions
        if submission.is_correct()
    )

    total = lesson.questions.count()

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "lesson": lesson,
            "score": score,
            "total": total,
            "submissions": submissions,
        }
    )
