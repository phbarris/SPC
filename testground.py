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

pd.set_option('display.max_columns', None)

for i in staff_id_list: 
    staff_rows = inputs[inputs["Staff_ID"] == i]
    staff_rows = staff_rows.reset_index()
    for j in measure_list:
        staff_row_by_measure = staff_rows[staff_rows["Measure"] == j].reset_index()
        print(type(staff_row_by_measure))
        print(staff_row_by_measure)
