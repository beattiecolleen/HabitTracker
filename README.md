# HabitTracker

## Description
The HabitTracker is a python application that allows users to create, manage, complete, and delete habits with a periodicity of either daily, weekly, or monthly. They have all kinds of options for viewing streaks and statistics (e.g. the longest streak, the most challenging habit, streaks by periodicity).
The application comes with a testing suite, a predefined user, and 5 predefined habits of all three periodicites with a completion history each dating back 4 - 10 weeks.
Python HabitTracker inlcudes MySQL, Pytest, Bcyrpt, and argparse.

## Features
- User Authentication (sign up, and log in)
- Adding, deleting, and viewing of habits for a specific user
- Track habit completion history
- Filter habits by periodicity and view statistics

## Requirements
Python 3.11.2
MySQL

## Setup and Installation
Follow these steps to set up and run the application:
### Step 1: Clone the Repository
Clone the repository to your local machine
git clone https://github.com/beattiecolleen/HabitTracker

### Step 2: Install the Dependencies
Navigate to the project directory and run the following command, ensuring all depenendcies in the requirements.txt are installed.
pip install -r requirements.txt

### Step 3: Set up the MySQL Database
1. Make sure MySQL is installed on your machine.
2. Create the databases (habittrackerdb for the app, testdatabase for the pytest test suite):
2.1. Open MySQL Workbench and log in. Create a new database names habittrackerdb using:
CREATE DATABASE habittrackerdb;
2.2. Create a new database testdatabase using:
CREATE DATABASE testdatabase;
3. Update the database configuration:
In the database.py file, update the database connection at the top to match your local MySQL setup (user, password, host).
Run the database setup script:
4. Run the database.py script to install the necessary tables using:
python database.py

## Step 4: Run the Application
The setup is now complete and the application can be run.
The main file that is to be run is cli.py. Do this using:
python cli.py
This will bring you to the interactive interface.
Instead of this, argparse can be used to interact with the application in a more effective manner. Generally, this is done using:
python cli.py <action>

## Usage
The very first step includes creating an account.
This can be done using:
python cli.py --create_account --username <your_username> --password <your_password>
From then on, you must login first before being able to use the application:
python cli.py --login --username <your_username> --password <your_password> <action>
Once you are logged in you can perform actions like adding habits or tracking the completion.

## Actions
These are the actions that can be performed via the terminal
--help or --h for seeing the possible actions and receiving help
--create_account for creatign a new account
--login for logging into an existing account
--create_habit for creating a new habit
--delete_habit for deleting an existing habit via its ID
--complete_habit for marking a habit as complete
--view_streak for viewing the current streak for a specific habit
--view_longest_streak for viewing the longest streak for a specific habit
--view_all_streaks for viewing the longest streak across all habits
--display_habits for displaying all habits
--challenging_habit for displaying the most challenging habit
--group_habits for grouping the habits based on their periodicity
--analytics for displaying the analytics, which show the average time between completions of a habit, the habit with the most consistent completions, and the total and average streak across all habits
--username for setting up a username or logging into an existing account
--password for setting up a password or logging into an existing account

## Technologies Used
Python 3.11.2
MySQL
bcrypt (for password hashing)
pytest (for the test suite)

## Troubleshooting
### Unable to connect to the database
Ensure MySQL is installed and running on your machine.
Ensure the database was created.
Ensure the database name in the database.py file and the database name in your MySQL workbench match.
Ensure you are properly connected to MySQL (user, host, and password must be correct). The credentials should be double checked.
