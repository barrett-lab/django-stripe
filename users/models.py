from django.db import models
from django.contrib.auth.models import User
from PIL import Image #pip install pillow
import os
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/cu_nav.png', upload_to='profile_pics')
    # this created profile_pics dir

    def __str__(self):
        return f'{self.user.username} Profile'
    
    # -- Resize large images using pillow: saves space and loading times --
    #def save(self):
        #super().save()
    def save(self,*args, **kawrgs):
        super().save(*args, **kawrgs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

def user_directory_path(instance, filename):
    if instance.user:
        return 'user_{0}/{1}'.format(instance.user.id, filename)
    else:
        return 'shared_files/{0}'.format(filename)

class File(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)  # Use user_directory_path function
    #file_name = models.CharField(max_length=100,default="untitled")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.file.name 