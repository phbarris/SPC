import pandas as pd
import numpy as np

from scipy.stats import shapiro

# Load source csv file
inputs = pd.read_csv("Raw_Data.csv")

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
    institution_df = pd.DataFrame(
        {"Institution": list_institutions,
        "Measure": list_measures,
        "Staff_Role": list_staffrole,
        "Mean": list_means,
        "Standard_Deviation": list_std,
        "Lower_Control_Limit": list_lcl,
        "Upper_Control_Limit": list_ucl,
        "Distribution": list_distribution})

    return(institution_df)

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

# Create a list for each staff member sperformance on an individual measure
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
            x = x + 1 #Increment after each measure
            staff_id[x].append(i) #Staff ID at [0]
            staff_id[x].append(staff_rows_by_measure.loc[0, "Institution_ID"]) # Institution ID at [1]
            staff_id[x].append(staff_rows_by_measure.loc[0, "Staff_Type"]) # Staff role at [2]
            staff_id[x].append(staff_rows_by_measure.loc[0, "Measure"]) # Measre at [3]
            staff_id[x].append(staff_pass_percentages) #serial performance data in a nested list at [4]
    return(staff_id)

institution_df = parse_institutions(inputs)
staff_performance_list = parse_subjects(inputs)

def spc(institution_df, staff_performance_list):
    #Create output variable lists
    list_Staff_ID = []
    list_Instituion = []
    list_Role = []
    list_Measure = []
    list_Time_Points_Tracked = []
    list_Distribution = []
    list_Unwarented_Variation = []
    list_Magnitude_of_Varitation = []
    list_Magnitude_of_Positive_Variation = []
    list_Magnitude_of_Negative_Variation = []
    list_Rule_1_Positive = []
    list_Rule_1_Negative = []
    list_Rule_2_Positive = []
    list_Rule_2_Negative = []
    list_Rule_3_Positive = []
    list_Rule_3_Negative = []
    list_Rule_4_Positive = []
    list_Rule_4_Negative = []
    list_Rule_5_Positive = []
    list_Rule_5_Negative = []

    ##SPC function, work in progress
    for staff_ID in staff_performance_list:
    
        #For each staff/measure on the performance list, pull the matching data from the institution_df
        matched_institution = institution_df[(institution_df["Institution"] == staff_ID[1]) & (institution_df["Measure"] == staff_ID[3]) & (institution_df["Staff_Role"] == staff_ID[2])].values.tolist() ##matches the individual in the loop to their institutions dataframe
        mean = matched_institution[0][3]
        std = matched_institution[0][4]
        lcl = matched_institution[0][5]
        ucl = matched_institution[0][6]
        distribution = matched_institution[0][7]

        pass_percentages = staff_ID[4]
        size = len(pass_percentages)

        #Rule 1: Points above the UCL or below the LCL
        rule_1_p = 0
        rule_1_n = 0
        for i in pass_percentages:
            if i > ucl:
                rule_1_p = rule_1_p + 1
            if i < lcl:
                rule_1_n = rule_1_n + 1
   
        #Rule 2: 2 of 3 consecutive points above or below 2 standard deviations (Zone A or beyond)
        rule_2_p = 0
        rule_2_n = 0
        a_p = mean + (2 * std)
        a_n = mean - (2 * std)
        for i in range(size - 1):
            if pass_percentages[i] > a_p and pass_percentages[i + 1] > a_p:
                rule_2_p = rule_2_p + 1
            if pass_percentages[i] < a_n and pass_percentages[i + 1] < a_n:
                rule_2_n = rule_2_n + 1

        #Rule 3: 4 of 5 consecutive points above or below 1 standard deviations (Zone B or beyond)
        rule_3_p = 0
        rule_3_n = 0
        b_p = mean + std
        b_n = mean - std
        for i in range(size - 3):
            if pass_percentages[i] > b_p and pass_percentages[i + 1] > b_p and pass_percentages[i + 2] > b_p and pass_percentages[i + 3] > b_p:
                rule_3_p = rule_3_p + 1
            if pass_percentages[i] < b_n and pass_percentages[i + 1] < b_n and pass_percentages[i + 2] < b_n and pass_percentages[i + 3] < b_n:
                rule_3_n = rule_3_n + 1
   
        #Rule 4: 9 consecutive points fall on the same side of the centerline (Zone C or beyond
        rule_4_p = 0
        rule_4_n = 0
        for i in range(size - 8):
            if pass_percentages[i] > mean and pass_percentages[i + 1] > mean and pass_percentages[i + 2] > mean and pass_percentages[i + 3] > mean and pass_percentages[i + 4] > mean and pass_percentages[i + 5] > mean and pass_percentages[i + 6] > mean and pass_percentages[i + 7] > mean and pass_percentages[i + 8] > mean:
                rule_4_p = rule_4_p + 1
            if pass_percentages[i] < mean and pass_percentages[i + 1] < mean and pass_percentages[i + 2] < mean and pass_percentages[i + 3] < mean and pass_percentages[i + 4] < mean and pass_percentages[i + 5] < mean and pass_percentages[i + 6] < mean and pass_percentages[i + 7] < mean and pass_percentages[i + 8] < mean:
                rule_4_n = rule_4_n + 1


        #Rule 5: Trend of 6 points in a row increasing or decreasing
        rule_5_i = 0
        rule_5_d = 0
        for i in range(size - 5):
            if pass_percentages[i] < pass_percentages[i + 1] < pass_percentages[i + 2] < pass_percentages[i + 3] < pass_percentages[i + 4] < pass_percentages[i + 5]: 
                rule_5_i = rule_5_i + 1
            if pass_percentages[i] > pass_percentages[i + 1] > pass_percentages[i + 2] > pass_percentages[i + 3] > pass_percentages[i + 4] > pass_percentages[i + 5]:
                rule_5_d = rule_5_d + 1 
    
        #Summarize unwarrented variation
        unwarrented_Variation = False
        if rule_1_n > 0 or rule_1_p > 0 or rule_2_n > 0 or rule_2_p > 0 or rule_3_n > 0 or rule_3_p > 0 or rule_4_n > 0 or rule_4_p > 0 or rule_5_d > 0  or rule_5_i > 0:
            unwarrented_Variation = True
        mag_Variation_p = rule_1_p + rule_2_p + rule_3_p + rule_4_p + rule_5_i
        mag_Variation_n = rule_1_n + rule_2_n + rule_3_n + rule_4_n + rule_5_d
        mag_Variation_tot = mag_Variation_p + mag_Variation_n

        #If distribution is not normally distributed, nullify unwarrented variation based on the mead/std
        if distribution == False:
            unwarrented_Variation = False
            mag_Variation_tot = 0
            mag_Variation_n = 0
            mag_Variation_p = 0
            rule_1_n = 0
            rule_1_p = 0
            rule_2_n = 0
            rule_2_p = 0
            rule_3_n = 0
            rule_3_p = 0
            rule_4_n = 0
            rule_4_p = 0
            rule_5_d = 0
            rule_5_i = 0

        #Append list with variables from iteration
        list_Staff_ID.append(staff_ID[0])
        list_Instituion.append(staff_ID[1])
        list_Role.append(staff_ID[2])
        list_Measure.append(staff_ID[3])
        list_Time_Points_Tracked.append(len(staff_ID[4]))
        list_Distribution.append(distribution)
        list_Unwarented_Variation.append(unwarrented_Variation)
        list_Magnitude_of_Varitation.append(mag_Variation_tot)
        list_Magnitude_of_Positive_Variation.append(mag_Variation_p)
        list_Magnitude_of_Negative_Variation.append(mag_Variation_n)
        list_Rule_1_Positive.append(rule_1_p)
        list_Rule_1_Negative.append(rule_1_n)
        list_Rule_2_Positive.append(rule_2_p)
        list_Rule_2_Negative.append(rule_2_n)
        list_Rule_3_Positive.append(rule_3_p)
        list_Rule_3_Negative.append(rule_3_n)
        list_Rule_4_Positive.append(rule_4_p)
        list_Rule_4_Negative.append(rule_4_n)
        list_Rule_5_Positive.append(rule_5_i)
        list_Rule_5_Negative.append(rule_5_d)


        spc_results_df = pd.DataFrame(
        {"Staff_ID": list_Staff_ID,
         "Institution": list_Instituion,
         "Role": list_Role,
         "Measure": list_Measure,
         "Time_Points_tracked": list_Time_Points_Tracked,
         "Distribution": list_Distribution,
         "Unwarrented_Variation": list_Unwarented_Variation,
         "Magnitude_of_Variation": list_Magnitude_of_Varitation,
         "Magnitude_of_Positive_Variation": list_Magnitude_of_Positive_Variation,
         "Magnitude_of_Negative_Variation": list_Magnitude_of_Negative_Variation,
         "Rule_1_Positive": list_Rule_1_Positive,
         "Rule_1_Negative": list_Rule_1_Negative,
         "Rule_2_Positive": list_Rule_2_Positive,
         "Rule_2_Negative": list_Rule_2_Negative,
         "Rule_3_Positive": list_Rule_3_Positive,
         "Rule_3_Negative": list_Rule_3_Negative,
         "Rule_4_Positive": list_Rule_4_Positive,
         "Rule_4_Negative": list_Rule_4_Negative,
         "Rule_5_Positive": list_Rule_5_Positive,
         "Rule_5_Negative": list_Rule_5_Negative,})

    return(spc_results_df)

spc(institution_df, staff_performance_list).to_csv("SPC_Results.csv")