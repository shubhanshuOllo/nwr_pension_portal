from django.utils.timezone import now
from datetime import timedelta
from django.db.models.functions import TruncMonth
# from django.db.models import Sum, Count, Coalesce, Case, When, Value
from dashboard.models import nwr_zone_data  # Replace 'your_app' with your actual app name
from .models import *
from django.db.models import Min
from django.db.models import Q
from datetime import date
from django.db.models import Count
from django.db import connection
from django.db.models import Sum, F, Case, When, Value
import pandas as pd
from datetime import datetime




def get_pension_stats_last_6_months(main_month):
    try:
        count_zone_change = zone_change_data(main_month)
    except:
        count_zone_change = ""
    # count_zone_change = 1

    dates = {
        "September 2024": (date(2024, 9, 1), date(2024, 9, 30)),
        "August 2024": (date(2024, 8, 1), date(2024, 8, 31)),
        "July 2024": (date(2024, 7, 1), date(2024, 7, 31)),
        "June 2024": (date(2024, 6, 1), date(2024, 6, 30)),
        "May 2024": (date(2024, 5, 1), date(2024, 5, 31)),
        "April 2024": (date(2024, 4, 1), date(2024, 4, 30)),
    }
    
    stats = {}
    for month, date_range in dates.items():
        queryset = nwr_zone_data.objects.filter(cessation_date__range=date_range)
        count = queryset.count()

        # Use pension_amount, if NULL or 0, use efp_amount, if NULL, use 0
        total_pension = queryset.aggregate(
            total=Sum(
                Case(
                    When(pension_amount__gt=0, then=F('pension_amount')),
                    When(efp_amount__isnull=False, then=F('efp_amount')),
                    default=Value(0)
                )
            )
        )['total'] or 0  # Ensure result is not None

        stats[month] = {
            "count": count,
            "total_pension": total_pension,
        }
         
          
    response_data = {
        "success": "true",
        "data": {
            "rule_data": {
            "stats": stats,
            "zone_change": count_zone_change
            
            }
        }
        }


    return response_data


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
    # Define SQL query
    sql_query = f"""
        WITH matched_pensioners AS (
            SELECT ds.file_number, COALESCE(md1.age, md2.age) AS age, ds.pension
            FROM debit_scroll ds
            LEFT JOIN nwr_master_data md1 ON ds.old_ppo = md1.ppo_number
            LEFT JOIN nwr_master_data md2 ON ds.new_ppo = md2.ppo_number
            WHERE ds.pension_month = '20240{month}'
            AND COALESCE(md1.age, md2.age) IS NOT NULL
            GROUP BY ds.file_number, age, ds.pension
        )
        SELECT 
            CASE 
                WHEN age >= 100 THEN '100+'
                WHEN age >= 95 THEN '95-100'
                WHEN age >= 90 THEN '90-95'
                WHEN age >= 85 THEN '85-90'
                WHEN age >= 80 THEN '80-85'
            END AS age_group,
            COUNT(*) AS total_pensioners,
            SUM(pension) AS total_pension
        FROM matched_pensioners
        WHERE age >= 80
        GROUP BY age_group
        ORDER BY age_group;
    """

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        results = cursor.fetchall()

    # Initialize age groups
    age_groups = {
        "80-85": {"count": 0, "pension": 0},
        "85-90": {"count": 0, "pension": 0},
        "90-95": {"count": 0, "pension": 0},
        "95-100": {"count": 0, "pension": 0},
        "100+": {"count": 0, "pension": 0},
    }

    total_80_plus_count = 0
    total_80_plus_pension = 0

    # Process query results
    for age_group, count, pension in results:
        age_groups[age_group]["count"] = count
        age_groups[age_group]["pension"] = pension
        total_80_plus_count += count
        total_80_plus_pension += pension

    # Return response in the requested format
    response_data = {
        "success": "true",
        "data": {
            "rule_no": 2,
            "total_amt": total_80_plus_pension,
            "total_pensioners": total_80_plus_count,
            "rule_data": age_groups
        }
    }

    return response_data


