import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

pd.set_option('display.max_columns', None)

#Import data
inputs = pd.read_csv("Raw_Data.csv")

#Reduce to only rows for CARD03
inputs = inputs[inputs["Measure"] == "CARD02"]

#Create a row for fail rate
inputs["Fail_Rate"] = 1 - inputs["Pass_percentage"]

##Create a list of staff role
list_staff_role = inputs["Staff_Type"].drop_duplicates()

#Create empty lists to build output dataframe from
f_list_Institution = []
f_list_Role = []
f_list_Quarters_Tracked = []
f_list_Sample_Size = []
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

#Function that takes a list with a given role and returns the p-chart for each institution
for i in list_staff_role: #For each staff role
    list_institutions = inputs["Institution_ID"].drop_duplicates() #Create a list of institutions represented
    #Create a list to hold each institution's variabe
    list_i = []
    list_sr = []
    list_m = []
    list_ss =[]
    list_fr =[]
    for j in list_institutions: #For each institution
        institution_df = inputs[inputs["Institution_ID"] == j]
        list_months = institution_df["Month"].drop_duplicates()
        
        for m in list_months: #For each month at that institution
            institution_month_df = institution_df[institution_df["Month"] == m]
            institution = j
            month = m
            sample_size = institution_month_df["Denominator"].sum()
            fail_rate = institution_month_df["Fail_Rate"].mean()
            list_i.append(institution)
            list_sr.append(i)
            list_m.append(month)
            list_ss.append(sample_size)
            list_fr.append(fail_rate)
    compiled_df = pd.DataFrame({ #Create new data frame that summarize each institution
        "Institution": list_i,
        "Staff_Role": list_sr,
        "Month": list_m,
        "Sample_Size": list_ss,
        "Fail_Rate": list_fr})

    for j in list_institutions: #For each institution, generate a control chart
        
        compiled_institution_df = compiled_df[compiled_df["Institution"] == j]
        compiled_institution_df["Month"] = pd.to_datetime(compiled_institution_df["Month"])
        compiled_institution_df = compiled_institution_df.groupby(compiled_institution_df["Month"].dt.to_period("Q")).agg({"Sample_Size": "sum",
                                                                                                                           "Fail_Rate": "mean"}).reset_index(drop=True)
        compiled_institution_df["Institution_ID"] = j
        #compiled_institution_df = compiled_institution_df[compiled_institution_df["Sample_Size"] >= 50]
        n = compiled_institution_df["Sample_Size"].sum()
        p_bar = (compiled_institution_df["Sample_Size"] * compiled_institution_df["Fail_Rate"]).sum()/compiled_institution_df["Sample_Size"].sum()
        n_bar = compiled_institution_df["Sample_Size"].mean()
        compiled_institution_df["Standard_Deviation"] = np.sqrt((p_bar * (1 - p_bar))/(compiled_institution_df["Sample_Size"]))
        compiled_institution_df["UAL"] = (p_bar + (3 * compiled_institution_df["Standard_Deviation"]))
        compiled_institution_df["LAL"] = (p_bar - (3 * compiled_institution_df["Standard_Deviation"]))
        compiled_institution_df["2UAL/3"] = (p_bar + (2 * compiled_institution_df["Standard_Deviation"]))
        compiled_institution_df["UAL/3"] = (p_bar + (compiled_institution_df["Standard_Deviation"]))
        staff_role = compiled_df["Staff_Role"][0]
        
        plt.figure(figsize=(15,6))
        plt.plot(compiled_institution_df["Fail_Rate"], label="Fail Rate")
        plt.plot(compiled_institution_df["UAL"], label="UAL")
        plt.plot(compiled_institution_df["LAL"], label="LAL")
        plt.title(str(j) + " " + str(staff_role))
        plt.axhline(y=p_bar, color='blue', linestyle='-', label="Average Fail Rate")
        leg = plt.legend()
        plt.show()
        
        ##Perform SPC functions
        #Rule 1: Point above the UAL
        compiled_institution_df["R1"] = np.where((compiled_institution_df["Fail_Rate"] > compiled_institution_df["UAL"]), 1, 0)
        rule_1_m = compiled_institution_df["R1"].sum()
        rule_1_p = False
        if rule_1_m > 0:
            rule_1_p = True
            
        #Rule 2: 2 of 3 consecutive points above or below 2 standard deviations (Zone A or beyond)
        size = len(compiled_institution_df)
        rule_2_m = 0
        rule_2_p = False
        compiled_institution_df["R2"] = np.where((compiled_institution_df["Fail_Rate"] > compiled_institution_df["2UAL/3"]), 1, 0)
        for i in range(size - 1):
            if ((compiled_institution_df["R2"][i] + compiled_institution_df["R2"][i + 1]) == 2):
            #if (compiled_institution_df["R2"][i] == 1 & compiled_institution_df["R2"][i + 1] == 1):
                rule_2_m = rule_2_m + 1
        if rule_2_m > 0:
            rule_2_p = True
       
        #Rule 3: 4 of 5 consecutive points above or below 1 standard deviations (Zone B or beyond)
        rule_3_m = 0
        rule_3_p = False
        compiled_institution_df["R3"] = np.where((compiled_institution_df["Fail_Rate"] > compiled_institution_df["UAL/3"]), 1, 0)
        for i in range(size - 3):
            if (compiled_institution_df["R3"][i] == 1 and compiled_institution_df["R3"][i + 1] == 1 and compiled_institution_df["R3"][i + 2] == 1 and compiled_institution_df["R3"][i + 3] == 1):
                rule_3_m = rule_3_m + 1
        if rule_3_m > 0:
            rule_3_p = True

        #Rule 4: 9 consecutive points fall on the same side of the centerline (Zone C or beyond
        rule_4_m = 0
        rule_4_p = False
        compiled_institution_df["R4"] = np.where((compiled_institution_df["Fail_Rate"] > p_bar), 1, 0)
        for i in range(size - 8):
            if (compiled_institution_df["R4"][i] == 1 and compiled_institution_df["R4"][i + 1] == 1 and compiled_institution_df["R4"][i + 2] == 1 and compiled_institution_df["R4"][i + 3] == 1 and compiled_institution_df["R4"][i + 4] == 1 and compiled_institution_df["R4"][i + 5] == 1 and compiled_institution_df["R4"][i + 6] == 1 and compiled_institution_df["R4"][i + 7] == 1 and compiled_institution_df["R4"][i + 8] == 1):
                rule_4_m = rule_4_m + 1
        if rule_4_m > 0:
            rule_4_p = True

        #Rule 5: Trend of 6 points in a row increasing or decreasing
        rule_5_m = 0
        rule_5_p = False
        for i in range(size-5):
            if (compiled_institution_df["Fail_Rate"][i] < compiled_institution_df["Fail_Rate"][i + 1]  < compiled_institution_df["Fail_Rate"][i + 2]  < compiled_institution_df["Fail_Rate"][i + 3]  < compiled_institution_df["Fail_Rate"][i + 4]  < compiled_institution_df["Fail_Rate"][i + 5]):
                rule_5_m = rule_5_m + 1
        if rule_5_m > 0:
            rule_5_p = True
            
        #Result cumulative of unwarrented variation
        unwarrented_variation = False
        if (rule_1_p == True or rule_2_p == True or rule_3_p == True or rule_4_p == True or rule_5_p == True):
            unwarrented_variation = True
        magnitude_variation = rule_1_m + rule_2_m + rule_3_m + rule_4_m + rule_5_m
        print(compiled_institution_df)

        #Append all values to dataframe conversion lists
        f_list_Institution.append(j)
        f_list_Role.append(staff_role)
        f_list_Quarters_Tracked.append(len(compiled_institution_df))
        f_list_Sample_Size.append(n)
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
    "Institution": f_list_Institution,
    "Staff_Role": f_list_Role,
    "Quarters_Tracked": f_list_Quarters_Tracked,
    "Sample_Size": f_list_Sample_Size,
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

       
            

