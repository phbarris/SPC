import pandas as pd
import numpy as np

from scipy.stats import shapiro

# Load source csv file
inputs = pd.read_csv("test.csv")

# Get lists of institution IDs, measures, staff roles, and staff IDs to stratify outcomes by
institution_list = inputs["Institution_ID"].drop_duplicates()
measure_list = inputs["Measure"].drop_duplicates()
staff_role_list = inputs["Staff_Type"].drop_duplicates()
staff_id_list = inputs["Staff_ID"].drop_duplicates()

# Summarize institutional data, per measure, per peer group into a new dataframe
def parse_institutions(inputs):

    list_institutions = [] #Create lists for output variables
    list_measures = []
    list_staffrole = []
    list_means = []
    list_std = []
    list_lcl = []
    list_ucl = []
    list_distribution = []

    for i in institution_list:
        institution = inputs[inputs["Institution_ID"] == i] #separates individual institutions
        for j in measure_list:
            measure = institution[institution["Measure"] == j] #separates measures per institution
            for k in staff_role_list:
                staff_role = measure[measure["Staff_Type"] == k] # separates measures per peer group

                mean = staff_role["Pass_percentage"].mean()

                #Add values to lists
                list_institutions.append(i)
                list_measures.append(j)
                list_staffrole.append(k)
                list_means.append(mean)

    #Transform lists into dictionary for dataframe conversion
    institution_d = {
        "Institution": list_institutions,
        "Measure": list_measures,
        "Staff_Role": list_staffrole,
        "Mean": list_means
        }

    institution_df = pd.DataFrame(data= institution_d)

    return(institution_df)

print(parse_institutions(inputs))