def age_bracket(month):

    master_data = NWRMasterData.objects.all().values('ppo_number', 'account_number', 'dob')
    debit_scroll_data = DebitScroll.objects.filter(pension_month=f"2024{int(month):02d}").values("old_ppo", "new_ppo", "account_number","pension")
    debit_scroll_data_lastmonth = DebitScroll.objects.filter(pension_month=f"2024{int(month)-1:02d}").values("old_ppo", "new_ppo", "account_number","pension")
    
    
    current_month_set = {(entry["old_ppo"], entry["new_ppo"], entry["account_number"]) for entry in debit_scroll_data}
    last_month_set = {(entry["old_ppo"], entry["new_ppo"], entry["account_number"]) for entry in debit_scroll_data_lastmonth}

    last_month_identifier = set()
    for old_ppo, new_ppo, acc_num in last_month_set:
        if old_ppo:
            last_month_identifier.add(old_ppo)
        if new_ppo:
            last_month_identifier.add(new_ppo)
        if acc_num:
            last_month_identifier.add(acc_num)
    
    new_cases = [
        entry for entry in debit_scroll_data
        if entry["old_ppo"] not in last_month_identifier and 
            entry["new_ppo"] not in last_month_identifier and
            entry["account_number"] not in last_month_identifier
    ]
    zone_change_new_cases = []
    for i in new_cases:
        if i.get("old_ppo"):
            if not i.get("old_ppo").startswith("NWR") and i.get("old_ppo")[4:7] != "733":
                zone_change_new_cases.append(i)
        
    



    master_ppo_dict = {entry['ppo_number']: entry['dob'] for entry in master_data if entry['ppo_number']}
    master_acc_dict = {entry['account_number']: entry['dob'] for entry in master_data if entry['account_number']}
 
    
    turning_eighty_zone_change = 0
    turning_eighty_zone_change_overlay = 0
    eighty_plus_zone_change = 0
    eighty_plus_zone_change_overlay = 0
    reference_date = datetime.strptime(f"2024-{int(month):02d}-01", "%Y-%m-%d").date()
    for i in zone_change_new_cases:
        dob = (
            master_ppo_dict.get(i["old_ppo"]) or
            master_ppo_dict.get(i["new_ppo"]) or 
            master_ppo_dict.get(i["account_number"]) or 
            None
        )
        age = None
        if dob:
            try:
                dob_date = dob if isinstance(dob, datetime) else datetime.strptime(str(dob), "%Y-%m-%d").date()
                age_last_month = reference_date.year - dob_date.year - 1  
                age_this_month = reference_date.year - dob_date.year - ((reference_date.month, reference_date.day) < (dob_date.month, dob_date.day))  
                
                if age_last_month == 79 and age_this_month == 80:
                    turning_eighty_zone_change += 1
                    turning_eighty_zone_change_overlay += i["pension"]
                elif age_this_month > 80:
                    eighty_plus_zone_change += 1
                    eighty_plus_zone_change_overlay += i["pension"]

            except ValueError:
                print(f"Value error: Invalid DOB format -> {dob}")

    mapped_data = []
    turning_80_count = 0  
    turning_80_overlay = 0 

    for debit in debit_scroll_data:
        dob = (
            master_ppo_dict.get(debit['old_ppo']) or
            master_ppo_dict.get(debit['new_ppo']) or
            master_acc_dict.get(debit['account_number']) or
            None
        )

        age = None
        if dob:
            try:
                dob_date = dob if isinstance(dob, datetime) else datetime.strptime(str(dob), "%Y-%m-%d").date()
                age_last_month = reference_date.year - dob_date.year - 1  
                age_this_month = reference_date.year - dob_date.year - ((reference_date.month, reference_date.day) < (dob_date.month, dob_date.day))  
                
                if age_last_month == 79 and age_this_month == 80:
                    turning_80_count += 1
                    turning_80_overlay += debit["pension"]
            except ValueError:
                print(f"Value error: Invalid DOB format -> {dob}")
        

        mapped_data.append({
            "old_ppo": debit['old_ppo'],
            "new_ppo": debit['new_ppo'],
            "pension": debit['pension'],
            "account_number": debit['account_number'],
            "dob": dob
        })
    final_dict = {"turning_80_count":turning_80_count,
                  "turning_80_overlay":turning_80_overlay,
                  "eighty_plus_zone_change":eighty_plus_zone_change,
                  "eighty_plus_zone_change_overlay":eighty_plus_zone_change_overlay,
                  "turning_eighty_zone_change":turning_eighty_zone_change,
                  "turning_eighty_zone_change_overlay":turning_eighty_zone_change_overlay,
                  }
    
    return final_dict  

