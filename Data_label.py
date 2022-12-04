import pandas as pd

column_names = ["Institution_ID", "Measure", "Staff_ID", "Staff_Type", "Month", ".", "..", "...", "....", "Pass_percentage"]

raw_data = pd.read_csv("PCRC_0088_Performance_Measures.csv", names=column_names)

raw_data.to_csv("Raw_Data.csv")