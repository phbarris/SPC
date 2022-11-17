import pandas as pd
import numpy as np

# Load source csv file
inputs = pd.read_csv("test.csv")

# Get a list of institution IDs
inputs = inputs.sort_values(["Institution_ID"])
institution_list = inputs["Institution_ID"].drop_duplicates()

# Get a list of measures
measures = inputs["Measure"].drop_duplicates()

# Get a list of staff roles
staff_role = inputs["Staff_Type"].drop_duplicates()

# Collect summary data per institution-per measure-per peer group
institution_summary = [] # creates an empty list that will contain each institutions data
for i in institution_list:
    institution = inputs[inputs["Institution_ID"] == i] #separates individual institutions
    #output.to_csv("Institution" + str(i))

    #find mean, std, ucl, lcl of each institutions pass percentage
    for j in measures:
        measure = institution[institution["Measure"] == j] #separates measures per institution

        for k in staff_role:
            staff = measure[measure["Staff_Type"] == k] # separates measures per peer group
            mean = staff["Pass_percentage"].mean()
            std = staff["Pass_percentage"].std()
            lcl = -3 * std
            ucl = 3 * std

            institution_summary.append([i, j, k, mean, std, lcl, ucl])

print(institution_summary)
