from django.utils.timezone import now
from datetime import timedelta
from django.db.models.functions import TruncMonth
# from django.db.models import Sum, Count, Coalesce, Case, When, Value
from dashboard.models import nwr_zone_data  # Replace 'your_app' with your actual app name
from .models import *
from django.db.models import Min
from django.db.models import Q

# def get_pension_stats_last_6_months(month):
#     today = now().date()
#     if month
#     six_months_ago = (today.replace(day=1) - timedelta(days=180)).replace(day=1)

#     retirees_last_6_months = (
#         nwr_zone_data.objects
#         .filter(cessation_date__gte=six_months_ago, cessation_date__lte=today)
#     )

#     # ✅ Monthly Pensioner Count & Outlay
#     pension_trend_last_6_months = list(
#         retirees_last_6_months
#         .annotate(month=TruncMonth('cessation_date'))
#         .values('month')
#         .annotate(
#             total_pensioners=Count('id'),  # New pensioners added per month
#             total_pension=Sum(
#                 Case(
#                     When(pension_amount__gt=0, then="pension_amount"),
#                     When(pension_amount__isnull=True, then=Coalesce("efp_amount", Value(0))),
#                     default=Coalesce("efp_amount", Value(0))
#                 )
#             )
#         )
#         .order_by('month')
#     )

#     return {
#         "total_retirees": retirees_last_6_months.count(),
#         "pension_trend_last_6_months": pension_trend_last_6_months
#     }



# def age_metrics(month):
    
#     debit_data = DebitScroll.objects.filter(pension_month__endswith=str(month)).values('account_number', 'pension').annotate(min_pension=Min('pension'))
#     print(len(debit_data),"debit data")
#     for data in debit_data:
        
#         account_number = data['account_number']
#         if data['account_number']:
#             data['account_number'] = str(data['account_number']).split(".")[0]
#         pension = data['pension']
#     pension_data = []
#     account_numbers = {data['account_number'] for data in debit_data}
#     print(len(account_numbers))
#     # master_data = {record.account_number: record for record in NWRMasterData.objects.filter(account_number__in=account_numbers)}
#     master_data = {
#     record.account_number: record
#     for record in NWRMasterData.objects.filter(account_number__in=account_numbers, age__gte=80)}

#     print(len(master_data),"master data")

#     age_groups = {
#         "80-85": {"count": 0, "pension": 0},
#         "85-90": {"count": 0, "pension": 0},
#         "90-95": {"count": 0, "pension": 0},
#         "95-100": {"count": 0, "pension": 0},
#         "100+": {"count": 0, "pension": 0},
#     }
#     total_outlay = 0
#     total_eighty= 0
#     for data in debit_data:
#         account_number = data['account_number']
#         pension = data['pension']
        
#         # Get age from pre-fetched master data
#         master_record = master_data.get(account_number)
       
#         age = master_record.age if master_record else None
       
        
#         if age and age >= 80:
#             total_eighty+=1
#             total_outlay += pension
#             if age >= 100:
#                 age_groups["100+"]["count"] += 1
#                 age_groups["100+"]["pension"] += pension
#             elif age >= 95:
#                 age_groups["95-100"]["count"] += 1
#                 age_groups["95-100"]["pension"] += pension
#             elif age >= 90:
#                 age_groups["90-95"]["count"] += 1
#                 age_groups["90-95"]["pension"] += pension
#             elif age >= 85:
#                 age_groups["85-90"]["count"] += 1
#                 age_groups["85-90"]["pension"] += pension
#             elif age >=80:
#                 age_groups["80-85"]["count"] += 1
#                 age_groups["80-85"]["pension"] += pension
        
  
       

#     return  total_eighty,age_groups, total_outlay

