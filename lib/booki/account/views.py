from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from django import forms

# this should probahly just list all accounts

def view_accounts(request):
    return HttpResponse("AJME MENI", mimetype="text/plain")

# signout

def signout(request):
    from django.contrib import auth

    auth.logout(request)

    return HttpResponseRedirect("/")

# signin

def signin(request):
    from django.contrib import auth

    if(request.POST.has_key("username")):
        user = auth.authenticate(username=request.POST["username"], password=request.POST["password"])

        if user:
            auth.login(request, user)
            return HttpResponseRedirect("/accounts/%s/" % request.POST["username"])
    
    return HttpResponseRedirect("/")

# register user

def register(request):
    from django.contrib.auth.models import User
    from django.contrib import auth

    user = User.objects.create_user(username=request.POST["username"], 
                                    email=request.POST["email"],
                                    password=request.POST["password"])
    user.save()

    user2 = auth.authenticate(username=request.POST["username"], password=request.POST["password"])

    auth.login(request, user2)

    return HttpResponseRedirect("/accounts/%s/" % request.POST["username"])

# project form

class ProjectForm(forms.Form):
    title = forms.CharField(required=False)
#    url_title = forms.CharField(required=True)

class ImportForm(forms.Form):
    archive_id = forms.CharField(required=False)
    
class ImportFlossForm(forms.Form):
    floss_book = forms.CharField(required=False)


def view_profile(request, username):
    from django.contrib.auth.models import User
    from booki.editor import models

    from django.template.defaultfilters import slugify

    user = User.objects.get(username=username)

    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        import_form = ImportForm(request.POST)
#        floss_form = ImportFlossForm(request.POST)

        if import_form.is_valid() and import_form.cleaned_data["archive_id"] != "":
            from booki.editor import common
            common.importBookFromURL("http://objavi.flossmanuals.net/espri.cgi?mode=zip&book="+import_form.cleaned_data["archive_id"], createTOC = True)

#        if floss_form.is_valid() and floss_form.cleaned_data["floss_book"] != "":
#            from booki.editor import common
#            common.importBookFromURL("http://objavi.flossmanuals.net/booki-twiki-gateway.cgi?server=en.flossmanuals.net&mode=zip&book="+floss_form.cleaned_data["floss_book"], createTOC = True)

        if project_form.is_valid() and project_form.cleaned_data["title"] != "":
            title = project_form.cleaned_data["title"]
            url_title = slugify(title)
#           url_title = project_form.cleaned_data["url_title"]
            

            project = models.Project(url_name = url_title,
                                  name = title,
                                  status = 0)
            project.save()

            status = models.ProjectStatus(project=project, name="not published",weight=0)
            status.save()

            import datetime

            book = models.Book(project = project,
                                         url_title = url_title,
                                         title = title,
                                         status=status,
                                         published = datetime.datetime.now())
            book.save()

            return HttpResponseRedirect("/accounts/%s/" % username)
    else:
        project_form = ProjectForm()
        import_form = ImportForm()
        floss_form = ImportFlossForm()

    books = models.Book.objects.all()

    return render_to_response('account/view_profile.html', {"request": request, "user": user, "project_form": project_form, "import_form": import_form, "floss_form": floss_form, "books": books})
