"""
TEST SUITE FOR A DUPLICATED DATABASE (EXACT COPY OF THE REAL DATABASE)
"""
import pytest
import sys
import mysql.connector
from database import (insert_new_user, get_user_by_username, insert_new_habit, delete_habit,
                      display_habits_for_deletion, insert_habit_completion, get_habits_by_user,
                      get_completion_history_for_habit, get_habits_by_periodicity)
from cli import (delete_habit_prompt, create_habit, complete_habit_prompt, view_habit_streak,
                 view_longest_streak, view_longest_streak_across_all_habits, display_user_habits,
                 display_most_challenging_habit, group_habits_by_periodicity, view_analytics, main)
from habit import Habit
from analytics import (average_completion_time, most_consistent_habit, aggregate_streak_analysis)

#Setting up a test database connection
@pytest.fixture
def db_connection():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "testingpassword",
        database = "testdatabase"
    )
    cursor = db.cursor()
    yield db, cursor
    db.close()

#Clean up the database after the tests (automated)
@pytest.fixture(autouse=True)
def clean_up_database(db_connection):
    db, cursor = db_connection
    cursor.execute("DELETE FROM CompletionHistory")
    cursor.execute("DELETE FROM Habits")
    cursor.execute("DELETE FROM Users")
    #tables = ["CompletionHistory", "Habits", "Users"]
    #for table in tables:
        #cursor.execute(f"DELETE FROM {table}")
    db.commit()

#THIS IS NEW
#Helping fixture for the creation of a new user (makes it easier to create a user before each test)
@pytest.fixture
def create_test_user(db_connection):
    db, cursor = db_connection
    username = "testuser"
    password = "password"
    insert_new_user(username, password)
    user = get_user_by_username(username)
    #Get the user's ID
    yield user[0]
    cursor.execute("DELETE FROM users WHERE userid = %s", (user[0],)) #changed from id to userid
    db.commit()


#Test the create user function
def test_insert_new_user(db_connection):
    db, cursor = db_connection

    #Only test that creates a user manually
    username = "testuser5"
    password = "testpassword"

    #Run database function to insert the new user
    insert_new_user(username, password)
    
    #Select user from database to make sure it was created
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    result = cursor.fetchall()

    #Make sure the result exists
    assert result is not None
    
