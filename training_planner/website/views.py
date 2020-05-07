from django.shortcuts import render, redirect

# Create your views here.


def welcome(request):
    return redirect('trainings-overview')
    return render(request, 'website/welcome.html')
