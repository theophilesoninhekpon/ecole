from django.db import models
# from phonenumber_field.modelfields import PhoneNumberField

class Academic_years(models.Model):
    start = models.DateField()
    end = models.DateField()
    school_name = models.CharField(max_length=100)

class Trimestres(models.Model):
    name = models.CharField(max_length=100)

class Roles(models.Model):
    name = models.CharField(max_length=100)


class Admins(models.Model):
    phone_num = models.CharField(max_length=15)
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=6, null=True, blank=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)

class Classes(models.Model):
    name = models.CharField(max_length=20)



class Profs (models.Model):
    phone_num = models.CharField(max_length=15)
    firstname = models.CharField(max_length=100)
    code = models.CharField(max_length=6, null=True, blank=True)
    lastname = models.CharField(max_length=100)


class Matieres(models.Model):
    name = models.CharField(max_length=50)
    coef = models.IntegerField()
    classe = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, blank=True)
    prof = models.ForeignKey(Profs, on_delete=models.SET_NULL, null=True, blank=True)

class Eleves (models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    birth_date = models.DateField()
    classe = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, blank=True)

class Interros(models.Model):
    note = models.IntegerField()
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    prof = models.ForeignKey(Profs, on_delete=models.SET_NULL, null=True, blank=True)
    trimestre = models.ForeignKey(Trimestres, on_delete=models.SET_NULL, null=True, blank=True)


class Devoirs(models.Model):
    note = models.IntegerField()
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    prof = models.ForeignKey(Profs, on_delete=models.SET_NULL, null=True, blank=True)
    trimestre = models.ForeignKey(Trimestres, on_delete=models.SET_NULL, null=True, blank=True)
