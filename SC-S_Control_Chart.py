import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import shapiro

inputs = pd.read_csv("Raw_Data.csv")

institution_list = inputs["Institution_ID"].drop_duplicates()
measure_list = inputs["Measure"].drop_duplicates()
staff_role_list = inputs["Staff_Type"].drop_duplicates()
staff_id_list = inputs["Staff_ID"].drop_duplicates()

list_institutions = []
list_measures = []
list_staffrole = []
list_means = []
list_std = []
list_lcl = []
list_ucl = []
list_distribution = []

for i in institution_list:
    institution = inputs[inputs["Institution_ID"] == i]
    for j in measure_list:
        measure = institution[institution["Measure"] == j]
        for k in staff_role_list:
            staff_role = measure[measure["Staff_Type"] == k]
            if staff_role.empty:
                continue
            print(staff_role)