def commutation_data(month):
    commutation_data = CommutationalData.objects.filter(month=f"2024{int(month):02d}")
    
    total_commutation_diff = 0
    commutation_count = 0
    for i in commutation_data:
        commutation_count+=1
        total_commutation_diff += i.commutation_diff
    final_dict = {
        "commutation_cases_count": commutation_count,
        "total_commutation_diff":total_commutation_diff
    }
    response_dict = {
        "success": True,
        "data": {
            "rule_no": "10",
            "rule_data": final_dict
        }
    }
    return response_dict                                       
def comp_age_bracket():
    sept_data = age_bracket("9")
    aug_data = age_bracket("8")
    july_data = age_bracket("7")
    june_data = age_bracket("6")
    may_data = age_bracket("5")
    april_data = age_bracket("4")
    rule_data = {
        "april_data": april_data,
        "may_data": may_data,
         "june_data": june_data,
         "july_data": july_data,
        "aug_data": aug_data,
         "sept_data":sept_data,
    }
    rule_number = 8
    response_data = {
            "success": "true",
            "data": {
                "rule_no":rule_number,
                "rule_data":rule_data
            }
    }

    return response_data

def stopped_pensioner(month):
    debit_scroll_data = DebitScroll.objects.filter(pension_month=f"2024{int(month):02d}").values("old_ppo", "new_ppo", "account_number","pension")
    debit_scroll_data_lastmonth = DebitScroll.objects.filter(pension_month=f"2024{int(month)-1:02d}").values("old_ppo", "new_ppo", "account_number","pension")
    
    
    current_month_set = {(entry["old_ppo"], entry["new_ppo"], entry["account_number"]) for entry in debit_scroll_data}
    last_month_set = {(entry["old_ppo"], entry["new_ppo"], entry["account_number"]) for entry in debit_scroll_data_lastmonth}

    current_month_identifier = set()
    for old_ppo, new_ppo, acc_num in current_month_set:
        if old_ppo:
            current_month_identifier.add(old_ppo)
        if new_ppo:
            current_month_identifier.add(new_ppo)
        if acc_num:
            current_month_identifier.add(acc_num)

    stopped_cases = [
    entry for entry in debit_scroll_data_lastmonth
        if entry["old_ppo"] not in current_month_identifier and 
            entry["new_ppo"] not in current_month_identifier and
            entry["account_number"] not in current_month_identifier
        ]
    
    stopped_cases_count = len(stopped_cases)
    stopped_cases_pension_overlay = 0
    for i in stopped_cases:
        stopped_cases_pension_overlay+=i["pension"]
    
    final_dict = {"stopped_cases_count":stopped_cases_count,
                  "stopped_cases_pension_overlay":stopped_cases_pension_overlay}
    
    return final_dict


def comp_stopped_pensioner():
    sept_data = stopped_pensioner("9")
    aug_data = stopped_pensioner("8")
    july_data = stopped_pensioner("7")
    june_data = stopped_pensioner("6")
    may_data = stopped_pensioner("5")
    april_data = stopped_pensioner("4")
    rule_data = {
        "april_data": april_data,
        "may_data": may_data,
         "june_data": june_data,
         "july_data": july_data,
        "aug_data": aug_data,
         "sept_data":sept_data,
    }
    rule_no = 9
    
    response_data = {
            "success": "true",
            "data": {
                "rule_no": rule_no,
                "rule_data":rule_data
            }
    }

    return response_data

