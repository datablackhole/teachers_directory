from django.http.response import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string

# from .models import UserProfile
from django.http import Http404
from .models import Teachers, Subjects
import os
from django.core.paginator import Paginator






def search(request):
    context = list(
        Subjects.objects.filter(subject_name__icontains=request.GET['term']).order_by('subject_name').values())

    return JsonResponse(context, safe=False, )




def home(request):
    context = {}

    queryset_list = Teachers.objects.order_by('first_name')
    term = request.GET.get('term', '')

    query_filter = {}

    if 'filter' in request.GET:
        if request.GET['filter'] == 'ln':
            query_filter['last_name__istartswith'] = term
        elif request.GET['filter'] == 'subject':
            query_filter['subjects_taught__icontains'] = term
        queryset_list = queryset_list.filter(**query_filter)

    paginator = Paginator(queryset_list, 10)  # Show 5 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context['page_obj'] = page_obj

    queryset_list = list(page_obj.object_list.values())
    # print(queryset_list)

    """
        Checking if profile picture exists with respect to filename
    """
    for teacher in queryset_list:
        path = os.path.join(settings.BASE_DIR, 'media', 'photos', teacher['profile_picture'])
        print(path)
        if os.path.exists(path):
            print()
            teacher['picture_exists'] = True
        else:
            teacher['picture_exists'] = False

    # stop 

    comp_context = {'teachers': queryset_list}
    teachers_html = render_to_string('components/teacher_card.html', comp_context)

    if request.is_ajax():
        return HttpResponse(teachers_html)

    context['teachers_html'] = teachers_html

    context['values'] = request.GET

    return render(request, 'home.html', context)





def teacher(request,id):
    print(id)
    context = {}
    try:
        teacher = Teachers.objects.get(pk=id).__dict__
        del teacher['_state']
        context['profile_picture'] = teacher.pop('profile_picture')
        path = os.path.join(settings.BASE_DIR, 'media', 'photos', context['profile_picture'])
        context['picture_exists'] = os.path.exists(path)
        del teacher['id']
        for key in list(teacher):
            newKey = " ".join([e.title() for e in key.split('_')])
            teacher[newKey] = teacher.pop(key)
        context['teacher'] = teacher
    except:
        raise Http404
    return render(request, 'teacher.html', context)


