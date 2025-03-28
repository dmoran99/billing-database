# -*- coding: utf-8 -*-

# Please see Readme for more info

# N.B.: Only run this code (including allowing it to run via the subprocess in the run_queries file) if you want to rebuild
# the database! The whole process can take multiple minutes, vs. the instant querying that running the EXE allows by default.
# I used PyInstaller to create the EXE, so please look into PyInstaller more if you would like to modify any of the code in
# these files and create your own EXE.

# I have already run this code via the subprocess in the run_queries file to create the database and load data into it. The
# data is cleaned partially by hand and partially by this code, saved to a CSV for use by anyone who needs it, and loaded into
# a SQLite database.

# If you would like to delete the database and rebuild it, you can run this code so that the tables are deleted and then
# created and loaded with data again. Alternatively, you can delete the database file itself and then run the code.

# If you run this code (or any code that connects to the database) but have an error pop up, first make sure both the cursor
# and the connection are closed. You can do this by running cursor.close() and then connection.close() in the kernel in your
# Python environment. Run both commands even if you get an error saying "Cannot operate on a closed database."

# If you get a "database is locked" error message, restart the kernel and, once it's done, delete the database file. Then run
# this code to rebuild the database.



# Part 1: Import and clean the data

# Import packages - sqlite3 for running the database, pandas for importing and manipulating the data, datetime for working
# with dates and their components (days/months/years), warnings for displaying a warning, and random for randomized data
# replacement (make patient names and hospital names more realistic, and replace ages with dates of birth)
import sqlite3
import pandas as pd
import datetime as dt
import warnings
from random import randint, seed

# Import partially cleaned hospital stay data from CSV
stay_data = pd.read_csv('Data files/hosp_stay_dataset_dr_names_cleaned.csv')

# Insert Date of Birth column
stay_data.insert(loc=2, column='Date of Birth', value=['']*stay_data.shape[0])

# Insert index column
stay_data.insert(loc=0, column='Index', value=range(1, stay_data.shape[0]+1))

# Import first name, last name, and gender columns from name dataset
name_gender_data = pd.read_csv('Data files/name_dataset.csv')

# Create list of hospitals to choose from
hospital_list = ['Northwestern Hospital', 'Central DuPage Hospital', 'LaGrange Hospital', 'Elmhurst Hospital',
                 'Swedish Hospital', 'Good Samaritan Hospital', 'Saint Joseph Hospital', 'Resurrection Hospital',
                 'Hinsdale Hospital', 'Edward Hospital', 'Alexian Bros. Hospital', 'Mercy Hospital', 'Palos Hospital']

# Function to change each age to date of birth
def change_age_to_db(age, admission_date):
    adm_date_year = dt.datetime.strptime(admission_date, '%Y-%m-%d').strftime('%Y')
    
    # If admission date is not on Feb 29th, latest possible birth date is the same day as admission date <Age> years prior
    if not(dt.datetime.strptime(admission_date, '%Y-%m-%d').strftime('%m') == '02' and dt.datetime.strptime(
           admission_date, '%Y-%m-%d').strftime('%d') == '29'):
        latest_possible_birth_date = str(int(adm_date_year)-age)+admission_date[admission_date.find('-'):]
    
    # If admission date is a Leap Day in a leap year, check whether <Age> years prior was also a leap year
    elif int(adm_date_year) % 400 == 0 or (int(adm_date_year) % 4 == 0 and int(adm_date_year) % 100 != 0):
        
        # If so, latest possible birth date is Leap Day <Age> years prior
        if int(adm_date_year)-age % 400 == 0 or (int(adm_date_year)-age % 4 == 0 and int(adm_date_year)-age % 100 != 0):
            latest_possible_birth_date = str(int(adm_date_year)-age)+'-02-29'
        
        # If <Age> years prior was not a leap year, latest possible birth date is Feb 28th
        else:
            latest_possible_birth_date = str(int(adm_date_year)-age)+'-02-28'
    
    # If admission date is Feb 29th but not in a leap year, warn the user
    else:
        warnings.warn('One of your admission dates is February 29th in a non-leap year! Please ensure the data is accurate.')
        latest_possible_birth_date = str(int(adm_date_year)-age)+'-02-28'
    
    # Pick any random day between latest possible birth date and 364 days before that
    # Note: earliest possible birth date will be 1 day later than it really should be if a Leap Day falls within this range
    birth_date = (dt.datetime.strptime(latest_possible_birth_date, '%Y-%m-%d') - dt.timedelta(days=randint(0, 364)))\
                 .strftime('%Y-%m-%d')
    return birth_date

