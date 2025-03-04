from django.db import models


class DebitScroll(models.Model):
    file_number = models.CharField(max_length=50)
    type_of_pension = models.CharField(max_length=50, blank=True, null=True)
    old_ppo = models.CharField(max_length=50)
    new_ppo = models.CharField(max_length=50)
    current_pensioner = models.CharField(max_length=255)
    pension_month = models.IntegerField()
    basic_pension = models.IntegerField(default=0)
    deduction = models.IntegerField(default=0)
    fma = models.IntegerField(default=0)
    da = models.IntegerField(default=0)
    pension = models.IntegerField(default=0)
    account_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.file_number} - {self.current_pensioner}"

    class Meta:
        db_table = 'debit_scroll'


class nwr_zone_data(models.Model):
    ppo_zone_code = models.CharField(max_length=50)
    pensioner_id = models.IntegerField()
    old_ppo = models.CharField(max_length=50)
    new_ppo = models.CharField(max_length=50)
    emp_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    cessation_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    pension_amount = models.IntegerField(null=True, blank=True)
    efp_amount = models.IntegerField(null=True, blank=True)
    efp_date = models.DateField(null=True, blank=True)
    ppb_account_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.ppo_zone_code} - {self.pensioner_id}"

    class Meta:
        db_table = 'nwr_zone_data'



class NWRMasterData(models.Model):
    ppo_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    pension_start_date = models.DateField()
    date_of_retirement = models.DateField()
    age = models.IntegerField(null=True, blank=True)
    account_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.ppo_number} - {self.name}"

    class Meta:
        db_table = 'nwr_master_data'