def overall_payment(month):
    
    mismatch_data_filter = mismatch_data.objects.filter(month__endswith=str(month))
    filtered_ds = DebitScroll.objects.filter(pension_month=f"20240{month}")
    unlinked_accounts = arpan_exception.objects.all()
    unlinked_accounts = arpan_exception.objects.filter(ifsc_code__icontains="SBI")
    
    mismatch_data_final = mismatch_data_filter.values_list('basic_diff', flat=True)

    under_payment_count = 0
    under_payment_amount = 0
    over_payment_count = 0
    over_payment_amount = 0

    for basic_diff in mismatch_data_final:
        if basic_diff > 0:
            over_payment_count += 1
            over_payment_amount += basic_diff
        elif basic_diff < 0:
            under_payment_count += 1
            under_payment_amount += abs(basic_diff)  

    
    matched_count = mismatch_data_filter.filter(scroll_basic__gt=0).count()
    unmatched_count = mismatch_data_filter.filter(scroll_basic=0).count()
  
    # print(len(unlinked_accounts))

    
    response_data = {
            "success": "true",
            "data": {
                "rule_no": 1,
                "rule_data": {
                "matched_records": len(filtered_ds)- len(unlinked_accounts),
                "basic_pay_mismatch_count": len(mismatch_data_final),
                "unlinked_records": len(unlinked_accounts),
                "overpayment_count": over_payment_count,
                "overpayment_amount": over_payment_amount,
                "underpayment_count": under_payment_count,
                "underpayment_amount": under_payment_amount,
               
                
                }
            }
        }

    return response_data


# def overall_payment(month):
    
#     filtered_ds = DebitScroll.objects.filter(pension_month__endswith=str(month))
    

    
#     ds_data = filtered_ds.values_list('old_ppo', 'new_ppo', 'basic_pension')

    
#     ds_dict = {}
#     for old_ppo, new_ppo, basic_pay in ds_data:
#         if old_ppo:
#             ds_dict[old_ppo] = basic_pay
#         if new_ppo:
#             ds_dict[new_ppo] = basic_pay

                                                                                                                                                          
#     nwr_data = nwr_zone_data.objects.values('old_ppo', 'new_ppo', 'pension_amount', 'efp_amount')

   

#     under_payment_count = 0
#     under_payment_amount = 0
#     over_payment_count = 0
#     over_payment_amount = 0
#     matched_count = 0
#     unmatched_count = 0
#     basic_pay_mismatch = 0
#     linked_amount = 0  # Total pension amount for linked accounts
   

#     # for record in nwr_data:
#     #     old_ppo = record['old_ppo']
#     #     new_ppo = record['new_ppo']
#     #     pension_amount = record['pension_amount'] if record['pension_amount'] is not None else record['efp_amount']

     
#     #     basic_pay = ds_dict.get(old_ppo) or ds_dict.get(new_ppo)

#     #     if basic_pay is not None:  
#     #         matched_count += 1
#     #         if pension_amount and type(pension_amount) == int:
#     #             linked_amount += pension_amount

#     #         if basic_pay != pension_amount:
#     #             basic_pay_mismatch += 1
#     #         if basic_pay > pension_amount:
               
#     #             over_payment_count += 1
#     #             over_payment_amount += (basic_pay - pension_amount)
#     #         elif basic_pay < pension_amount:
     
#     #             under_payment_count += 1
#     #             under_payment_amount += (pension_amount - basic_pay)
#     #     else:
#     #         unmatched_count += 1  
#     #         if basic_pay:
#     #             unlinked_amount += basic_pay
#     nwr_ppo_set = set()
#     nwr_pension_dict = {}
  
#     for record in nwr_data:
#         old_ppo = record['old_ppo']
#         new_ppo = record['new_ppo']
#         pension_amount = record['pension_amount'] if record['pension_amount'] is not None else record['efp_amount']

