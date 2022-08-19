from cProfile import label
from calendar import month
from django.http.response import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.views.decorators import gzip

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import cv2

import threading

from .forms import CreateUserForm

from .filters import DetectionFilter

from .models import UploadAlert

from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

from django.db.models import Count

from django.db.models.functions import ExtractDay

import datetime

import itertools



# Handles the registration page
def registerPage(request):

	if request.user.is_authenticated:
		return redirect('home')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was successfully created for ' + user)

				return redirect('login')

		context = {'form':form}
		return render(request, 'detection/register.html', context)

# Handles the login page
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user) 
				return redirect('home')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'detection/login.html', context)

# Handles the logout
def logoutUser(request):
	logout(request)
	return redirect('login')

# Handles the dashboard page
@login_required(login_url='login')
def home(request):

	year = datetime.datetime.now().year
	month = datetime.datetime.now().month

	token = Token.objects.get(user=request.user)

	uploadAlert = UploadAlert.objects.filter(user_ID = token).order_by('-id')

	page_num  = request.GET.get('page',1)

	paginator = Paginator(uploadAlert,4)

	no_alerts = UploadAlert.objects.count()

	user = get_user_model()


	users = user.objects.all().count()

	pie_label = ['Detections','Alerts']
	pie_data = [no_alerts,no_alerts]

	myFilter = DetectionFilter(request.GET, queryset=uploadAlert)
	uploadAlert = myFilter.qs 

	# qsty = UploadAlert.objects.filter('date_created')

	# qst = UploadAlert.objects.values('date_created').annotate(count=Count('pk'))

	qst = UploadAlert.objects.values('date_created')

	var2 = itertools.groupby(qst,lambda x : x.get('date_created').strftime('%d  %B'))

	day_month = [(a,len(list(b))) for a,b in var2 ]

	print(day_month)

	label = []
	data = []

	counter = 0

	for k, v in day_month:

		if counter <= 7:
			label.append(k)
			data.append(v)
			counter = counter + 1
		else:
			break





	print(label)
	print(data)

	

	try:
		page_obj = paginator.page(page_num)

	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	context = {'myFilter':myFilter, 'uploadAlert':uploadAlert,'no_alerts':no_alerts, 'users':users, 'page_obj': page_obj, 'day_month':day_month,'data':data,'label':label,'pie_label':pie_label,'pie_data':pie_data}

	return render(request, 'detection/dashboard.html', context)



class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def livefeed(request):
		try:
			cam = VideoCamera()
			return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
		except Exception as e: 
			print(e)
		return render(request, 'detection/cam.html')


def alert(request, pk):

	uploadAlert = UploadAlert.objects.filter(image = str(pk) + ".jpg")

	myFilter = DetectionFilter(request.GET, queryset=uploadAlert)
	uploadAlert = myFilter.qs 

	context = {'myFilter':myFilter, 'uploadAlert':uploadAlert}

	return render(request, 'detection/alert.html', context)