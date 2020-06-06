from django.shortcuts import redirect, render

# Create your views here.


def welcome(request):
    return redirect('trainings-overview')
    return render(request, 'website/welcome.html')


def about(request):
    return render(request, 'website/about.html')