#         if old_ppo:
#             nwr_ppo_set.add(old_ppo)
#             nwr_pension_dict[old_ppo] = pension_amount
#         if new_ppo:
#             nwr_ppo_set.add(new_ppo)
#             nwr_pension_dict[new_ppo] = pension_amount

#         # Initialize counts and totals
#     matched_count = 0
#     unmatched_count = 0
#     matched_amount = 0
#     unmatched_amount = 0

#     # Loop through ds_data and check if PPO numbers exist in nwr_data
#     for old_ppo, new_ppo, basic_pay in ds_data:
#         if old_ppo in nwr_ppo_set or new_ppo in nwr_ppo_set or old_ppo in nwr_ppo_set:
#             matched_count += 1
#             linked_amount += basic_pay
            
#             if old_ppo in nwr_pension_dict:
#                 matched_amount += nwr_pension_dict[old_ppo]
#                 if basic_pay < nwr_pension_dict[old_ppo]:
#                     under_payment_count += 1
#                     under_payment_amount += (nwr_pension_dict[old_ppo] - basic_pay)
#                 elif basic_pay > nwr_pension_dict[old_ppo]:
#                     over_payment_count += 1
#                     over_payment_amount += (basic_pay - nwr_pension_dict[old_ppo])
#             elif new_ppo in nwr_pension_dict:
#                 matched_amount += nwr_pension_dict[new_ppo]
#                 if basic_pay < nwr_pension_dict[new_ppo]:
#                     under_payment_count += 1
#                     under_payment_amount += (nwr_pension_dict[new_ppo] - basic_pay)
#                 elif basic_pay > nwr_pension_dict[old_ppo]:
#                     over_payment_count += 1
#                     over_payment_amount += (basic_pay - nwr_pension_dict[old_ppo])
            
#         else:
#             unmatched_count += 1
#             unmatched_amount += basic_pay  # Since it's not in nwr, we sum the ds amount
#     print(linked_amount,"linked_amount count")
#     print(unmatched_count,"unmatched count")
   
#     response_data = {
#             "success": "true",
#             "data": {
#                 "rule_no": 1,
#                 "rule_data": {
#                 "matched_records": matched_count,
#                 "basic_pay_mismatch_count": basic_pay_mismatch,
#                 "unlinked_records": len(ds_data)-matched_count,
#                 "overpayment_count": over_payment_count,
#                 "overpayment_amount": over_payment_amount,
#                 "underpayment_count": under_payment_count,
#                 "underpayment_amount": under_payment_amount,
#                 "unlinked_amount": unmatched_amount,
#                 "linked_amount": linked_amount,
#                 }
#             }
#         }

#     return response_data
    

def family_pension_conversion(month):
    filtered_ds = DebitScroll.objects.filter(pension_month=f"20240{month}")
    
    

    
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
                "rule_no": 3,
                "rule_data": {
                "regular_pension_count": regular_pension_count,
                "family_pension_count": family_pension_count,
                "regular_pension_amount": regular_pension_amount,
                "family_pension_amount": family_pension_amount, 
                }
            }
        }

    
    return response_data

def revised_pensioners(month):
    
    zone_data_list = list(nwr_zone_data.objects.all()) 
    master_data_list = list(NWRMasterData.objects.all())

    data = {"old": 0, "new": 0, "unmatched": 0, "total": len(master_data_list)}

    old_ppo_set, new_ppo_set = set(), set()
    for obj in zone_data_list:
        old_ppo_set.add(obj.old_ppo)
        new_ppo_set.add(obj.new_ppo)

    for obj in master_data_list:
        ppo = obj.ppo_number


        if ppo in new_ppo_set:  
            data["new"] += 1  
        elif ppo in old_ppo_set:  
            data["old"] += 1  
        else:  
            data["unmatched"] += 1  

    
    
    response_data = {
            "success": "true",
            "data": {
            "rule_no": 4,
            "rule_data": {
                "new": data["new"],
                "old": data["old"],
                "unmatched": data["unmatched"],
                "total": data["total"], 
                }
            }
        }
    return(response_data)

    # # Print results
    # print(f"Total Pensioners: {total}")
    # print(f"UNmatched PPO : {unmatched}")
    # print(f"New PPO Matches: {new_ppo_match_count}")
    # print(f"Old PPO Matches: {old_ppo_match_count}")


