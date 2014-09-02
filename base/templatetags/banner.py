from django import template
from os import listdir, path
from django.conf import settings
from random import choice

register = template.Library()

@register.filter(name='bannerImage')
def bannerImage(value):
    #banner_images_path = '/Users/reedd/Dropbox/pycharm/paleoanthro_dev/static/base/home_page_images/'
    banner_images_path = path.join(path.dirname(settings.PROJECT_PATH), "static", "base", "home_page_images",)
    banner_images_names = listdir(banner_images_path)
    return choice(banner_images_names)

