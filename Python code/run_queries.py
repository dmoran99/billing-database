# -*- coding: utf-8 -*-

# Please see Readme for more info

# This code causes the database to be built if it has not been already and then creates and displays a user interface window
# in which the user can type a query. If the query is written correctly, the data will be displayed in a new interface window.
# Then the user can choose to run as many additional queries as they would like or to quit.

# If you run this code (or any code that connects to the database) but have an error pop up, make sure both the cursor and the
# connection are closed before you run any code again. You can do this by running cursor.close() and then connection.close()
# in the kernel in your Python environment. Run both commands even if you get an error saying "Cannot operate on a closed
# database."

# If you get a "database is locked" error message, restart the kernel and, once it's done, delete the database file. Then run
# this code with the subprocess lines (24 and 32) uncommented to rebuild the database.

# I used PyInstaller to create the EXE, so please look into PyInstaller more if you would like to modify any of the code in
# these files and create your own EXE.

# N.B.: Only uncomment the subprocess lines if you would like to rebuild the database! Keep the code as is if you simply wish
# to query the already built and loaded database.

# Import packages - subprocess for running the database creation code (if applicable), sqlite3 for running the database, and
# tkinter for creating and running the user interface
#import subprocess
import sqlite3
import tkinter as tk



# Part 1: Run the create_db code through a subprocess (if database not built yet)

#subprocess.run(['python', 'create_db.py'])


# Part 2: Enable user to run queries on the database

# Create connection to the database hospital_stay_database
connection = sqlite3.connect('hospital_stay_database.db') 
# Also create a cursor from this connection to collect user query results
cursor = connection.cursor()

# Define variable to indicate whether a Quit button has been clicked
quit_button_clicked = False
# Define function to set this variable to true; each Quit button will execute this function when clicked
def set_quit_var_to_true():
    global quit_button_clicked
    quit_button_clicked = True

# Keep running interface windows until a Quit button is clicked
while quit_button_clicked == False:
    # Create the window where the user will enter the query
    enter_query_window = tk.Tk()
    enter_query_window.wm_iconbitmap('Icon/database_exe_icon.ico')
    enter_query_window.title('Enter a query')
    enter_query_window.geometry('500x250+500+250')
    window_text = tk.Label(enter_query_window, text='Please enter a SQL query below.\nTo exit the program, click Quit at any'+
                           ' time.', font=('Arial', 15))
    window_text.place(x=60, y=30)
    # Text box for query entry
    query_entry_box = tk.Text(enter_query_window, width=55, height=6)
    query_entry_box.place(x=18, y=85)
    
    # Define a variable and a function to get the query that has been entered in the text box; activated by clicking OK button
    def get_query():
        global query_str
        query_str = query_entry_box.get('1.0', 'end-1c')
    ok_button = tk.Button(enter_query_window, text='OK', width=15, command=lambda: [get_query(),
                                                                                    enter_query_window.destroy()])
    ok_button.place(x=70, y=200)
    quit_button = tk.Button(enter_query_window, text='Quit', width=15, command=lambda: [set_quit_var_to_true(),
                                                                                 enter_query_window.destroy()])
    quit_button.place(x=290, y=200)
    enter_query_window.mainloop()
    
    # If Quit has been clicked, end all interface window processes
    if quit_button_clicked == True:
        break
    
    # Try to execute the query given by the user; if the query is invalid, an error window will pop up
    try:
        if query_str == '': # If no query given, prompt the user again
            continue
        cursor.execute(query_str)
    except:
        # Create error window
        invalid_query_window = tk.Tk()
        invalid_query_window.wm_iconbitmap('Icon/database_exe_icon.ico')
        invalid_query_window.title('Invalid query')
        invalid_query_window.geometry('500x200+500+250')
        window_text = tk.Label(invalid_query_window, text="Unfortunately, the query you entered was invalid.\nPlease "+
                               "enter a valid one instead.\n(See readme for query examples)", font=('Arial', 15))
        window_text.place(x=30, y=20)
        ok_button = tk.Button(invalid_query_window, text='OK', width=15, command=invalid_query_window.destroy)
        ok_button.place(x=70, y=160)
        quit_button = tk.Button(invalid_query_window, text='Quit', width=15, command=lambda: [set_quit_var_to_true(),
                                                                                     invalid_query_window.destroy()])
        quit_button.place(x=290, y=160)
        invalid_query_window.mainloop()
        
        if quit_button_clicked == True:
            break
        
        continue # Skip trying to display the query result if the query was invalid
    
    # Store query result rows in text form in query_result_text
    data = cursor.fetchall()
    query_result_text = ''
    for record in data:
        query_result_text += str(record) + '\n'
    
    # Create the query result display window
    result_display_window = tk.Tk()
    result_display_window.wm_iconbitmap('Icon/database_exe_icon.ico')
    result_display_window.title('Query result')
    result_display_window.geometry('700x500+400+200')
    result_display_box = tk.Text(result_display_window, state='normal', width=86, height=27)
    result_display_box.insert('1.0', query_result_text)
    result_display_box.config(state='disabled') # Make the textbox for displaying the result read-only
    result_display_box.grid(row=0, column=0)
    connection.commit()
    ok_button = tk.Button(result_display_window, text='OK', width=15, command=result_display_window.destroy)
    ok_button.place(x=170, y=450)
    quit_button = tk.Button(result_display_window, text='Quit', width=15, command=lambda: [set_quit_var_to_true(),
                                                                                 result_display_window.destroy()])
    quit_button.place(x=390, y=450)
    result_display_window.mainloop()
    
    if quit_button_clicked == True:
        break



# Part 3: End any remaining active processes

# Close the cursor and the connection
cursor.close()
connection.close()