def zone_change_data(month, year=2024):
    month = str(month).zfill(2)
    prev_month = str(int(month) - 1).zfill(2)
    prev_year = str(year)

    if month == "01":
        prev_month = "12"
        prev_year = str(int(year) - 1)


    curr_pension_month = f"{year}{month}"
    prev_pension_month = f"{prev_year}{prev_month}"

    curr_mon_ds = list(DebitScroll.objects.filter(pension_month=curr_pension_month).values())
    pre_mon_ds = list(DebitScroll.objects.filter(pension_month=prev_pension_month).values())

    pre_mon_dict = {record['new_ppo']: record['account_number'] for record in pre_mon_ds if record.get('new_ppo')}
    pre_acc_dict = {record['account_number']: record['new_ppo'] for record in pre_mon_ds if record.get('account_number')}

    matched_records = []
    unmatched_records = []

    for curr_record in curr_mon_ds:
        new_ppo = curr_record.get('new_ppo')
        old_ppo = curr_record.get('old_ppo')
        curr_acc_no = curr_record.get('account_number')

       
        if (new_ppo and new_ppo in pre_mon_dict) or (old_ppo and old_ppo in pre_mon_dict):
            matched_records.append(curr_record)
        
        elif curr_acc_no in pre_acc_dict:
            matched_records.append(curr_record)
        else:
            if new_ppo:
                if isinstance(new_ppo, float) and new_ppo.is_integer():
                    unmatched_records.append(str(int(new_ppo)))  
                else:
                    unmatched_records.append(str(new_ppo)) 

            elif old_ppo:
                if isinstance(old_ppo, float) and old_ppo.is_integer():
                    unmatched_records.append(str(int(old_ppo)))  
                else:
                    unmatched_records.append(str(old_ppo)) 

    if unmatched_records:
        unique_values = set(unmatched_records)  # Remove duplicates

        results = nwr_zone_data.objects.filter(
            Q(new_ppo__in= list(unique_values)) | Q(old_ppo__in=list(unique_values))
        ).exclude(ppo_zone_code=733)

        total_count = results.count()  # Get the count of records

        print(f"Total records found: {total_count}")


        return total_count
    else:
        return 0


# def active_pensioner(month,year=2024):
#     month = str(month).zfill(2)
#     prev_month = str(int(month) - 1).zfill(2)
#     prev_year = str(year)

#     if month == "01":
#         prev_month = "12"
#         prev_year = str(int(year) - 1)


#     curr_pension_month = f"{year}{month}"
#     prev_pension_month = f"{prev_year}{prev_month}"

#     curr_mon_ds = list(DebitScroll.objects.filter(pension_month=curr_pension_month).values())
#     pre_mon_ds = list(DebitScroll.objects.filter(pension_month=prev_pension_month).values())

#     pre_mon_dict = {record['new_ppo']: [record['account_number'],record['basic_pension'] ]for record in pre_mon_ds if record.get('new_ppo')}
#     pre_acc_dict = {record['account_number']: [record['new_ppo'],record['basic_pension']] for record in pre_mon_ds if record.get('account_number')}
    
#     matched_records = []
#     unmatched_records = []
#     un_active_pensioner = 0
#     un_active_pensioner_amt = 0
#     active_pensioner_amt = 0
#     pre_ppos = {record['new_ppo']: (record['account_number'], record['basic_pension']) for record in pre_mon_ds if record.get('new_ppo')}
#     curr_ppos = {record['new_ppo'] for record in curr_mon_ds if record.get('new_ppo')}
#     curr_old_ppos = {record['old_ppo'] for record in curr_mon_ds if record.get('old_ppo')}
#     pre_accounts = {record['account_number'] for record in pre_mon_ds if record.get('account_number')}
#     curr_accounts = {record['account_number'] for record in curr_mon_ds if record.get('account_number')}


