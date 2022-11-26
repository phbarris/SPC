# Statistical Process Control Function

## About

This program assess for special cause variation using statistical process control methods (SPC). The type of data this function works with includes sample data with measurements across multiple time points. Sample data can be stratified into unique identifiers with additional categorical variables fixed to the identifier. 

The current version of this model identifies special cause variation by comparing each outcome ("Pass_percentage") for a unique identifiers (Staff_ID), stratified by categorical variable 1 (Staff_Type) and categorical variable 2 (Measure). Each outcome is compared to the sample (Institution) mean and standard deviation for the outcome across the stratifying variables (for example: mean and standard deviation of the Pass_percentage for measure x and staff role y at Institution z). **Only data with a normal distribution can undergo SPC methods using mean and standard deviation.** The program assess for normality of the distribution using the Shaprio Wilk test.

For each sample, stratified by categorical variables, the program assigns a mean, standard deviation, upper control limit (3(standard deviation)), lower control limit (-3(standard deviation)), and a boolean identifying normal distribution.

Each unique identifier is then matched with the appropriate institution data and the following statistical process control rules are performed.

**Current SPC rules tested**
|Rule #| Rule Description                                               |
|     1| A point falls above the UCL or below the LCL                   |
|     2| 2 of 3 consecutive points above or below 2 standard deviations |
|     3| 4 of 5 consecutive points above or below 1 standard deviation  |
|     4| 9 consecutive points fall on the same side of the centerline   |
|     5| Trend of 6 points in a row increasing or decreasing            |

### Inputs

The program takes an input csv file from the directory the program is runnning. The file should include columns for the following:
- Sample (Institution_ID)
- Unique Identifier (Staff_ID)
- Categorical Variable 1 (Staff_Type)
- Categorical Variable 2 (Measure)
- Outcome (Pass_percentage)

### Outputs

The program returns a csv labled "SPC_Results.csv" to the program directory. Results include the following:
- Unique Identifier (Staff_ID)
- Sample (Institution)
- Categorical Variable 1 (Role)
- Categorical Variable 2 (Measure)
- Time_Points <- *This is the number of measures assessed across the control chart for the individual*
- Distribution
- Unwarrented_Variation <- *True/False*
- Magnitude_of_Variation <- *Total amount of special cause variation*
- Magnitude_of_Positive_Variation <- *Total amount of special cause variation above the mean*
- Magnitude_of_Negative_Variation <- *Total amount of special cause variation below the mean*
- Rule_1_Positive <- *For each rule, assessed as above or below the mean*
- Rule_1_Negative
- Rule_2_Positive
- Rule_2_Negative
- Rule_3_Positive
- Rule_3_Negative
- Rule_4_Positive
- Rule_4_Negative
- Rule_5_Positive
- Rule_5_Negative

### How to Run

SPC.py runs without other file dependencies. Ensure that your input data file is in the same directory as SPC.py. Required libraries below. 

#### Required Libraries

- Pandas
- Numpy
- Scipy

