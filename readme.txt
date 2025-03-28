Creating a Hospital Stay Database for a Medical Billing Team

The goal of this project is to create a database of hospital stays for the billing team in a medical billing company to use to know how much to bill each patient and/or the insurance provider for each hospital stay. To assist with billing, the database includes such data as the patient's name and date of birth, his or her medical condition, the insurance provider, the billing total for the stay, and the hospital where he or she received treatment.

In this scenario, this project would be done by a data engineer within the fictional medical billing company. The company is a third party that acts as a go-between for payers (patients/insurance companies) and care providers (hospitals). After each hospital stay, the company translates diagnoses and treatments done during the stay into medical codes, determines the billing amount based on the code(s), provides the payer with the bill, collects the payment from the payer, and gives the payment to the care provider. The care provider pays the billing company for these services, and because of this outsourcing of medical coding and billing, the care provider's doctors and nurses can spend less time doing administrative tasks and more time caring for their patients.

The hospital stay data is mock data downloaded from Kaggle. The name and gender data is mock data created by me, and its purpose is to replace the patient names and genders in the Kaggle dataset with more realistic names and correct genders to model real-world data more accurately.

Hospital stay data source: https://www.kaggle.com/datasets/prasad22/healthcare-dataset?resource=download



How to Run This Program

First, make sure to download all files and folders included on GitHub (perhaps aside from README.md and LICENSE) and move everything into a folder of your choice. For example, you could create a folder within your Documents folder called "Database for the Billing Team" and move the 4 folders and the 3 other files you downloaded there. Then double-click on Database for the Billing Team with the red plus icon to run the program. The query prompt should appear shortly, and you can enter any valid SQLite statement. See the "SQL Statement Examples" section below for some examples of statements, and look for SQL and SQLite resources online if anything is unclear to you.

If you would like to change the Python code at all, the source code can be found in the "Python code" folder. Note that the database creation code create_db.py is run within the query running code run_queries.py. See the comments at the top of each code file for information on dealing with errors that may occur after editing the code. Also, I created the EXE file using PyInstaller, so you can learn how to use PyInstaller if you would like to create a new EXE based on your modified code. The PyInstaller specification code I used for creating the EXE is in the EXE files -> EXE specs folder.



Database Structure

The hospital stay database was designed using a dimensional model (star schema) created on the website ERDPlus and saved in the PNG file in the Data files folder. Structurally, the database consists of a hospital_stay fact table and 8 dimension tables: date, patient, doctor, hospital, insurance, admission_type, medication, and test_results.

The fact table is about hospital stays because hospital stays are the organizational events of interest. The billing team wants to know how much the patient involved in each hospital stay or his/her insurance company should be billed for the care provided during that stay. The quantitative variable billing_amt that describes the hospital stay itself (i.e., the stay is worth billing_amt because of the care provided during it) goes into the hospital stay fact table, as does the unique stay identifier stay_id. There are also foreign keys referencing the dimensions, so the dimension tables must be created and defined first in the code.

The people, organizations, and other entities involved in the hospital stay (e.g., the hospital itself, the patient, the doctor) are assigned to their own dimensions. The fact table must contain quantitative (numerical) rather than qualitative (text) data, so it will contain foreign keys referencing these dimensions' unique numeric IDs rather than containing the actual names of hospitals, patients, doctors, etc. Therefore, except for the date dimension, each dimension has a numeric auto-incrementing ID for each row in the dimension, with each row having a unique value or set of values across the other (i.e., non-ID) columns. For example, if a recent hospital stay is added to the database and the patient is already entered into the patient dimension (same combination of name, birth date, gender, blood type, and medical condition), the patient's data will not be re-entered into a new row in the patient dimension. Instead, the fact table should simply have a new row with the patient foreign key referencing the existing patient ID, which can be found by querying the ID column where the patient name, birth date, gender, blood type, and medical condition all match the given patient's data.

From what I have learned about data modeling, creating a date dimension seems to be best practice. The foreign key in the fact table for each date can just be the date in 'YYYY-MM-DD' text format, and that same text format date can be the ID for the date in the date dimension. This date dimension enables the user to query the year, the quarter, the month (number and name), the day, and the day of the week for each date.

Please note that all variables are mandatory (i.e., can never have a null value), partially to ensure that all data entered is complete and partially because no null values have appeared so far in the data. If a null value appears in a future data record for a reason (e.g., null insurance_provider_id because the patient has no insurance and plans to pay the medical billing company entirely out of pocket), such a case will be addressed individually. It might be that a "No insurance" entry can be added to the insurance dimension, for instance.


