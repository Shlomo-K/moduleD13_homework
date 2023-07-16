from django.db import models
from users.models import MyUser
from django.urls import reverse


class Notice(models.Model):
    GUILDS = (
        ('TK', 'Танки'),
        ('HL', 'Хилеры'),
        ('DD', 'ДД'),
        ('TD', 'Торговцы'),
        ('GM', 'Гилдмастеры'),
        ('QG', 'Квестгиверы'),
        ('BS', 'Кузнецы'),
        ('LD', 'Кожевники'),
        ('PN', 'Зельевары'),
        ('MS', 'Мастера заклинаний'),
    )

    Notice_author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    Creation_date = models.DateTimeField(auto_now_add=True)
    Notice_title = models.CharField(max_length=255)
    Notice_text = models.TextField(default='Текст объявления')
    Category = models.CharField(max_length=2, choices=GUILDS)

    def __str__(self):
        return '%s' % (self.Notice_title)


    def get_absolute_url(self):
        return reverse('notice', kwargs={'pk': self.pk})


class Files(models.Model):
    Notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    Name = models.CharField(default='file-name', max_length=255)
    File = models.FileField(upload_to='', blank=True, null=True)
    File_type = models.TextField(default='jpg')

    def save(self, *args, **kwargs):
        img_ending = {'jpg', 'png', 'img'}
        self.Name = self.File.name
        check_img = {self.Name.split(".")[-1]}
        if check_img.intersection(img_ending):
            self.File_type = 'img'
        else:
            self.File_type = 'video'
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s' % str(self.Name)


class Comments(models.Model):
    Notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    User = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    Comment = models.TextField(default='Комментарий')
    Comment_date = models.DateTimeField(auto_now_add=True)
    Comment_accepted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % str(self.Comment)


class OneTimeCode(models.Model):
    User = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    Code = models.CharField(default="", max_length=4)

    def __str__(self):
        return '%s %s' % (self.User, self.Code)
