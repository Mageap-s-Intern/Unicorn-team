from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .maper import mapping
from mapper.forms import UploadFileForm


# Create your views here.
def handle_uploaded_file(f):
    with open(f"media/input_file.xml", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def convert_xml(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['file'])
            mapping.xml_mapping('media/input_file.xml', 'mapper/maper/stop_list.csv')
            print('Файл прошел конвертацию!')
            return render(request, 'index.html', {'file': 'media/output.xml', 'form': form})
    else:
        form = UploadFileForm()

    return render(request, 'index.html', {'file': '', 'form': form})
