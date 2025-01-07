#Connection to MySQL
import mysql.connector
#Used for password hashing
import bcrypt

#Creation of a new database
db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "testingpassword",
    database = "habittrackerdb"
    #database = "testdatabase" #Uncomment this for pytest tests, use "habittrackerdb" for real use
)

mycursor = db.cursor()


#Creation of User table
mycursor.execute(""" CREATE TABLE IF NOT EXISTS Users(
                 username VARCHAR(50) NOT NULL,
                 password VARCHAR(500) NOT NULL,
                 userID INT(15) AUTO_INCREMENT PRIMARY KEY,
                 UNIQUE (username)
                 )
                 """)
db.commit()

#Creation of Habit table
mycursor.execute(""" CREATE TABLE IF NOT EXISTS Habits(
                 habitID INT(15) AUTO_INCREMENT PRIMARY KEY,
                 habitname VARCHAR(100) NOT NULL,
                 periodicity ENUM('daily', 'weekly', 'monthly') NOT NULL,
                 created_at DATETIME NOT NULL,
                 userrefID  INT(15),
                 FOREIGN KEY(userrefID) REFERENCES Users(userID) ON DELETE CASCADE
                 )
                 """)
db.commit()

#Creation of CompletionHistory table
mycursor.execute(""" CREATE TABLE IF NOT EXISTS CompletionHistory(
                 completionhistoryID INT(15) AUTO_INCREMENT PRIMARY KEY,
                 habitrefID INT(15),
                 completedate DATETIME NOT NULL,
                 FOREIGN KEY(habitrefID) REFERENCES Habits(habitID) ON DELETE CASCADE
                 )
                 """)
db.commit()

#New user account creation
def insert_new_user(username_input, hashed_password):
    #INSERT query to store the hashed password and username in the users table
    mycursor.execute("""INSERT INTO Users(username, password)
                    VALUES (%s, %s)
                    """, (username_input, hashed_password))
    db.commit()


#Allow users to log in
def get_user_by_username(entry_username):
    #App retrieves stored password
    mycursor.execute(""" SELECT userID, password FROM users WHERE username = %s
                     """, (entry_username,))
    result = mycursor.fetchone() #Fetch one row from the result of the query
    return result #Return result so that cli.py can use it

#Allow logged in users to create a new habit
def insert_new_habit(habit_name, periodicity, user_id):
    mycursor.execute("""
                    INSERT INTO habits(habitname, periodicity, created_at, userrefID)
                     VALUES(%s, %s, NOW(), %s)
                     """, (habit_name, periodicity, user_id))
    db.commit()

#Allow logged in users to delete a habit
def delete_habit(habit_id, user_id):
    #Make sure the habit belongs to the logged in user
    mycursor.execute("""
                    DELETE FROM habits
                    WHERE habitID = %s AND userrefID = %s
                     """, (habit_id, user_id))
    db.commit()

    if mycursor.rowcount > 0:
        return True
    return False

#Display habits for deleting
def display_habits_for_deletion(user_id):
    mycursor.execute("""
                    SELECT habitID, habitname, periodicity FROM habits
                    WHERE userrefID = %s
                     """, (user_id,))
    return mycursor.fetchall() #Return the list of habits for the user

#Allow users to complete a habit
def insert_habit_completion(habit_id):
    #Insert a completion record for a habit in the completionhistory table
    mycursor.execute("""
                    INSERT INTO CompletionHistory(habitrefID, completedate)
                     VALUES (%s, NOW())
                     """, (habit_id,))
    db.commit()

def get_habits_by_user(user_id):
    #Gets all habits for the logged in user
    mycursor.execute("""
                    SELECT habitID, habitname, periodicity FROM Habits
                    WHERE userrefID = %s
                     """, (user_id,))
    return mycursor.fetchall()

#Completion history for streak calculation
def get_completion_history_for_habit(habit_id):
    #Gets all completion records for a specific habit
    mycursor.execute("""
                    SELECT completedate FROM CompletionHistory
                    WHERE habitrefID = %s 
                    ORDER BY completedate DESC
                     """, (habit_id,))
    return mycursor.fetchall() #Returns a list of completion dates for a specific habit

#Allow users to get habits by periodicity
def get_habits_by_periodicity(user_id, periodicity):
    mycursor.execute("""
                    SELECT habitID, habitname, periodicity, created_at FROM Habits
                    WHERE userrefID = %s AND periodicity = %s
                     """, (user_id, periodicity))
    return mycursor.fetchall() #Returns a list of all habits that meet the criteria