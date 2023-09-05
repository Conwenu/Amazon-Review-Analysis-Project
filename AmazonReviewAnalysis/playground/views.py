from django.shortcuts import render, redirect
from django.http import HttpResponse
from .runIn import peaches
from .AmzReviewScraper import AmazonReviewAnalysis


def getURL(request):
    return render(request, 'MainPage.html')


def home(request):
    # html = "Please <a href=getURL> Send in your URL</a>"
    # return HttpResponse(html)
    return render(request, 'Start.html')


def showResults(request):
    if len(request.GET['givenUrl']) < 50:
        return render(request, 'Results.html')
    else:
        # Results = {}
        # Results["Average_Positive"] = 78
        # Results["Highest_Positive_Rev"] = request.GET['givenUrl']
        Results = AmazonReviewAnalysis(request.GET['givenUrl'])
        return render(request, 'Results.html', Results)
