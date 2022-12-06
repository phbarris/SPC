import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

#Import data
inputs = pd.read_csv("Raw_Data.csv")

#Reduce to only rows for CARD03
inputs = inputs[inputs["Measure"] == "BP01"]

#Create a row for fail rate
inputs["Fail_Rate"] = 1 - inputs["Pass_percentage"]

#Create lists of institutions and staff role
list_institutions = inputs["Institution_ID"].drop_duplicates()
list_staff_role = inputs["Staff_Type"].drop_duplicates()

#Create empty lists to build output dataframe from
f_list_Staff_ID = []
f_list_Institution = []
f_list_Role = []
f_list_Quarters_Tracked = []
f_list_Unwarrented_Variation = []
f_list_Magnitude_of_Variation = []
f_Rule_1_Positive = []
f_Rule_1_Magnitude = []
f_Rule_2_Positive = []
f_Rule_2_Magnitude = []
f_Rule_3_Positive = []
f_Rule_3_Magnitude = []
f_Rule_4_Positive = []
f_Rule_4_Magnitude = []
f_Rule_5_Positive = []
f_Rule_5_Magnitude = []

##Loop each institution down tojust the CARD03 measures among that institution's staff role
for i in tqdm(list_institutions):
    institution = inputs[inputs["Institution_ID"] == i]
    for j in list_staff_role:
        staff_role = institution[institution["Staff_Type"] == j]
        inst_Staff = pd.DataFrame({
            "Staff_ID": staff_role["Staff_ID"],
            "Month": staff_role["Month"],
            "Sample_Size": staff_role["Denominator"],
            "Fail_Rate": staff_role["Fail_Rate"]})
        
        list_staff_id = inst_Staff["Staff_ID"].drop_duplicates()
        for k in tqdm(list_staff_id):
            staff_id = inst_Staff[inst_Staff["Staff_ID"] == k]
            staff_id["Month"] = pd.to_datetime(staff_id["Month"])
            staff_id = staff_id.groupby(staff_id["Month"].dt.to_period("Q")).agg({"Sample_Size": "sum",                                                                       "Fail_Rate": "mean"}).reset_index(drop=True)
            staff_id["Staff_ID"] = k
            #Drop rows with n <50
            #staff_id = staff_id[staff_id["Sample_Size"] >= 50]
            #Calculate p_bar
            p_bar = staff_id["Fail_Rate"].mean()
            #Calculate n_bar
            n_bar = staff_id["Sample_Size"].mean()
            #Calculate standard deviation column
            staff_id["Standard_Deviation"] = np.sqrt((p_bar * (1 - p_bar))/(staff_id["Sample_Size"]))
            #Calculate UAL and LAL columns
            staff_id["UAL"] = (p_bar + 3 * staff_id["Standard_Deviation"])
            staff_id["LAL"] = (p_bar - 3 * staff_id["Standard_Deviation"])
            staff_id['LAL'] = np.where(staff_id['LAL'] < 0, 0, staff_id['LAL'])
            staff_id["2UAL/3"] = staff_id["UAL"] * (2/3)
            staff_id["UAL/3"] = staff_id["UAL"] / 3

            print("iteratre:")
            
            #Demonstrate plots showing p-charts
            #plt.figure(figsize=(15,6))
            #plt.plot(staff_id["Fail_Rate"], label="Fail Rate")
            #plt.plot(staff_id["UAL"], label="UAL")
            #plt.plot(staff_id["LAL"], label="LAL")
            #plt.title(str(i) + " " + str(j) + " " + str(k))
            #plt.axhline(y=p_bar, color='blue', linestyle='-', label="Average Fail Rate")
            #leg = plt.legend()
            #plt.show()

            ##Perform SPC functions
            #Rule 1: Point above the UAL
            staff_id["R1"] = np.where((staff_id["Fail_Rate"] > staff_id["UAL"]), 1, 0)
            rule_1_m = staff_id["R1"].sum()
            rule_1_p = False
            if rule_1_m > 0:
                rule_1_p = True
            
            #Rule 2: 2 of 3 consecutive points above or below 2 standard deviations (Zone A or beyond)
            size = len(staff_id)
            rule_2_m = 0
            rule_2_p = False
            staff_id["R2"] = np.where((staff_id["Fail_Rate"] > staff_id["2UAL/3"]), 1, 0)
            for i in range(size - 1):
                if (staff_id["R2"][i] == 1 & staff_id["R2"][i + 1] == 1):
                    rule_2_m = rule_2_m + 1
            if rule_2_m > 0:
                rule_2_p = True

            #Rule 3: 4 of 5 consecutive points above or below 1 standard deviations (Zone B or beyond)
            rule_3_m = 0
            rule_3_p = False
            staff_id["R3"] = np.where((staff_id["Fail_Rate"] > staff_id["UAL/3"]), 1, 0)
            for i in range(size - 3):
                if (staff_id["R3"][i] == 1 & staff_id["R3"][i + 1] == 1 & staff_id["R3"][i + 2] == 1 & staff_id["R3"][i + 3] == 1):
                    rule_3_m = rule_3_ + 1
            if rule_3_m > 0:
                rule_3_p = True

            #Rule 4: 9 consecutive points fall on the same side of the centerline (Zone C or beyond
            rule_4_m = 0
            rule_4_p = False
            staff_id["R4"] = np.where((staff_id["Fail_Rate"] > p_bar), 1, 0)
            for i in range(size - 8):
                if (staff_id["R4"][i] == 1 & staff_id["R4"][i + 1] == 1 & staff_id["R4"][i + 2] == 1 & staff_id["R4"][i + 3] == 1 & staff_id["R4"][i + 4] == 1 & staff_id["R4"][i + 5] == 1 & staff_id["R4"][i + 6] == 1 & staff_id["R4"][i + 7] == 1 & staff_id["R4"][i + 8] == 1):
                    rule_4_m = rule_4_m + 1
            if rule_4_m > 0:
                rule_4_p = True

            #Rule 5: Trend of 6 points in a row increasing or decreasing
            rule_5_m = 0
            rule_5_p = False
            for i in range(size-5):
                if (staff_id["Fail_Rate"][i] < staff_id["Fail_Rate"][i + 1]  < staff_id["Fail_Rate"][i + 2]  < staff_id["Fail_Rate"][i + 3]  < staff_id["Fail_Rate"][i + 4]  < staff_id["Fail_Rate"][i + 5]):
                    rule_5_m = rule_5_m + 1
            if rule_5_m > 0:
                rule_5_p = True
            
            #Result cumulative of unwarrented variation
            unwarrented_variation = False
            if (rule_1_p == True | rule_2_p == True | rule_3_p == True | rule_4_p == True | rule_5_p == True):
                unwarrented_variation = True
            magnitude_variation = rule_1_m + rule_2_m + rule_3_m + rule_4_m + rule_5_m


            #Append all values to dataframe conversion lists
            f_list_Staff_ID.append(k)
            f_list_Institution.append(i)
            f_list_Role.append(j)
            f_list_Quarters_Tracked.append(len(staff_id))
            f_list_Unwarrented_Variation.append(unwarrented_variation)
            f_list_Magnitude_of_Variation.append(magnitude_variation)
            f_Rule_1_Positive.append(rule_1_p)
            f_Rule_1_Magnitude.append(rule_1_m)
            f_Rule_2_Positive.append(rule_2_p)
            f_Rule_2_Magnitude.append(rule_2_m)
            f_Rule_3_Positive.append(rule_3_p)
            f_Rule_3_Magnitude.append(rule_3_m)
            f_Rule_4_Positive.append(rule_4_p)
            f_Rule_4_Magnitude.append(rule_4_m)
            f_Rule_5_Positive.append(rule_5_p)
            f_Rule_5_Magnitude.append(rule_5_m)
            
#Create a resulting dataframe
output_df = pd.DataFrame({
    "Staff_ID": f_list_Staff_ID,
    "Institution": f_list_Institution,
    "Staff_Role": f_list_Role,
    "Quarters_Tracked": f_list_Quarters_Tracked,
    "Unwarrented_Variation_Present": f_list_Unwarrented_Variation,
    "Magnitude_of_Unwarrented_Variation":f_list_Magnitude_of_Variation,
    "Rule_1_Present": f_Rule_1_Positive,
    "Rule_1_Magnitude": f_Rule_1_Magnitude,
    "Rule_2_Present": f_Rule_2_Positive,
    "Rule_2_Magnitude": f_Rule_2_Magnitude,
    "Rule_3_Present": f_Rule_3_Positive,
    "Rule_3_Magnitude": f_Rule_3_Magnitude,
    "Rule_4_Present": f_Rule_4_Positive,
    "Rule_4_Magnitude": f_Rule_4_Magnitude,
    "Rule_5_Present": f_Rule_5_Positive,
    "Rule_5_Magnitude": f_Rule_5_Magnitude,
    })

output_df.to_csv("SPC_Results.csv")

       
