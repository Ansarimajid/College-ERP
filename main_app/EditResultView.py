from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Group, Staff, Student, StudentResult
from django.urls import reverse
from django.http import JsonResponse
import json


class EditResultView(View):
    template = "staff_template/edit_student_result.html"

    def _groups(self, request):
        staff = get_object_or_404(Staff, admin=request.user)
        return Group.objects.filter(teacher=staff, is_archived=False)

    def get(self, request, *args, **kwargs):
        groups = self._groups(request)
        return render(request, self.template, {
            'groups': groups,
            'page_title': "Edit Student Result",
        })

    def post(self, request, *args, **kwargs):
        groups = self._groups(request)
        group_id = request.POST.get('group')
        student_id = request.POST.get('student')
        test = request.POST.get('test')
        exam = request.POST.get('exam')

        try:
            group = get_object_or_404(Group, id=group_id)
            student = get_object_or_404(Student, id=student_id)
            result = StudentResult.objects.get(student=student, group=group)
            result.test = float(test)
            result.exam = float(exam)
            result.save()
            messages.success(request, "Result updated successfully.")
        except StudentResult.DoesNotExist:
            messages.warning(request, "No result found for this student in the selected group.")
        except Exception as e:
            messages.warning(request, f"Could not update: {e}")

        return render(request, self.template, {
            'groups': groups,
            'page_title': "Edit Student Result",
        })
