import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

pd.set_option('display.max_columns', None)

#Import data
inputs = pd.read_csv("Raw_Data.csv")

#Reduce to only rows for CARD03
inputs = inputs[inputs["Measure"] == "BP01"]

#Create a row for fail rate
inputs["Fail_Rate"] = 1 - inputs["Pass_percentage"]

##Create a dataframe for each staff role
attending = inputs[inputs["Staff_Type"] == "Attending"]
resident = inputs[inputs["Staff_Type"] == "Resident"]
crna = inputs[inputs["Staff_Type"] == "CRNA"]

#Function that takes a list with a given role and returns the p-chart for each institution
def spc(role):
    list_institutions = role["Institution_ID"].drop_duplicates()
    list_i = []
    list_m = []
    list_ss =[]
    list_fr =[]
    for i in list_institutions:
        institution_df = role[role["Institution_ID"] == i]
        list_months = institution_df["Month"].drop_duplicates()
        
        for m in list_months:
            institution_month_df = institution_df[institution_df["Month"] == m]
            institution = i
            month = m
            sample_size = institution_month_df["Denominator"].sum()
            fail_rate = institution_month_df["Fail_Rate"].mean()
            list_i.append(institution)
            list_m.append(month)
            list_ss.append(sample_size)
            list_fr.append(fail_rate)
    compiled_df = pd.DataFrame({ #Create new data frame that summarize each institution
        "Institution": list_i,
        "Month": list_m,
        "Sample_Size": list_ss,
        "Fail_Rate": list_fr})
    for i in list_institutions: #For each institution, generate a control chart
        compiled_institution_df = compiled_df[compiled_df["Institution"] == i]
        compiled_institution_df = compiled_institution_df[compiled_institution_df["Sample_Size"] >= 50]
        p_bar = (compiled_institution_df["Sample_Size"] * compiled_institution_df["Fail_Rate"]).sum()/compiled_institution_df["Sample_Size"].sum()
        n_bar = compiled_institution_df["Sample_Size"].mean()
        compiled_institution_df["Standard_Deviation"] = np.sqrt((p_bar * (1 - p_bar))/(compiled_institution_df["Sample_Size"]))
        compiled_institution_df["UAL"] = (p_bar + (3 * compiled_institution_df["Standard_Deviation"]))
        compiled_institution_df["LAL"] = (p_bar - (3 * compiled_institution_df["Standard_Deviation"]))

        plt.figure(figsize=(15,6))
        plt.plot(compiled_institution_df["Month"], compiled_institution_df["Fail_Rate"], label="Fail Rate")
        plt.plot(compiled_institution_df["Month"], compiled_institution_df["UAL"], label="UAL")
        plt.plot(compiled_institution_df["Month"], compiled_institution_df["LAL"], label="LAL")
        plt.title(str(i))
        plt.axhline(y=p_bar, color='blue', linestyle='-', label="Average Fail Rate")
        leg = plt.legend()
        plt.show()
        print(p_bar)
        print(compiled_institution_df["UAL"])

spc(crna)
            
            

