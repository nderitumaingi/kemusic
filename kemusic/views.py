from django.shortcuts import render, get_object_or_404, redirect
from .models import Album, Song
from .forms import AlbumForm, SongForm, UserForm
from django.views.generic import UpdateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# Create your views here.
@login_required(login_url='kemusic:login')
def index(request):
    albums = Album.objects.filter(user=request.user)
    song_results = Song.objects.all()
    query = request.GET.get("q")
    if query:
        albums = albums.filter(
            Q(album_name__icontains=query) |
            Q(artist_name__icontains=query)

        ).distinct()
        song_results = song_results.filter(
            Q(song_name__icontains=query)
        ).distinct()
        return render(request, 'kemusic/index.html', {
            'albums':  albums,
            'songs': song_results
         })
    return render(request, 'kemusic/index.html', {'albums': albums})
def detail(request,album_id):
    album = get_object_or_404(Album, pk=album_id)
    return render(request, 'kemusic/detail.html', {'album': album})


def create_album(request):
    form = AlbumForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        albums = Album.objects.filter(user=request.user)
        for album in albums:
            if album.album_name == form.cleaned_data.get('album_name'):
                context = {
                    'form': form,
                    'message': 'This album is already added',
                }
                return render(request, 'kemusic/create_album.html', context)
        album = form.save(commit=False)
        album.album_cover = request.FILES['album_cover']
        album.user = request.user
        album.save()
        return render(request, 'kemusic/detail.html', {'album': album})
    return render(request, 'kemusic/create_album.html', {'form': form})

class AlbumUpdateView(UpdateView):
    model = Album
    fields = ['album_name', 'artist_name', 'album_cover', 'album_genre']
    template_name = "kemusic/create_album.html"

def album_delete(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    album.delete()
    return redirect('/')

def create_song(request, album_id):
    form =SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=album_id)
    if form.is_valid():
        for s in album.song_set.all():
            if s.song_name == form.cleaned_data.get('song_name'):
                context = {
                    'form': form,
                    'message':'You already added that song',
                }
            return render(request, 'kemusic/create_song.html', context)
        song = form.save(commit=False)
        song.album = album
        song.song_audio = request.FILES['song_audio']
        song.save()
        context = {
            'album': album,
            'message': 'Song Created Successfully',
        }
        return render(request, 'kemusic/detail.html', context)
    return render(request, 'kemusic/create_song.html', {'form':form})

class SongUpdateView(UpdateView):
    model = Song
    fields =['song_name', 'song_audio']
    template_name = 'kemusic/create_song.html'


def delete_song(request, album_id, song_id):
    album = get_object_or_404(Album, pk=album_id)
    song = get_object_or_404(Song, pk=song_id)
    song.delete()
    context = {
        'album':album,
        'message': 'Song Deleted Successfully!'
    }
    return render(request, 'kemusic/detail.html', context)

def signup(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = form.save(commit=False)
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('kemusic:index')
    return render(request, 'registration/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        #if user.is_active:
        login(request, user)
        return redirect('kemusic:index')
        #return render(request, 'registration/login.html')
    return render(request, 'registration/login.html')


def logout_user(request):
    logout(request)
    context = {
        'message': 'logged Out!'
    }
    return redirect( 'kemusic:login')