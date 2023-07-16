from django.test import TestCase

img_ending  = {'jpg', 'png', 'img', 'mp4'}

file_name = 'myfile.ssla.jpg.mp4'

check_img = {file_name.split(".")[-1]}

if check_img.intersection(img_ending):
    print('yes')
else:
    print('no')
