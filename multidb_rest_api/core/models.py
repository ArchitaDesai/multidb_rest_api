from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200)
    age = models.IntegerField()
    city = models.CharField(max_length=50)

    def __str__(self):
        return f'first_name: {self.first_name}, last_name:{self.last_name}, email:{self.email}, age:{self.age}, city:{self.city}'


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    salary = models.IntegerField()
    experience_years = models.IntegerField()
    company_name = models.CharField(max_length=200)

    def __str__(self):
        return f'first_name:{self.first_name}, last_name:{self.last_name}, city:{self.city}, salary:{self.salary}, experience_years:{self.experience_years}, company_name:{self.company_name}'
