import pandas as pd
import numpy as np

from scipy.stats import shapiro

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


# Summarize institutional data, per measure, per peer group
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
        for j in measures:
            measure = institution[institution["Measure"] == j] #separates measures per institution
            for k in staff_role:
                staff = measure[measure["Staff_Type"] == k] # separates measures per peer group

                #Calculate mean, std, lcl, and ucl per institution, per measure, per provider role
                mean = staff["Pass_percentage"].mean()
                std = staff["Pass_percentage"].std()
                lcl = mean - (3 * std)
                ucl = mean + (3 * std)

                #Is the institutional performance per measure per peer group normally distributed?
                stat, p = shapiro(staff["Pass_percentage"])
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