date Dimension Table Structure

Each row in this dimension table represents one distinct date. For each date, 8 variables are stored in the table:

date_id (type DATE, primary key) - a unique ID for each date, which is the date in 'YYYY-MM-DD' text format
date_year (type INT) - the year portion of the date
date_quarter (type INT) - the quarter in which the date occurs (1, 2, 3, or 4)
date_month (type INT) - the month portion of the date, expressed as a number from 1 to 12
date_day (type INT) - the day portion of the date
date_month_name (type CHARACTER(9)) - the name of the date month
date_quarter_in_year (type CHARACTER(7)) - the date's quarter and year, expressed as, e.g., 'Q1 2025'
date_day_of_week (type CHARACTER(9)) - the date's day of the week


patient Dimension Table Structure

Each row in this dimension table represents one distinct patient. For each patient, 6 variables are stored in the table:

patient_id (type INT, primary key) - a unique ID for each patient
patient_name (type TEXT) - the patient's first and last name
patient_birth_date (type DATE, foreign key) - the patient's date of birth, references the date of birth's date_id from the date table
patient_gender (type CHARACTER(6)) - the patient's gender (Male or Female)
patient_blood_type (type CHARACTER(3)) - the patient's blood type (AB+, AB-, O+, A-, etc.)
patient_medical_condition (type TEXT) - the patient's medical condition

Moreover, each combination of the last 5 variables in each row must be unique.


doctor Dimension Table Structure

Each row in this dimension table represents one distinct doctor. For each doctor, 2 variables are stored in the table:

doctor_id (type INT, primary key) - a unique ID for each doctor
doctor_name (type TEXT, unique) - the doctor's first and last name


hospital Dimension Table Structure

Each row in this dimension table represents one distinct combination of hospital name and room number. For each hospital room, 3 variables are stored in the table:

hospital_id (type INT, primary key) - a unique ID for each hospital room
hospital_name (type TEXT) - the name of the hospital
hospital_room (type INT) - the hospital room number

Moreover, each combination of hospital_name and hospital_room must be unique.


insurance Dimension Table Structure

Each row in this dimension table represents one distinct insurance provider. For each insurance provider, 2 variables are stored in the table:

insurance_provider_id (type INT, primary key) - a unique ID for each insurance provider
insurance_provider_name (type TEXT, unique) - the insurance provider's name


admission_type Dimension Table Structure

Each row in this dimension table represents one distinct admission type. For each admission type, 2 variables are stored in the table:

adm_type_id (type INT, primary key) - a unique ID for each admission type
adm_type (type TEXT, unique) - the admission type's name


medication Dimension Table Structure

Each row in this dimension table represents one distinct medication. For each medication, 2 variables are stored in the table:

medication_id (type INT, primary key) - a unique ID for each medication
medication_name (type TEXT, unique) - the medication's name


test_results Dimension Table Structure

Each row in this dimension table represents one distinct test results type. For each test results type, 2 variables are stored in the table:

test_results_id (type INT, primary key) - a unique ID for each test results type
test_results (type TEXT, unique) - the test results type's name


hospital_stay Fact Table Structure

Each row in the fact table represents one distinct hospital stay. For each stay, 11 variables are stored in the table:

stay_id (type INT, primary key) - a unique ID for each stay
patient_id (type INT, foreign key) - the unique ID of the patient involved in the stay
doctor_id (type INT, foreign key) - the unique ID of the doctor in charge of caring for this patient
hospital_id (type INT, foreign key) - the unique ID of the hospital where the stay took place
insurance_provider_id (type INT, foreign key) - the unique ID of the patient's insurance provider
adm_type_id (type INT, foreign key) - the unique ID of the admission type (urgent, emergency, or elective)
medication_id (type INT, foreign key) - the unique ID of the medication involved in the treatment given to the patient
test_results_id (type INT, foreign key) - the unique ID of the results of test(s) done during the stay (normal, abnormal, or inconclusive)
admission_date (type DATE, foreign key) - the date the patient was admitted to the hospital
discharge_date (type DATE, foreign key) - the date the patient was discharged from the hospital
billing_amt (type NUMERIC) - the amount the payer owes for the care the patient received during this stay, in U.S. dollars

Moreover, each combination of the last 10 variables in each row must be unique. This is to prevent unnecessary or accidental duplication of data.



SQL Statement Examples

Please type your statements using SQLite-compatible keywords and the proper SQL statement structure, as demonstrated in these examples.

