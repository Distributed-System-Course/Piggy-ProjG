from django.template import loader
from django.utils import timezone
from django.http import HttpResponse

# Create your views here.

def index(request):
    template = loader.get_template('hello/index.html')  # Relative path from the 'templates' folder to the template file
    return HttpResponse(template.render(
        {
            'title' : "Hello Django",
            'message' : "Hello Django!",
            'content' : " on " + timezone.now().strftime(("%Y/%m/%d, %H:%M:%S"))
        },
        request
    ))
