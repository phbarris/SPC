import pandas as pd
import numpy as np

#Build a list for each individual per measure that references their role
#[Institution, Measure, Role, ID, monthly performance......]

inputs = pd.read_csv("test.csv")

#Get a list of all staff members
staff_list = inputs["Staff_ID"].drop_duplicates()



for i in staff_list:
    staff = inputs[inputs["Staff_ID"] == i] ##Separates indviduals outs

    print(staff)
