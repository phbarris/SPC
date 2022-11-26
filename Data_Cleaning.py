import pandas as pd
import numpy as np

raw_data = pd.read_csv("MPOG Data Tests.csv")
raw_data = raw_data[raw_data["Denominator"] >= 30]
raw_data["Pass_percentage"] = raw_data["Passed_Count"] / raw_data["Denominator"]

list_staff_ids = raw_data["Staff_ID"].drop_duplicates()
list_measures = raw_data["Measure"].drop_duplicates()

raw_data_2 = pd.DataFrame({ })
for i in list_staff_ids:
    staff_rows = raw_data[raw_data["Staff_ID"] == i]
    for j in list_measures:
        measure_rows = staff_rows[staff_rows["Measure"] == j]
        if len(measure_rows) < 4:
            continue
        raw_data_2 = pd.concat([raw_data_2, measure_rows])

raw_data_2.to_csv("Raw_Data.csv")