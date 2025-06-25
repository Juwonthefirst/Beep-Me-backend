from celery import shared_task
from PIL import Image
from IO import BytesIO
from .models import ProfilePicture

@shared_task
def resize_and_save(image_file, user):
	file = Image.open(image_file)
	file.load()
	file.resize(512, 512)
	profile_picture = BytesIO()
	file.save(profile_picture, format = file.format)
	profile_picture.seek(0)
	
	file.resize(16, 16)
	cropped_image_file = BytesIO()
	file.save(cropped_profile_picture, format = file.format)
	cropped_image_file.seek(0)
	
	profile = ProfilePicture(file = profile_picture, thumbnail = cropped_profile_picture, uploader = user)
	profile.save()