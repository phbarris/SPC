import pandas as pd

raw_data = pd.read_csv("PCRC_0088_Performance_Measures")

raw_data = raw_data.rename(columns={[0]:"Institution_ID", [1]:"Measure", [2]:"Staff_ID", [3]:"Staff_Type", [4]:"Month", [9]:"Pass_percentage"})

raw_data.to_csv("Raw_Data")