# Replace original patient names and genders and hospital names with more realistic ones, and change each age to date of birth
seed(100) # For reproducibility; feel free to change to a different seed
for df_row in range(0, stay_data.shape[0]):
    # Use the selected first name's gender by pulling it from the same row as the first name
    first_name_gender_row = randint(name_gender_data.index.start, name_gender_data.index.stop-1)
    first_name = name_gender_data.loc[first_name_gender_row, 'First Name']
    gender = name_gender_data.loc[first_name_gender_row, 'Gender']
    # Choose any last name
    last_name = name_gender_data.loc[randint(name_gender_data.index.start, name_gender_data.index.stop-1), 'Last Name']
    # Join first name, space, and last name
    stay_data.loc[df_row, 'Name'] = first_name+' '+last_name
    # Convert age (assumed to be at time of admission) to date of birth
    stay_data.loc[df_row, 'Date of Birth'] = change_age_to_db(stay_data.loc[df_row, 'Age'],
                                                              stay_data.loc[df_row, 'Date of Admission'])
    # Change gender to the correct gender (if applicable)
    stay_data.loc[df_row, 'Gender'] = gender
    # Pick a random name from the hospital list
    stay_data.loc[df_row, 'Hospital'] = hospital_list[randint(0, len(hospital_list)-1)]

# Remove Age column
stay_data = stay_data.drop('Age', axis=1)    

# Now that the data has been fully cleaned, save it to a CSV so other data analysts can use it for various purposes
stay_data.iloc[:, 1:].to_csv('Data files/hosp_stay_dataset_fully_cleaned.csv', index=False)




# Part 2: Create the database and load it with data

# Create connection to the database hospital_stay_database, or create the database if it does not already exist
connection = sqlite3.connect('hospital_stay_database.db') 
# Also create a cursor from this connection to collect query results (for finding foreign key IDs when adding the data)
cursor = connection.cursor()


# Drop tables if they already exist so we can run the CREATE TABLE command
for table in ['date', 'patient', 'doctor', 'hospital', 'insurance', 'admission_type', 'medication', 'test_results',
              'hospital_stay']:
    try:
        connection.execute('DROP TABLE '+table+';')
        connection.commit()
    except sqlite3.OperationalError:
        pass


# Create date dimension table and define its column structure
# Dimension table stores data related to people, objects, or entities involved in the fact table below
connection.execute('CREATE TABLE date (date_id DATE PRIMARY KEY, '+
                   'date_year INT NOT NULL, '+
                   'date_quarter INT NOT NULL, '+
                   'date_month INT NOT NULL, '+
                   'date_day INT NOT NULL, '+
                   'date_month_name CHARACTER(9) NOT NULL, '+
                   'date_quarter_in_year CHARACTER(7) NOT NULL, '+
                   'date_day_of_week CHARACTER(9) NOT NULL);')
connection.commit()

# Load each unique patient date of birth, admission date, and discharge date into the table
# The set function gets the unique values of these columns and allows them to all be merged into one large list
date_list = list(set(stay_data['Date of Birth']) | set(stay_data['Date of Admission']) | set(stay_data['Discharge Date']))
for date in date_list:
    date_year = int(dt.datetime.strptime(date, '%Y-%m-%d').strftime('%Y'))
    date_month = int(dt.datetime.strptime(date, '%Y-%m-%d').strftime('%m'))
    date_day = int(dt.datetime.strptime(date, '%Y-%m-%d').strftime('%d'))
    date_quarter = pd.Timestamp(date_year, date_month, date_day).quarter
    connection.execute('INSERT INTO date VALUES ("'+date+'", '+ # date_id
                       str(date_year)+', '+ # date_year
                       str(date_quarter)+', '+ # date_quarter
                       str(date_month)+', '+ # date_month
                       str(date_day)+', '+ # date_day
                       '"'+dt.datetime.strptime(date, '%Y-%m-%d').strftime('%B')+'", '+ # date_month_name
                       '"Q'+str(date_quarter)+' '+str(date_year)+'", '+ # date_quarter_in_year
                       '"'+dt.datetime.strptime(date, '%Y-%m-%d').strftime('%A')+'");') # date_day_of_week
connection.commit()


