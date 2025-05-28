from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
# Create your views here.
@api_view(["GET"])
def home(request):
	return Response({"status": "hello"})
	
@api_view(["GET"])
def google_verify(request):
	return HttpResponse("google-site-verification: googlef10182ad33636f0c.html", content_type = "text/html")