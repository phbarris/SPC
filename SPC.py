import pandas as pd
import numpy as np

from scipy.stats import shapiro

# Load source csv file
inputs = pd.read_csv("test.csv")

# Get lists of institution IDs, measures, staff roles, and staff IDs to stratify outcomes by
institution_list = inputs["Institution_ID"].drop_duplicates()
measure_list = inputs["Measure"].drop_duplicates()
staff_role_list = inputs["Staff_Type"].drop_duplicates()
staff_id_list = inputs["Staff_ID"].drop_duplicates().sort_values()

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

                #Calculate mean, std, lcl, and ucl per institution, per measure, per provider role
                mean = staff_role["Pass_percentage"].mean()
                if np.isnan(mean):
                    continue
                std = staff_role["Pass_percentage"].std()
                lcl = mean - (3 * std)
                ucl = mean + (3 * std)

                #Is the institutional performance per measure per peer group normally distributed?
                stat, p = shapiro(staff_role["Pass_percentage"])
                alpha = 0.05
                distribution = False
                if p > alpha:
                    distribution = True

                #Add values to lists
                list_institutions.append(i)
                list_measures.append(j)
                list_staffrole.append(k)
                list_means.append(mean)
                list_std.append(std)
                list_lcl.append(lcl)
                list_ucl.append(ucl)
                list_distribution.append(distribution)

    #Transform lists into dictionary for dataframe conversion
    institution_d = {
        "Institution": list_institutions,
        "Measure": list_measures,
        "Staff_Role": list_staffrole,
        "Mean": list_means,
        "Standard_Deviation": list_std,
        "Lower_Control_Limit": list_lcl,
        "Upper_Control_Limit": list_ucl,
        "Distribution": list_distribution
        }

    institution_df = pd.DataFrame(data= institution_d)

    return(institution_df)

# Create an new dataframe reorganizing each row into a staff member per measure
def parse_subjects(inputs):
    staff_id = [[] for x in range(len(staff_id_list))]
    x = -1
    for i in staff_id_list:
        x = x + 1
        staff = inputs[inputs["Staff_ID"] == i]
        staff_id[x].append(int(i))
    return(staff_id)


#Statistical Process Control
#Rule 1: Points above the UCL or below the LCL
#rule_1 = 0
#if mean > ucl | mean < lcl:
    #rule_1 = rule_1 + 1
#Rule 2: 2 of 3 consecutive points above or below 2 standard deviations (Zone A or beyond)

#Rule 3: 4 of 5 consecutive points above or below 1 standard deviations (Zone B or beyond)

#Rule 4: 9 consecutive points fall on the same side of the centerline (Zone C or beyond

#Rule 5: Trend of 6 points in a row increasing or decreasing

parse_institutions(inputs).to_csv("Institution_Summary.csv")

print(parse_institutions(inputs))
print(parse_subjects(inputs))