# Create patient dimension table and define its column structure
connection.execute('CREATE TABLE patient (patient_id INT PRIMARY KEY,'+
                   'patient_name TEXT NOT NULL, '+
                   'patient_birth_date DATE NOT NULL, '+
                   'patient_gender CHARACTER(6) NOT NULL, '+
                   'patient_blood_type CHARACTER(3) NOT NULL, '+
                   'patient_medical_condition TEXT NOT NULL, '+
                   'FOREIGN KEY (patient_birth_date) REFERENCES date(date_id), '+
                   'UNIQUE(patient_name, patient_birth_date, patient_gender, '+
                   'patient_blood_type, patient_medical_condition));')
connection.commit()

# Load each unique patient's data into the table
id_num = 1
for df_row in range(0, stay_data.shape[0]):
    connection.execute('INSERT INTO patient VALUES ('+str(id_num)+', '+ # patient_id
                       '"'+stay_data.loc[df_row, 'Name']+'", '+ # patient_name
                       '"'+stay_data.loc[df_row, 'Date of Birth']+'", '+ # patient_birth_date
                       '"'+stay_data.loc[df_row, 'Gender']+'", '+ # patient_gender
                       '"'+stay_data.loc[df_row, 'Blood Type']+'", '+ # patient_blood_type
                       '"'+stay_data.loc[df_row, 'Medical Condition']+'");') # patient_medical_condition
    id_num += 1
connection.commit()


# Create doctor dimension table and define its column structure
connection.execute('CREATE TABLE doctor (doctor_id INT PRIMARY KEY, doctor_name TEXT NOT NULL UNIQUE);')
connection.commit()

# Load each unique doctor's data into the table
id_num = 1
doctor_list = list(set(stay_data['Doctor']))
for doctor_name in doctor_list:
    connection.execute('INSERT INTO doctor VALUES ('+str(id_num)+', "'+doctor_name+'");')
    id_num += 1
connection.commit()


# Create hospital dimension table and define its column structure
connection.execute('CREATE TABLE hospital (hospital_id INT PRIMARY KEY, hospital_name TEXT NOT NULL, '+
                   'hospital_room INT NOT NULL, UNIQUE(hospital_name, hospital_room));')
connection.commit()

# Load each unique hospital name and room number combination into the table
id_num = 1
for row in stay_data.groupby(['Hospital', 'Room Number']):
    connection.execute('INSERT INTO hospital VALUES ('+str(id_num)+', "'+row[0][0]+'", '+str(row[0][1])+');')
    id_num += 1


# Create insurance dimension table and define its column structure
connection.execute('CREATE TABLE insurance (insurance_provider_id INT PRIMARY KEY, insurance_provider_name TEXT NOT NULL '+
                   'UNIQUE);')
connection.commit()

# Load each unique insurance provider's name into the table
id_num = 1
provider_list = list(set(stay_data['Insurance Provider']))
for provider_name in provider_list:
    connection.execute('INSERT INTO insurance VALUES ('+str(id_num)+', "'+provider_name+'");')
    id_num += 1
connection.commit()


# Create admission_type dimension table and define its column structure
connection.execute('CREATE TABLE admission_type (adm_type_id INT PRIMARY KEY, adm_type TEXT NOT NULL UNIQUE);')
connection.commit()

# Load each unique admission type into the table
id_num = 1
adm_type_list = list(set(stay_data['Admission Type']))
for adm_type in adm_type_list:
    connection.execute('INSERT INTO admission_type VALUES ('+str(id_num)+', "'+adm_type+'");')
    id_num += 1
connection.commit()


# Create medication dimension table and define its column structure
connection.execute('CREATE TABLE medication (medication_id INT PRIMARY KEY, medication_name TEXT NOT NULL UNIQUE);')
connection.commit()

# Load each unique medication into the table
id_num = 1
med_list = list(set(stay_data['Medication']))
for med in med_list:
    connection.execute('INSERT INTO medication VALUES ('+str(id_num)+', "'+med+'");')
    id_num += 1
connection.commit()


# Create test_results dimension table and define its column structure
connection.execute('CREATE TABLE test_results (test_results_id INT PRIMARY KEY, test_results TEXT NOT NULL UNIQUE);')
connection.commit()

# Load each unique test result into the table
id_num = 1
result_list = list(set(stay_data['Test Results']))
for result in result_list:
    connection.execute('INSERT INTO test_results VALUES ('+str(id_num)+', "'+result+'");')
    id_num += 1
connection.commit()


