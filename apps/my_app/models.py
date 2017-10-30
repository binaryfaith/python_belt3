from __future__ import unicode_literals
from django.db import models
from datetime import datetime, date
from time import strftime
import re
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class UserManager(models.Manager):
    def add_validator(self, post_data):
        errors = []
        for key in post_data:
            if post_data[key] == "":
                errors.append("All fields must be filled")
                return errors
        date_of_birth = datetime.strptime(post_data['date_of_birth'], '%m/%d/%Y')
        now = datetime.now()
        if not post_data['name'].isalpha():
            errors.append("Name should contain only letters, no spaces")
        if not EMAIL_REGEX.match(post_data['email']):
            errors.append("Not a valid email")
        else:
            exists = self.filter(email=post_data['email'])
            if exists:
                errors.append("This email is already registered")
        if len(post_data['password']) < 8:
            errors.append("Password must be at least 8 characters long")
        if post_data['password'] != post_data['confirm_password']:
            errors.append("Password and confirmation must match")
        if date_of_birth > now:
            errors.append("I kind of doubt you were born in the future")
        return errors

    def login_validator(self, post_data):
        errors = []
        warning = "Something is wrong with email or password"
        for key in post_data:
            if post_data[key] == "":
                errors.append("All fields must be filled")
                return errors
        exists = self.filter(email=post_data['email'])
        if exists:
            if not bcrypt.checkpw(post_data['password'].encode(), exists[0].password.encode()):
                print "password nope"
                errors.append(warning)
        else:
            print "email nope"
            errors.append(warning)
        return errors

class User(models.Model):
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Appointment(models.Model):
    user_id = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()