#     missing_ppos = {
#         ppo: pension for ppo, (acc, pension) in pre_ppos.items()
#         if (ppo not in curr_ppos) and (acc not in curr_accounts) and (ppo not in curr_old_ppos) 
#     }
#     missing_ppos_count = len(missing_ppos)
#     missing_pension_amt = sum(missing_ppos.values())
#     print(missing_ppos)
#     total_pensioner = (len(list(curr_mon_ds)))
#     for curr_record in curr_mon_ds:
#         new_ppo = curr_record.get('new_ppo')
#         old_ppo = curr_record.get('old_ppo')
#         curr_acc_no = curr_record.get('account_number')
#         curr_basic_pension= curr_record.get('basic_pension')
#         curr_basic_pension= curr_record.get('basic_pension')

       
#         if new_ppo and new_ppo in pre_mon_dict:
#             key = new_ppo
#         elif old_ppo and old_ppo in pre_mon_dict:
#             key = old_ppo
#         elif curr_acc_no in pre_acc_dict:
#             key = curr_acc_no
#         else:
#             key = None

#         if (key==new_ppo or key==old_ppo) and (pre_mon_dict.get(key, [0, 0])[1] != 0) and (curr_basic_pension == 0):
            
#             un_active_pensioner += 1
#             un_active_pensioner_amt += pre_mon_dict.get(key, [0, 0])[1]
#         elif (key )and (pre_acc_dict.get(key, [0, 0])[1] != 0) and (curr_basic_pension == 0):
            
#             un_active_pensioner += 1
#             un_active_pensioner_amt += pre_acc_dict.get(key, [0, 0])[1] 
#         else:
#             active_pensioner_amt += curr_basic_pension


    

#     response_data = {
#             "success": "true",
#             "data": {
#                 "rule_no": 6,
#                 "rule_data": {
#                 "total_pensioner":total_pensioner,
#                 "count_of_un_active_pensioner": un_active_pensioner+missing_ppos_count,
#                 "count_of_active_pensioner": (total_pensioner-un_active_pensioner-missing_ppos_count),
#                 "active_pensioner_amt":active_pensioner_amt,
#                 "un_active_pensioner_amt":(un_active_pensioner_amt+missing_pension_amt)
#                 }
#             }
#         }
#     return response_data

def active_pensioner(month, year=2024):
    month = str(month).zfill(2)
    prev_month = str(int(month) - 1).zfill(2)
    prev_year = str(year)

    if month == "01":
        prev_month = "12"
        prev_year = str(int(year) - 1)

    curr_pension_month = f"{year}{month}"
    prev_pension_month = f"{prev_year}{prev_month}"

    curr_mon_ds = list(DebitScroll.objects.filter(pension_month=curr_pension_month).values())
    pre_mon_ds = list(DebitScroll.objects.filter(pension_month=prev_pension_month).values())

    pre_mon_dict = {record['new_ppo']: (record['account_number'], record['basic_pension']) for record in pre_mon_ds if record.get('new_ppo')}
    pre_acc_dict = {record['account_number']: (record['new_ppo'], record['basic_pension']) for record in pre_mon_ds if record.get('account_number')}

    curr_ppos = {record['new_ppo'] for record in curr_mon_ds if record.get('new_ppo')}
    curr_old_ppos = {record['old_ppo'] for record in curr_mon_ds if record.get('old_ppo')}
    curr_accounts = {record['account_number'] for record in curr_mon_ds if record.get('account_number')}

    missing_ppos = {
        ppo: pension for ppo, (acc, pension) in pre_mon_dict.items()
        if ppo not in curr_ppos and ppo not in curr_old_ppos and acc not in curr_accounts
    }

    missing_ppos_count = len(missing_ppos)
    missing_pension_amt = sum(missing_ppos.values())

    total_pensioner = len(curr_mon_ds)
    un_active_pensioner = 0
    un_active_pensioner_amt = 0
    active_pensioner_amt = 0

    for curr_record in curr_mon_ds:
        new_ppo = curr_record.get('new_ppo')
        old_ppo = curr_record.get('old_ppo')
        curr_acc_no = curr_record.get('account_number')
        curr_basic_pension = curr_record.get('basic_pension')

        key = new_ppo if new_ppo in pre_mon_dict else old_ppo if old_ppo in pre_mon_dict else curr_acc_no if curr_acc_no in pre_acc_dict else None

        if key:
            prev_pension_amt = pre_mon_dict.get(key, (None, 0))[1] or pre_acc_dict.get(key, (None, 0))[1]
            if prev_pension_amt != 0 and curr_basic_pension == 0:
                un_active_pensioner += 1
                un_active_pensioner_amt += prev_pension_amt
            else:
                active_pensioner_amt += curr_basic_pension

    response_data = {
        "success": "true",
        "data": {
            "rule_no": 6,
            "rule_data": {
                "total_pensioner": total_pensioner,
                "count_of_un_active_pensioner": un_active_pensioner + missing_ppos_count,
                "count_of_active_pensioner": total_pensioner - un_active_pensioner - missing_ppos_count,
                "active_pensioner_amt": active_pensioner_amt,
                "un_active_pensioner_amt": un_active_pensioner_amt + missing_pension_amt,
            }
        }
    }

    return response_data


