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


class mismatch_data(models.Model):
    arpan_ppo_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=20)
    scroll_pension_type = models.CharField(max_length=10)
    arpan_pension_type = models.CharField(max_length=10)
    ppo_number = models.CharField(max_length=20)
    pensioner_name = models.CharField(max_length=255)
    scroll_acc_no = models.CharField(max_length=20)
    cessation_date = models.DateField()
    arpan_basic = models.IntegerField()
    scroll_basic = models.IntegerField()
    basic_diff = models.IntegerField()
    month = models.CharField(max_length=45)

    def __str__(self):
        return self.pensioner_name
    
    class Meta:
        db_table = "mismatch_data"




class arpan_exception(models.Model):
    debit_zone_code = models.CharField(max_length=50)  # Debit Zone Code
    debit_zone = models.CharField(max_length=100)      # Debit Zone
    bank_code = models.CharField(max_length=50)        # Bank Code
    scroll_ppo_no = models.CharField(max_length=50)    # Scroll PPO No
    account_number = models.CharField(max_length=50)   # Account Number
    pensioner_name = models.CharField(max_length=255)  # Pensioner Name
    ifsc_code = models.CharField(max_length=20)        # IFSC Code

    class Meta:
        db_table = "arpan_exception"  # Explicitly setting the DB table name

    def __str__(self):
        return f"{self.pensioner_name} - {self.scroll_ppo_no}"
    
class CommutationalData(models.Model):
    arpan_ppo_number = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    bank_ppo_number = models.CharField(max_length=50, null=True, blank=True)
    pensioner_name = models.CharField(max_length=100, null=True, blank=True)
    scroll_acc_no = models.CharField(max_length=50, null=True, blank=True)
    cessation_date = models.DateField(null=True, blank=True)
    arpan_basic = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scroll_basic = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    basic_diff = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    arpan_commutation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scroll_commutation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commutation_diff = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gen_pdf = models.CharField(max_length=20, null=True, blank=True)
    month = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'commutational_data'  # This tells Django to use the existing table name
        verbose_name = "Commutational Data"
        verbose_name_plural = "Commutational Data"

    def __str__(self):
        return f"Commutational Data for {self.pensioner_name}"