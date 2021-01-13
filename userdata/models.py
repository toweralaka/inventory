from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save


# Create your models here.
TITLE = (
    ('Mr', 'Mr'),
    ('Mrs', 'Mrs'),
    ('Miss', 'Miss'),
)

class Merchant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, help_text="Business Name")
    phone_number = models.CharField(max_length=13)
    email_address = models.EmailField()
    address = models.TextField()
    liaison_officer = models.CharField(max_length=250)
    liaison_officer_salutation = models.CharField(max_length=10, choices=TITLE)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def the_merchant(self):
        return f"{self.liaison_officer_salutation} {self.liaison_officer}"

BRANCHES = (
    ('branch1', 'branch1'),
    ('branch2', 'branch2'),
    ('branch3', 'branch3'),
)

DEPARTMENT = (
    ('dept_1', 'control'),
    ('dept_2', 'kitchen'),
    ('dept_3', 'store'),
)

class Department(models.Model):
    name = models.CharField(max_length=250)
    short_code = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return self.short_code

    

class Officer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    employee_code = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=10, choices=BRANCHES)
    department = models.CharField(max_length=10, choices=DEPARTMENT)
    # department = models.ForeignKey(
    #     Department, blank=True, null=True, on_delete=models.SET_NULL
    #     )
    phone_number = models.CharField(max_length=13)
    email_address = models.EmailField()
    details = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.name} - {self.employee_code}"

    
def set_staff_receiver(sender, instance, *args, **kwargs):
    the_user = instance.user
    if not the_user.is_staff:
        the_user.is_staff = True
        the_user.save()

post_save.connect(set_staff_receiver, sender=Officer)