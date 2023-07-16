
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Notice, Files, Comments, MyUser, OneTimeCode
from .forms import NoticeForm, InputForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .filters import PostFilter


def home_view(request):
    context = {}
    context['form'] = InputForm()
    if request.method == 'POST':
        form = InputForm(request.POST)
        if request.user.is_authenticated:
            logout(request)
            return render(request, "home.html", context)
        if form.is_valid():
            data = {}
            data['invalid_login'] = False
            user = authenticate(
                username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('announce/')
                else:
                    return render(request, 'home.html', context)
            else:
                return render(request, 'home.html', context)
        else:
            return render(request, "home.html", context)

    return render(request, "home.html", context)


@login_required(login_url='/')
def register_code_view(request):
    context = {}

    if request.method == 'POST' and request.POST.get('Activate') != '':
        
        OneTimeCodeObj = OneTimeCode.objects.filter(
            User=request.user, Code=request.POST.get('Activate'))
        if OneTimeCodeObj.exists():
            UserObject = MyUser.objects.filter(id=request.user.id)[0]
            UserObject.enabled = True
            UserObject.save()
            OneTimeCodeObj.delete()
            return redirect('/')

    return render(request, "account/register_code.html", context)


class ConfirmedUserMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.enabled:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(register_code_view)


class NoticeCreate(LoginRequiredMixin, ConfirmedUserMixin, CreateView):
    login_url = '/'
    model = Notice
    template_name = 'announce/announce_create.html'
    fields = ['Notice_title', 'Notice_text', 'Category']

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            AnnounceObj = Notice.objects.create(
                Notice_author=request.user,
                Notice_title=request.POST['Notice_title'],
                Notice_text=request.POST['Notice_text'],
                Category=request.POST['Category']
            )

            myFiles = request.FILES.getlist('files')
            if myFiles is not None and len(myFiles) > 0:

                for file in myFiles:
                    fileObj = Files.objects.create(
                        Notice=AnnounceObj, Name=file.name, File=file)
                    fileObj.save()

        return redirect('/announce/')


class NoticeList(ListView):

    model = Notice
    template_name = 'notice/notice.html'
    context_object_name = 'Notice'
    ordering = ['-Creation_date']
    paginate_by = 10
    form_class = NoticeForm
    queryset = Notice.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NoticeDetailView(DetailView):

    model = Notice
    template_name = 'notice/notice_detail.html'
    context_object_name = 'Notice'
    queryset = Notice.objects.all()

    def get_object(self):
        obj = super().get_object(queryset=self.queryset)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = NoticeForm()

        objFiles = Files.objects.filter(Notice=self.object)
        data = []
        for file in objFiles:
            file_data = {'name': file.Name,
                         'type': file.File_type}

            data.append(file_data)

        context['dataFiles'] = data

        objComments = Comments.objects.filter(
            Notice=self.object, Comment_accepted=True)
        data = []
        for comment in objComments:
            data.append(comment)

        context['comments'] = data

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(home_view)
        if not request.user.is_superuser:
            if not request.user.enabled:
                return redirect(register_code_view)
        self.object = self.get_object()
        if request.method == 'POST':
            buttonAddCommentPressed = request.POST.get("AddComment")
            if buttonAddCommentPressed is not None and request.POST.get('CommentArea') != "":
                commentObj = Comments.objects.create(
                    Notice=self.object, User=request.user, Comment=request.POST.get('CommentArea'))
                commentObj.save()

            return redirect('/notice/' + str(kwargs['pk']))


class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    model = Notice
    template_name = 'notice/notice_edit.html'
    form_class = NoticeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notice_files'] = Files.objects.filter(
            Notice=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        if request.method == 'POST':
            buttonDeletePressed = request.POST.get("Delete")
            if buttonDeletePressed is not None:
                Files.objects.filter(Notice=self.object, File=Files.objects.get(
                    id=int(buttonDeletePressed))).delete()
                return redirect('/notice/' + str(kwargs['pk']) + '/edit')
            form = NoticeForm(request.POST)
            if form.is_valid():
                files = request.FILES.getlist('files')
                for file in files:
                    fileObj = Files.objects.create(
                        Notice=self.object, Name=file.name, File=file)
                    fileObj.save()

                self.object.save()
                return redirect('/notice/' + str(kwargs['pk']))
            else:
                context['form'] = NoticeForm()

        return self.render_to_response(context)


class NoticeDelete(LoginRequiredMixin, DeleteView):
    login_url = '/'
    model = Notice
    template_name = 'notice/notice_delete.html'
    success_url = "/notice/"


class NoticeComment(LoginRequiredMixin, ConfirmedUserMixin, ListView):
    login_url = '/'
    model = Comments
    template_name = 'notice/notice_comments.html'
    context_object_name = 'Comments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['AllComments'] = True
        context['myfilter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        if len(self.kwargs) > 0:
            context['Notice'] = Notice.objects.get(
                id=str(self.kwargs['pk']))
            context['AllComments'] = False
        return context

    def get_queryset(self):
        if "announce" not in self.request.path:
            Posts = Notice.objects.filter(
                Notice_author=self.request.user)
            queryset = Comments.objects.filter(
                Notice__in=Posts, Comment_accepted=False)
        else:
            queryset = Comments.objects.filter(Notice=Notice.objects.get(
                id=str(self.kwargs['pk'])), Comment_accepted=False)
        return queryset

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            pk = None
            buttonAcceptPressed = request.POST.get("Accept")
            buttonDeniedPressed = request.POST.get("Denied")
            if buttonAcceptPressed is not None:
                objComment = Comments.objects.get(id=buttonAcceptPressed)
                objComment.Comment_accepted = True
                objComment.save()
                pk = objComment.Notice_id
            elif buttonDeniedPressed is not None:
                objComment = Comments.objects.get(id=buttonDeniedPressed)
                pk = objComment.Notice_id
                objComment.delete()
            else:
                pass

            if pk is not None:
                return redirect('/notice/' + str(pk) + "/comments")
            else:
                return redirect('/notice/' + str(kwargs['pk']) + "/comments")