# Create hospital stay fact table
# Fact table stores quantitative data about a business/organizational event
connection.execute('CREATE TABLE hospital_stay (stay_id INT PRIMARY KEY, '+
                   'patient_id INT NOT NULL, '+
                   'doctor_id INT NOT NULL, '+
                   'hospital_id INT NOT NULL, '+
                   'insurance_provider_id INT NOT NULL, '+
                   'adm_type_id INT NOT NULL, '+
                   'medication_id INT NOT NULL, '+
                   'test_results_id INT NOT NULL, '+
                   'admission_date DATE NOT NULL, '+
                   'discharge_date DATE NOT NULL, '+
                   'billing_amt NUMERIC NOT NULL, '+
                   'FOREIGN KEY (patient_id) REFERENCES patient(patient_id), '+
                   'FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id), '+
                   'FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id), '+
                   'FOREIGN KEY (insurance_provider_id) REFERENCES insurance(insurance_provider_id), '+
                   'FOREIGN KEY (adm_type_id) REFERENCES admission_type(adm_type_id), '+
                   'FOREIGN KEY (medication_id) REFERENCES medication(medication_id), '+
                   'FOREIGN KEY (test_results_id) REFERENCES test_results(test_results_id), '+
                   'FOREIGN KEY (admission_date) REFERENCES date(date_id), '+
                   'FOREIGN KEY (discharge_date) REFERENCES date(date_id), '+
                   'UNIQUE(patient_id, doctor_id, hospital_id, insurance_provider_id, adm_type_id, medication_id, '+
                   'test_results_id, admission_date, discharge_date, billing_amt));')
connection.commit()


# Load the hospital stay data into the database row by row
for df_row in range(0, stay_data.shape[0]):
    
    # Find the patient id matching with the patient from this row
    cursor.execute('SELECT patient_id FROM patient WHERE patient_name = "'+stay_data.loc[df_row, 'Name']+'" AND '+
                   'patient_birth_date = "'+stay_data.loc[df_row, 'Date of Birth']+'" AND '+
                   'patient_gender = "'+stay_data.loc[df_row, 'Gender']+'" AND '+
                   'patient_blood_type = "'+stay_data.loc[df_row, 'Blood Type']+'" AND '+
                   'patient_medical_condition = "'+stay_data.loc[df_row, 'Medical Condition']+'";')
    patient_id = cursor.fetchall()
    
    # Find the doctor id matching with the doctor from this row
    cursor.execute('SELECT doctor_id FROM doctor WHERE doctor_name = "'+stay_data.loc[df_row, 'Doctor']+'";')
    doctor_id = cursor.fetchall()
    
    # Find the hospital id matching with the hospital from this row
    cursor.execute('SELECT hospital_id FROM hospital WHERE hospital_name = "'+stay_data.loc[df_row, 'Hospital']+'" AND '+
                   'hospital_room = '+str(stay_data.loc[df_row, 'Room Number'])+';')
    hospital_id = cursor.fetchall()
    
    # Find the insurance provider id matching with the insurance provider from this row
    cursor.execute('SELECT insurance_provider_id FROM insurance WHERE insurance_provider_name = "'+
                   stay_data.loc[df_row, 'Insurance Provider']+'";')
    insurance_provider_id = cursor.fetchall()
    
    # Find the admission type id matching with the admission type from this row
    cursor.execute('SELECT adm_type_id FROM admission_type WHERE adm_type = "'+stay_data.loc[df_row, 'Admission Type']+'";')
    adm_type_id = cursor.fetchall()
    
    # Find the medication id matching with the medication from this row
    cursor.execute('SELECT medication_id FROM medication WHERE medication_name = "'+stay_data.loc[df_row, 'Medication']+'";')
    medication_id = cursor.fetchall()
    
    # Find the test results id matching with the test results from this row
    cursor.execute('SELECT test_results_id FROM test_results WHERE test_results = "'+stay_data.loc[df_row, 'Test Results']+
                   '";')
    test_results_id = cursor.fetchall()
    
    # Insert all the values from the current DataFrame row into the hospital_stay fact table
    connection.execute('INSERT INTO hospital_stay VALUES ('+
                       str(stay_data.loc[df_row, 'Index'])+', '+ # stay_id
                       str(patient_id[0][0])+', '+
                       str(doctor_id[0][0])+', '+
                       str(hospital_id[0][0])+', '+
                       str(insurance_provider_id[0][0])+', '+
                       str(adm_type_id[0][0])+', '+
                       str(medication_id[0][0])+', '+
                       str(test_results_id[0][0])+', '+
                       '"'+stay_data.loc[df_row, 'Date of Admission']+'", '+
                       '"'+stay_data.loc[df_row, 'Discharge Date']+'", '+
                       str(round(stay_data.loc[df_row, 'Billing Amount'], 2))+');')

connection.commit()



# Part 3: End any remaining active processes

# Close the cursor and the connection
cursor.close()
connection.close()