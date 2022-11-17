import pandas as pd
import numpy as np

# Load source csv file
inputs = pd.read_csv("test.csv")

# Get lists of institution IDs, measures, and staff roles to stratify outcomes by
## Get a list of institution IDs
inputs = inputs.sort_values(["Institution_ID"])
institution_list = inputs["Institution_ID"].drop_duplicates()
## Get a list of measures
measures = inputs["Measure"].drop_duplicates()
## Get a list of staff roles
staff_role = inputs["Staff_Type"].drop_duplicates()


# Collect summary data per institution, per measure, per peer group
def parse_institutions(inputs):

    list_institutions = [] #Create lists for output variables
    list_measures = []
    list_staffrole = []
    list_means = []
    list_std = []
    list_lcl = []
    list_ucl = []

    for i in institution_list:
        institution = inputs[inputs["Institution_ID"] == i] #separates individual institutions
        for j in measures:
            measure = institution[institution["Measure"] == j] #separates measures per institution
            for k in staff_role:
                staff = measure[measure["Staff_Type"] == k] # separates measures per peer group
                mean = staff["Pass_percentage"].mean()
                std = staff["Pass_percentage"].std()
                lcl = mean - (3 * std)
                ucl = mean + (3 * std)

                list_institutions.append(i) #Add values to lists
                list_measures.append(j)
                list_staffrole.append(k)
                list_means.append(mean)
                list_std.append(std)
                list_lcl.append(lcl)
                list_ucl.append(ucl)

                institution_d = { #transform lists into a dictionary for dataframe conversion
                    "Institution": list_institutions,
                    "Measure": list_measures,
                    "Staff_Role": list_staffrole,
                    "Mean": list_means,
                    "Standard_Deviation": list_std,
                    "Lower_Control_Limit": list_lcl,
                    "Upper_Control_Limit": list_ucl
                }

    institution_df = pd.DataFrame(data= institution_d)
    
    return(institution_df)

print(parse_institutions(inputs))
parse_institutions(inputs).to_csv("Institution_Summary.csv")
