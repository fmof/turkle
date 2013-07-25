from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader, RequestContext
from hits.models import Hit, HitTemplate


def hits_list_context(template, more_map={}):

    hit_templates = []
    for t in HitTemplate.objects.all():
        unfinished_hits = Hit.objects.filter(template=t, completed=False)
        unfinished_hits = unfinished_hits.order_by('id')

        finished_hits = Hit.objects.filter(template=t, completed=True)
        finished_hits = finished_hits.order_by('-id')

        hit_templates.append((t, unfinished_hits, finished_hits))

    c = Context(dict(hit_templates=hit_templates, **more_map))
    return template.render(c)


def index(request):
    t = loader.get_template('hits/index.html')
    return HttpResponse(hits_list_context(t))


def detail(request, hit_id):
    h = get_object_or_404(Hit, pk=hit_id)
    return render_to_response(
        'hits/detail.html',
        {'hit': h},
        context_instance=RequestContext(request)
    )


def results(request, hit_id):
    return HttpResponse("You're looking at the results of hit %s." % hit_id)


def submission(request, hit_id):
    h = get_object_or_404(Hit, pk=hit_id)
    h.completed = True
    h.answers = dict(request.POST.items())
    h.save()
    t = loader.get_template('hits/submission.html')
    return HttpResponse(hits_list_context(t, {'submitted_hit': h}))