#Test create new habit function
def test_insert_new_habit(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of the habit
    habit_name  = "Exercise"
    periodicity = "daily"

    #Run insert_new_habit to create the habit
    insert_new_habit(habit_name, periodicity, user_id)

    #Query for the created habit
    cursor.execute("SELECT habitname, periodicity FROM Habits WHERE userrefID = %s", (user_id,))
    result = cursor.fetchone()

    #Make sure there is a result
    assert result is not None

#Test get user by username function (necessary for all streak calculations)
def test_get_user_by_username(db_connection, create_test_user):
    db, cursor = db_connection

    #Manually select the create_test_user name for simplicity
    username = "testuser"

    #Function queries db for username and returns it as a tuple
    result = get_user_by_username(username)

    assert result is not None

#Test delete habit function
def test_habit_deletion(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of a new habit for testing the deletion
    habit_name = "Exercise"
    periodicity = "daily"
    habit_id = insert_new_habit(habit_name, periodicity, user_id)

    result = delete_habit(habit_id, user_id)

    #Proves habit was deleted
    cursor.execute("SELECT * FROM Habits WHERE habitID = %s", (habit_id,))
    habit_after_delete = cursor.fetchone()
    assert habit_after_delete is None

#Test displaying habits for deleting (used for confirmation) 
def test_display_habits_for_deletion(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of a new habit for testing
    habit_name = "Exercise"
    periodicity = "daily"
    insert_new_habit(habit_name, periodicity, user_id)

    #Returns a lsit of all of the user's habits
    result = display_habits_for_deletion(user_id)

    assert result is not None

#Test insert habit completion (used for check_off and complete_habit_prompt) 
def test_insert_habit_completion(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of a new habit for testing
    habit_name = "Exercise"
    periodicity = "daily"
    habit_id = insert_new_habit(habit_name, periodicity, user_id)

    #Inserts automatic completion date and habitrefID into CompletionHistory table
    insert_habit_completion(habit_id)

    cursor.execute("SELECT * FROM CompletionHistory WHERE habitrefID = %s", (habit_id,))
    result = cursor.fetchall()
    assert result is not None

#Test get habits by user (used in cli.py e.g. for completing a task) 
def test_get_habits_by_user(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of a new habit manually
    habit_name = "Exercise"
    periodicity = "daily"
    insert_new_habit(habit_name, periodicity, user_id)

    #Selects all habits belonging to this user ID and returns them as a tuple
    result = get_habits_by_user(user_id)

    assert result is not None

#Test get completion history for habit 
def test_get_completion_history_for_habit(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of a new habit
    habit_name = "Exercise"
    periodicity = "daily"
    habit_id = insert_new_habit(habit_name, periodicity, user_id)
    insert_habit_completion(habit_id)

    #Returns a list of all completion dates belonging to a specific habit as a tuple
    result = get_completion_history_for_habit(habit_id)

    assert result is not None

#Test get habits by periodicity (used for grouping the habits) 
def test_get_habits_by_periodicity(db_connection, create_test_user):
    db, cursor = db_connection
    user_id = create_test_user

    #Creation of a new habit
    habit_name = "Exercise"
    periodicity = "daily"
    insert_new_habit(habit_name, periodicity, user_id)

    #Takes userid and periodicity and queries all habits of that user that match the periodicity, returns them as a tuple
    result = get_habits_by_periodicity(user_id, periodicity)

    assert result is not None

#Testing the main function of the program
@pytest.fixture
def mock_input(monkeypatch):
    #Simulate user input for account creation
    monkeypatch.setattr("builtins.input", lambda _: "testuser6")

@pytest.fixture
def mock_getpass(monkeypatch):
    #Simulate password input for account creation
    monkeypatch.setattr("getpass.getpass", lambda _: "testpassword123")

#Test create_account function 
def test_create_account(mock_input, mock_getpass, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["python, ""cli.py", "--create_account", "--username", mock_input, "--password", mock_getpass])
    main()

#Test login function 
@pytest.fixture
def mock_input(monkeypatch):
    #Simulate input for login
    monkeypatch.setattr("builtins.input", lambda _: "testuser5")

@pytest.fixture
def mock_getpass(monkeypatch):
    #Simulate password input for login
    monkeypatch.setattr("getpass.getpass", lambda _: "testpassword")

def test_login_success(mock_input, mock_getpass, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli.py", "--login", "--username", mock_input, "--password", mock_getpass])
    main()

#Test create habit functoin (cli.py) 
@pytest.fixture
def mock_input(monkeypatch):
    #Simulate user input
    monkeypatch.setattr("builtins.input", lambda prompt: "Read" if "name" in prompt else "daily")

def test_create_habit(mock_input, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli.py", "--create_habit"])

    create_habit("22") #UserID 22 from testuser5

#Test habit deletion (cli.py) 
@pytest.fixture
def mock_input(monkeypatch):
    #Simulate user input
    monkeypatch.setattr("builtins.input", lambda prompt: "18" if "habit ID" in prompt else "yes")

def test_delete_habit_prompt(mock_input, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["cli.py", "--delete_habit", mock_input])
    delete_habit_prompt("22")

#Test habit completion (cli.py) 
@pytest.fixture
def mock_input(monkeypatch):
    #Simulate user input
    monkeypatch.setattr('builtins.input', lambda prompt: "17" if "habit ID" in prompt else "yes")

def test_complete_habit(mock_input, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['cli.py', '--complete_habit', mock_input])

    complete_habit_prompt("22")
