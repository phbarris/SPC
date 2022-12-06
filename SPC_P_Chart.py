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
        
        #Drop rows with n <50
        inst_Staff = inst_Staff[inst_Staff["Sample_Size"] >= 50]
        print(inst_Staff)
        #Calculate p_bar
        p_bar = inst_Staff["Fail_Rate"].mean()
        #Calculate n_bar
        n_bar = inst_Staff["Sample_Size"].mean()
        #Calculate standard deviation column
        inst_Staff["Standard_Deviation"] = ((p_bar * (1 - p_bar))/(inst_Staff["Sample_Size"]))
        #Calculate UAL and LAL columns
        inst_Staff["UAL"] = (p_bar + 3 * inst_Staff["Standard_Deviation"])
        inst_Staff["LAL"] = (p_bar - 3 * inst_Staff["Standard_Deviation"])

        ##Separate out for each Staff_ID at the institution/role
        list_staff_id = inst_Staff["Staff_ID"].drop_duplicates()
        for k in tqdm(list_staff_id):
            staff_id = inst_Staff[inst_Staff["Staff_ID"] == k]
            #Demonstrate plots showing p-charts
            plt.figure(figsize=(15,6))
            plt.plot(staff_id["Month"], staff_id["Fail_Rate"], label="Fail Rate")
            plt.plot(staff_id["Month"], staff_id["UAL"], label="UAL")
            plt.plot(staff_id["Month"], staff_id["LAL"], label="LAL")
            plt.title(str(i) + " " + str(j) + " " + str(k))
            plt.axhline(y=p_bar, color='blue', linestyle='-', label="Average Fail Rate")
            leg = plt.legend()
            plt.show()
            #print(staff_ID)




       
