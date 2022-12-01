import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import shapiro
from sklearn.preprocessing import PowerTransformer

pd.set_option('display.max_columns', 500)

# Load source csv file
inputs = pd.read_csv("Raw_Data.csv")

# Get lists of institution IDs, measures, staff roles, and staff IDs to stratify outcomes by
institution_list = inputs["Institution_ID"].drop_duplicates()
measure_list = inputs["Measure"].drop_duplicates()
staff_role_list = inputs["Staff_Type"].drop_duplicates()
staff_id_list = inputs["Staff_ID"].drop_duplicates().sort_values()

list_institutions = []
list_measures = []
list_staffrole = []
list_means = []
list_std = []
list_lcl = []
list_ucl = []
list_distribution = []

#def #yeoJohnsonTransformation(feature):
    #yeojohnTr = PowerTransformer(standardize=True)
    #df_yeojohn = pd.DataFrame(yeojohnTr.fit_transform(df[feature].values.reshape(-1,1)))

for i in institution_list:
    institution = inputs[inputs["Institution_ID"] == i]
    for j in measure_list:
        measure = institution[institution["Measure"] == j]
        for k in staff_role_list:
            staff_role = measure[measure["Staff_Type"] == k]

            mean = staff_role["Pass_percentage"].mean()
            std = staff_role["Pass_percentage"].std()
            lcl = mean - (3 * std)
            ucl = mean + (3 * std)
            if np.isnan(mean):
                continue

            stat, p = shapiro(staff_role["Pass_percentage"])
            alpha = 0.05
            distribution = False
            if p >  alpha:
                distribution = True

            

            if distribution == False:

                yeojohnTr = PowerTransformer(standardize=True)
                df_yeojohn = pd.DataFrame(yeojohnTr.fit_transform(staff_role["Pass_percentage"].values.reshape(-1,1)))
                transformed_staff_role = staff_role.reset_index()
                transformed_staff_role["Transformed"] = df_yeojohn[0]
                
                #plt.figure(figsize=(15,6))
                #plt.title(str(i) + str(j) + str(k), fontsize=15)
                #sns.histplot(transformed_staff_role["Transformed"], kde=True, color="red")
                #plt.show()

                stat, p = shapiro(transformed_staff_role["Transformed"])
                if p > alpha:
                    distribution = True
                    mean = transformed_staff_role["Transformed"].mean()
                    std = transformed_staff_role["Transformed"].std()
                    lcl = mean - (3 * std)
                    ucl = mean + (3 * std)   
                    
            list_institutions.append(i)
            list_measures.append(j)
            list_staffrole.append(k)
            list_means.append(mean)
            list_std.append(std)
            list_lcl.append(lcl)
            list_ucl.append(ucl)
            list_distribution.append(distribution)

institution_df = pd.DataFrame({
    "Institution": list_institutions, 
    "Measure": list_measures,
    "Staff_Role": list_staffrole,
    "Mean": list_means,
    "Standard_Deviation": list_std,
    "Lower_Control_Limit": list_lcl,
    "Upper_Control_Limit": list_ucl,
    "Distribution": list_distribution})