SELECT * FROM hospital_stay; - view all data from the hospital_stay fact table
SELECT billing_amt FROM hospital_stay; - view all billing amounts from the data
SELECT * FROM hospital_stay hs, patient p WHERE hs.patient_id = p.patient_id; - view all data from both hospital_stay and patient
SELECT p.patient_name, hs.billing_amt FROM hospital_stay hs INNER JOIN patient p ON hs.patient_id = p.patient_id INNER JOIN insurance i ON hs.insurance_provider_id = i.insurance_provider_id WHERE i.insurance_provider_name = 'Blue Cross'; - view patient names and billing amounts for all patients who have Blue Cross insurance
INSERT INTO patient VALUES (100000, 'Hingle McCringleberry', '1991-04-03', 'Male', 'B+', 'Diabetes'); - add a new row with these values to the patient table
SELECT * FROM patient WHERE patient_id = 100000; - view the new row mentioned above
DELETE FROM patient WHERE patient_id = 100000; - delete the same row


Data Cleaning

The odd capitalization of the patient names in the healthcare dataset and the fact that some of the names were associated with the wrong gender made cleaning the data in the patient name column difficult and time-consuming. Given the self-assigned deadline for completing this project and the fact that the data used is just mock data, I found it more reasonable to replace the patient names with my own patient names that are capitalized properly and associated with the correct gender. These can be found in the name_dataset.csv file. For each row in the healthcare dataset, a first name and gender are randomly picked from name_dataset, and then a last name is picked at random separately to add variation. Then the first and last name replace the patient name in the healthcare dataset, and the respective gender is put in the gender column for that row.


The doctor's name column is easier to clean. The main inconsistencies from what I could tell were that some names started with the titles Dr., Mr., Mrs., Miss, or Ms., and some names ended with MD, DDS, PhD, or DVM, while others had no extra titles. I decided to keep the name suffixes Jr., Sr., II, III, IV, and V and remove the other titles mentioned above to create consistency. Simply replacing all instances of ",Dr. "/",Mr. "/",Mrs. "/etc. with "," and all instances of " MD,"/" DDS,"/" DVM,"/etc. with "," resulted in a column of clean data.


The original dataset includes each patient's age at the time of admission. If that patient goes to one of these hospitals again at a different age, though, the only solutions of which I know that would ensure all ages are kept (if there is a need for this) are
(1) to create a new row in the patient dimension that includes the older age. To a database user, this may imply (falsely) that this is a distinct person who happens to share a first and last name, gender, blood type, and possibly medical condition with the existing patient. Even if not, this goes against the idea of each distinct patient having his/her own row in the dimension.
(2) to add a new column for the age each patient was at the time of admission for his/her second hospital stay. This would result in a column that would contain many null values if many patients had only had one stay at any of these hospitals since the data began to be recorded. Subsequent hospital stays for a single patient would require even more columns to be added if a record of each age needed to be kept.
This is all because patient age is a slowly changing dimension.

In addition, for the sake of data accuracy, it can be difficult to keep track of someone's exact age over time without knowing the date of birth. Someone who was previously admitted to a hospital on September 1, 2022, at age 30 and was admitted again today (as of this writing) on March 28, 2025, could be either 32 or 33 now. For accuracy over time, for clarity, and for efficiency in data storage, date of birth is the variable to use instead of age. A person's age is always easy to calculate given his/her date of birth and the current date.

In real life, the medical billing company would need to obtain each patient's actual date of birth. Here, however, we will give each of our fictional patients a random date of birth given his/her age and date of admission. Leap years make the randomization more difficult, admittedly. Generally, though, the birth date generation algorithm takes the admission date, goes back exactly <Age> years prior, assigns that date as the latest possible birth date, and generates a random date between that latest possible date and the date 364 days before it.

Example: Jacob Blues, age 75, date of admission 10/09/2024
The algorithm would go back 75 years before 10/09/2024 and set the latest possible birth date as 10/09/1949. Then it would randomly generate a birth date between 10/10/1948 and 10/09/1949, with either of those two endpoint dates as a possible choice (inclusive).

All dates of birth are put into the Date of Birth column in the stay_data DataFrame, and once all other data cleaning and alteration has been done, the Age column is dropped from stay_data.


The final column that needed alteration was the hospital column. The hospital names given were not all realistic, so in the code I created a list of more realistic hospital names and replaced the hospital names in the healthcare dataset with the more realistic ones.


The Python code does all data cleaning and alteration other than the cleaning of the doctor names. It also saves the fully cleaned data as the hosp_stay_dataset_fully_cleaned CSV, enabling anyone who needs the database data in CSV form (e.g., to create Tableau visualizations) to have access to it in that format.