def get_efp_count():
    df = pd.DataFrame(nwr_zone_data.objects.values('efp_amount'))  
    
    if df.empty:
        return {
            "success": "true",
            "data": {
                "rule_no": 3,
                "rule_data": {
                    "total_pensioner": 0,
                    "efp_count": 0, 
                    "efp_amt": 0, 
                    "normal_pension": 0
                }
            }
        }
    
    filtered_df = df[df['efp_amount'] != 0]
    
    # Compute required values
    epf_count = int(len(filtered_df))  # Convert to int
    total_efp_amt = int(filtered_df['efp_amount'].sum())  # Convert to int
    total_count = int(len(df))  # Convert to int
    
    # Prepare response
    response_data = {
        "success": "true",
        "data": {
            "rule_no": 3,
            "rule_data": {
                "total_pensioner": total_count,
                "efp_count": epf_count, 
                "efp_amt": total_efp_amt, 
                "normal_pension": total_count - epf_count
            }
        }
    }
    
    return response_data


def comp_overall_payment(month):
    i = month[0]
    j = month[1]
    month_comparison_dict = {}
    while i <= j:
        response = overall_payment(i)
        month_comparison_dict[i] = response["data"]["rule_data"]
        i+=1
    final_dict = {}
    final_dict = {
        "success": "True",
        "rule_data": month_comparison_dict
    }
    return final_dict


def comp_age_metrics(month):
    i = month[0]
    j = month[1]
    month_comparison_dict = {}
    while i <= j:
        response = age_metrics(i)
        month_comparison_dict[i] = response["data"]["rule_data"]
        i+=1
    final_dict = {}
    final_dict = {
        "success": "True",
        "rule_data": month_comparison_dict
    }
    return final_dict

def comp_family_pension_conversion(month):
    i = month[0]
    j = month[1]
    month_comparison_dict = {}
    while i <= j:
        response = family_pension_conversion(i)
        month_comparison_dict[i] = response["data"]["rule_data"]
        i+=1
    final_dict = {}
    final_dict = {
        "success": "True",
        "rule_data": month_comparison_dict
    }
    return final_dict
def comp_revised_pensioners(month):
    i = month[0]
    j = month[1]
    month_comparison_dict = {}
    while i <= j:
        response = revised_pensioners(i)
        month_comparison_dict[i] = response["data"]["rule_data"]
        i+=1
    return month_comparison_dict

def comp_active_pensioner(month):
    i = month[0]
    j = month[1]
    month_comparison_dict = {}
    while i <= j:
        response = active_pensioner(i)
        month_comparison_dict[i] = response["data"]["rule_data"]
        i+=1
    final_dict = {}
    final_dict = {
        "success": "True",
        "rule_data": month_comparison_dict
    }
    return final_dict
