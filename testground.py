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

#Calcualte the total unique time measures are seen across all providers
def tot_measure_x_individuals(inputs):
    y = 0
    for i in staff_id_list:
        staff_rows = inputs[inputs["Staff_ID"] == i]
        for j in measure_list:
            measure = staff_rows[staff_rows["Measure"] == j]
            if measure.empty:
                continue
            y = y + 1
    return(y)


def parse_subjects(inputs):
    staff_id = [[] for x in range(tot_measure_x_individuals(inputs))]
    x = -1
    for i in staff_id_list: 
        staff_rows = inputs[inputs["Staff_ID"] == i].reset_index()
        for j in measure_list:
            staff_rows_by_measure = staff_rows[staff_rows["Measure"] == j].reset_index() 
            if staff_rows_by_measure.empty:
                continue
            staff_pass_percentages = staff_rows_by_measure["Pass_percentage"].tolist()
            x = x + 1
            staff_id[x].append(i)
            staff_id[x].append(staff_rows_by_measure.loc[0, "Institution_ID"])
            staff_id[x].append(staff_rows_by_measure.loc[0, "Staff_Type"])
            staff_id[x].append(staff_rows_by_measure.loc[0, "Measure"])
            staff_id[x].append(staff_pass_percentages)
    return(staff_id)

print(parse_subjects(inputs))