from django.shortcuts import render
from dkconsole.data.models import Tub
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse, Http404, FileResponse

from .services import TubService
from .serializers import TubSerializer, TubImageSerializer, MetaSerializer
from rest_framework.decorators import api_view
import os
from pathlib import Path
from django.conf import settings
from PIL import Image

import os
from dkconsole.util import *

# Create your views here.


@api_view(['GET'])
def index(request):

    # for name in os.listdir(tub_path()):
    #     print(name)
    tubs = TubService.get_tubs()

    serializer = TubSerializer(tubs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def tub_archive(request, tub_name):
    tub_paths = [Path(settings.DATA_DIR) / tub_name]
    archive_path = TubService.generate_tub_archive(tub_paths)

    if os.path.exists(archive_path):
        with open(archive_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/gzip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(archive_path)
            return response
    raise Http404


@api_view(['POST'])
def delete(request):
    try:
        tub_path = request.data['tub_path']

        TubService.delete_tub(tub_path)

        return Response({"success": True})
    except Exception as e:
        print(e)
        return Response({"success": False})


@api_view(['GET'])
def jpg(request, tub_name, filename):
    '''
    http://localhost:8000/data/tub_9_20-01-10/1_cam-image_array_.jpg
    '''
    try:
        image_file_path = Path(settings.DATA_DIR) / tub_name / filename

        # 192.168.0.76

        return FileResponse(open(image_file_path, 'rb'))

        # with open(image_file_path, "rb") as f:
        #     return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        # with open(get_no_image_path(), "rb") as f:
        #     return HttpResponse(f.read(), content_type="image/png")

        return FileResponse(open(get_no_image_path(), 'rb'))


def get_no_image_path():
    return os.path.dirname(__file__) + "/static/no_image.png"


@api_view(['POST'])
def delete_tubs(request):
    try:
        number_of_images = request.data['number_of_images']

        TubService.delete_tubs(number_of_images)

        return Response({"success": True})
    except Exception as e:
        print(e)
        return Response({"success": False})


def stream_video(request, tub_name):
    path = str(TubService.gen_movie(tub_name))
    resp = video_stream(request, path)
    return resp


@api_view(['GET'])
def detail(requst, tub_name):
    tub = TubService.get_detail(tub_name)
    serializer = TubSerializer(tub)
    return Response(serializer.data)


@api_view(['GET'])
def latest(requst):
    latest = TubService.get_latest()
    # tub = TubService.get_detail(TubService.get_latest())
    print(latest)
    serializer = TubSerializer(latest)
    return Response(serializer.data)


@api_view(['GET'])
def histogram(requst, tub_name):
    '''
    http://localhost:8000/data/tub_9_20-01-10/tub_9_20-01-10_hist.png
    '''
    try:
        TubService.gen_histogram(Path(settings.DATA_DIR) / tub_name)
        histogram_name = tub_name + "_hist.png"
        image_file_path = Path(settings.DATA_DIR) / tub_name / histogram_name
        return FileResponse(open(image_file_path, 'rb'))
    except:
        return FileResponse(open(get_no_image_path(), 'rb'))


@api_view(['GET'])
def latest_histogram(requst):
    '''
    http://localhost:8000/data/tub_9_20-01-10/tub_9_20-01-10_hist.png
    '''
    try:
        latest = TubService.get_latest()
        TubService.gen_histogram(Path(settings.DATA_DIR) / latest.name)
        histogram_name = latest.name + "_hist.png"
        image_file_path = Path(settings.DATA_DIR) / latest.name / histogram_name
        return FileResponse(open(image_file_path, 'rb'))
    except:
        return FileResponse(open(get_no_image_path(), 'rb'))


@api_view(['GET'])
def show_meta(request, tub_name):
    meta = TubService.get_meta(tub_name)
    serializer = MetaSerializer(meta)
    return Response(serializer.data)


@api_view(['POST'])
def update_meta(request, tub_name):
    '''
    {"update_parms":["123: 123"]}
    '''
    data = request.data["update_parms"]

    if (data):
        # Transform the input param. Input param should not be a string. It should be a dict. Let's fix this later

        update_parms = dict([i.split(':') for i in data])
        TubService.update_meta(tub_name, update_parms)
        return Response({"success": True})
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
