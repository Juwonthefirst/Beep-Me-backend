from celery import shared_task
from PIL import Image
from io import BytesIO


# @shared_task
# def resize_and_save(image_file, user):
#     file = Image.open(image_file)
#     file.load()
#     file.resize(512, 512)
#     profile_picture = BytesIO()
#     file.save(profile_picture, format=file.format)
#     profile_picture.seek(0)

#     file.resize(16, 16)
#     cropped_profile_picture = BytesIO()
#     file.save(cropped_profile_picture, format=file.format)
#     cropped_profile_picture.seek(0)

#     profile = ProfilePicture(
#         file=profile_picture, thumbnail=cropped_profile_picture, uploader=user
#     )
#     profile.save()