def age_metrics(month):
    filtered_ds = DebitScroll.objects.filter(pension_month__endswith=str(month))
    ds_data = filtered_ds.values_list('old_ppo', 'new_ppo', 'pension')
    ppo_numbers = {old for old, new, _ in ds_data if old} 
    ppo_numbers.update({new for old, new, _ in ds_data if new}) 

  
    master_data = {
        record["ppo_number"]: record["age"]
        for record in NWRMasterData.objects.filter(ppo_number__in=ppo_numbers).values("ppo_number", "age")
    }
    age_groups = {
        "80-85": {"count": 0, "pension": 0},
        "85-90": {"count": 0, "pension": 0},
        "90-95": {"count": 0, "pension": 0},
        "95-100": {"count": 0, "pension": 0},
        "100+": {"count": 0, "pension": 0},
    }

    total_80_plus_count = 0
    total_80_plus_pension = 0

    # Process data
    for old_ppo, new_ppo, pension in ds_data:
        ppo_number = old_ppo if old_ppo in master_data else new_ppo 
        age = master_data.get(ppo_number)

        if age and age >= 80:  
            total_80_plus_count += 1
            total_80_plus_pension += pension

            if age >= 100:
                age_groups["100+"]["count"] += 1
                age_groups["100+"]["pension"] += pension
            elif age >= 95:
                age_groups["95-100"]["count"] += 1
                age_groups["95-100"]["pension"] += pension
            elif age >= 90:
                age_groups["90-95"]["count"] += 1
                age_groups["90-95"]["pension"] += pension
            elif age >= 85:
                age_groups["85-90"]["count"] += 1
                age_groups["85-90"]["pension"] += pension
            elif age >= 80:
                age_groups["80-85"]["count"] += 1
                age_groups["80-85"]["pension"] += pension

    # Return results
    response_data = {
            "success": "true",
            "data": {
                "total_amt": total_80_plus_pension,
                "total_pensioners": total_80_plus_count,
                "rule_data": age_groups
            }
        }

    return response_data


def overall_payment(month):
    
    filtered_ds = DebitScroll.objects.filter(pension_month__endswith=str(month))
    

    
    ds_data = filtered_ds.values_list('old_ppo', 'new_ppo', 'basic_pension')

    
    ds_dict = {}
    for old_ppo, new_ppo, basic_pay in ds_data:
        if old_ppo:
            ds_dict[old_ppo] = basic_pay
        if new_ppo:
            ds_dict[new_ppo] = basic_pay

  
    nwr_data = nwr_zone_data.objects.values('old_ppo', 'new_ppo', 'pension_amount', 'efp_amount')

   

    under_payment_count = 0
    under_payment_amount = 0
    over_payment_count = 0
    over_payment_amount = 0
    matched_count = 0
    unmatched_count = 0
    basic_pay_mismatch = 0

    for record in nwr_data:
        old_ppo = record['old_ppo']
        new_ppo = record['new_ppo']
        pension_amount = record['pension_amount'] if record['pension_amount'] is not None else record['efp_amount']

     
        basic_pay = ds_dict.get(old_ppo) or ds_dict.get(new_ppo)

        if basic_pay is not None:  
            matched_count += 1

            if basic_pay != pension_amount:
                basic_pay_mismatch += 1
            if basic_pay > pension_amount:
               
                over_payment_count += 1
                over_payment_amount += (basic_pay - pension_amount)
            elif basic_pay < pension_amount:
     
                under_payment_count += 1
                under_payment_amount += (pension_amount - basic_pay)
        else:
            unmatched_count += 1  
   
    response_data = {
            "success": "true",
            "data": {
                "rule_data": {
                "matched_records": matched_count,
                "basic_pay_mismatch_count": basic_pay_mismatch,
                "unlinked_records": len(ds_data)-matched_count,
                "overpayment_count": over_payment_count,
                "overpayment_amount": over_payment_amount,
                "underpayment_count": under_payment_count,
                "underpayment_amount": under_payment_amount
                }
            }
        }

    return response_data
    

def family_pension_conversion(month):
    filtered_ds = DebitScroll.objects.filter(pension_month__endswith=str(month))
    

    
    ds_data = filtered_ds.values_list('pension', 'type_of_pension')  

    regular_pension_count = 0
    family_pension_count = 0
    regular_pension_amount = 0
    family_pension_amount = 0  

    for pension, pension_type in ds_data:  
        if pension_type == 'F':
            family_pension_count += 1
            family_pension_amount += pension
        elif pension_type == 'R':
            regular_pension_count += 1
            regular_pension_amount += pension
    response_data = {
            "success": "true",
            "data": {
            "rule_data": {
            "regular_pension_count": regular_pension_count,
            "family_pension_count": family_pension_count,
            "regular_pension_amount": regular_pension_amount,
            "family_pension_amount": family_pension_amount, 
            }
            }
        }

    
    return response_data
