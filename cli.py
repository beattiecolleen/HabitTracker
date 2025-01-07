#Command Line Interface
"""
Users can run commands like:
python cli.py --login --username janedoe --password janespassword --view_streak
or:
python cli.py :An interactive menu will show up where users can select the same actions as via the argparse statements
"""
#import libraries
import argparse
import bcrypt
import getpass
from habit import Habit
#calls function from database to handle database operations
from database import (insert_new_user, get_user_by_username, insert_new_habit, 
                      delete_habit, display_habits_for_deletion, get_habits_by_user, 
                      insert_habit_completion, get_completion_history_for_habit, 
                      get_habits_by_periodicity)
#import from analytics.py
from analytics import average_completion_time, most_consistent_habit, aggregate_streak_analysis


#Definition of functions that are called later
#Definition of create_habit function
def create_habit(user_id):
    print("Create a new habit: ")
    habit_name = input("Please enter the name of the new habit: ")
    periodicity = input("Please enter the periodicity (daily, weekly, monthly): ")

    if periodicity.lower() not in ['daily', 'weekly', 'monthly']:
        print("Invalid periodicity. Please enter one of the pre-selected ones.")
        return

    #Save habit to database
    insert_new_habit(habit_name, periodicity.lower(), user_id)
    print(f"Habit '{habit_name}' created successfully!")

 #Definition of delete_function
def delete_habit_prompt(user_id):
    #Get habits for the user by calling display function from database.py
    habits = display_habits_for_deletion(user_id)
    #Loops through the habits of that user or returns an error message if there are none
    if not habits:
        print("You have no habits to delete.")
        return
    
    print("Your habits: ")
    for habit in habits:
        print(f"ID: {habit[0]} | Name: {habit[1]} | Periodicity: {habit[2]}")
    
    #Prompt for habit ID to delete habit
    habit_id = input("Please enter the ID of the habit you want to delete: ")
    #Only allow numbers
    if not habit_id.isdigit():
        print("Invalid input. Please enter a number as a habit ID.")
        return
    
    habit_id = int(habit_id)

    #Confirm deletion to ensure the user doesN#t accidentally delete a habit
    confirm = input(f"Are you sure you want to delete habit {habit_id}? (yes / no): ")
    if confirm == "yes":
        success = delete_habit(habit_id, user_id)
        if success:
            print("Habit deleted successfully!")
        else:
            print("Failed to delete habit. Please enter the correct habit ID")
    else:
        print("Invalid entry. The deletion is cancelled.")

#Function to allow users to complete a habit
def complete_habit_prompt(user_id):
    #Get the user's habits
    habits = get_habits_by_user(user_id)
    if not habits:
        print("You have no habits to complete.")
        return
    print("Your habits: ")
    for habit in habits:
        print(f"ID : {habit[0]} | Name: {habit[1]} | Periodicity: {habit[2]}")

    #Prompt for habit ID to complete habit
    habit_id = input("Please enter the ID of the habit you want to mark as complete: ")

    if not habit_id.isdigit():
        print("Invalid input. Please enter a number.")
        return
    
    habit_id = int(habit_id)

    #Make sure the habit belongs to the user
    selected_habit = next((h for h in habits if h[0] == habit_id), None)
    if not selected_habit:
        print("Invalid habit ID. Please select a valid habit.")
        return
    
    #Use the habit class (habit.py) to log the completion
    habit = Habit(name = selected_habit[1], periodicity = selected_habit[2])
    habit.check_off()

    #Insert the completion into the database
    insert_habit_completion(habit_id)

    print(f"Habit '{habit.name}' marked as complete!")

#Function to allow a user to select a habit and calculate a streak for it
def view_habit_streak(user_id):
    #Get the habits of the user
    habits = get_habits_by_user(user_id)

    if not habits:
        print("You have no habits to view.")
        return
    
    print("Your habits: ")
    for habit in habits:
        print(f"ID : {habit[0]} | Name: {habit[1]} | Periodicity: {habit[2]}")

    #Prompt for habit Id to view the streak
    habit_id = input("Please enter the ID of the habit to view the streak for: ")

    if not habit_id.isdigit():
        print("Invalid input. Please enter a number.")
        return
    
    habit_id = int(habit_id)

    #Make sure the habit belongs to the user
    selected_habit = next((h for h in habits if h[0] == habit_id), None)
    if not selected_habit:
        print("Invalid habit ID. Please select a valid habit ID.")
        return
    
    #Get the habit completion history from the database
    completions = get_completion_history_for_habit(habit_id)

    #Create a habit object to calculate the streak
    habit = Habit(name=selected_habit[1], periodicity=selected_habit[2])

    #Add the completion history to the habit object
    habit.completion_history = [completion[0] for completion in completions]

    #Calculate and display the streak
    habit.calculate_streak()

#Function to calculate the longest streak for a specific habit
def view_longest_streak(user_id):
    #Get the habits of the user
    habits = get_habits_by_user(user_id)

    if not habits:
        print("You have no habits to view.")
        return
    
    print("Your habits: ")
    for habit in habits:
        print(f"ID: {habit[0]}| Name: {habit[1]} | Periodicity: {habit[2]}")

    #Prompt for habit ID to view the longest streak for that habit
    habit_id = input("Please enter the ID of the habit you want to calculate the current streak for: ")

    if not habit_id.isdigit():
        print("Invalid input. Please enter a number.")
        return
    
    habit_id = int(habit_id)

    #Make sure the habit belongs to the user
    selected_habit = next((h for h in habits if h[0] == habit_id), None)
    if not selected_habit:
        print("Invalid habit ID. Please select a valid habit.")
        return
    
    #Get the completion history from the database
    completions = get_completion_history_for_habit(habit_id)

    #Create a habit object to calculate the longest streak for this habit
    habit = Habit(name=selected_habit[1], periodicity=selected_habit[2])

    #Add the completion history to the habit object and extract the completion dates from the result
    habit.completion_history = [completion[0] for completion in completions]

    #Calculate and display the longest streak
    habit.calculate_streak()
    print(f"The longest streak for '{habit.name}' is {habit.longest_streak} completions in a row.")

#Function to allow a user to calculate the longest streak across all habits
def view_longest_streak_across_all_habits(user_id):
    #Get all habits of the user
    habits = get_habits_by_user(user_id)

    if not habits:
        print("You have no habits to view.")
        return
    
    #Track the overall longest streak
    longest_streak = 0
    #Track the habit with the longest streak
    longest_streak_habit = None

    print("Calculating the longest streak accross all you habits ...")

    #Iteratre through all the habits and calculate their longest streaks
    for habit in habits:
        habit_id = habit[0]
        habit_name = habit[1]
        habit_periodicity = habit[2]

        #Get the habit completion history from the database
        completions = get_completion_history_for_habit(habit_id)

        #Create a habit object
        habit_object = Habit(name=habit_name, periodicity=habit_periodicity)

        #Add the completion history to the object
        habit_object.completion_history = [completion[0] for completion in completions]

        #Calculate the streak for the current habit
        habit_object.calculate_streak()

        #Check if this habit's streak is the longest
        if habit_object.longest_streak > longest_streak:
            longest_streak = habit_object.longest_streak
            longest_streak_habit = habit_object.name
    
    #Display the result
    if longest_streak_habit:
        print(f"The longest streak across all of your habits is {longest_streak} completions for the habit '{longest_streak_habit}'.")
    else:
        print("No streaks found for you habits. Complete a habit first.")

#Function to display all habits belonging to a user
def display_user_habits(user_id):
    #Get all habits for the user
    habits = get_habits_by_user(user_id)

    #Make sure there are habits
    if not habits:
        print("You have no habits to display.")
        return
    
    #Display the habits:
    print("Your habits: ")
    for habit in habits:
        print(f"ID: {habit[0]}| Name: {habit[1]} | Periodicity: {habit[2]}")

#Function to get the most challenging habit of a user
def display_most_challenging_habit(user_id):
    #Get the user's habits
    habits = get_habits_by_user(user_id)

    if not habits:
        print("You have no habits do display.")
        return
    
    most_challenging_habit = None
    max_streak_break = 0

    #Loop through the habits to calculate the streak breaks
    for habit in habits:
        habit_id, habit_name, periodicity = habit[:3]

        #Get the completion history for the habit
        completions = get_completion_history_for_habit(habit_id)
        #Skips the habit if there are no completions
        if not completions:
            continue
        
        #Get the dates from the tuples that were returned
        completion_dates = [completion[0] for completion in completions]
        #Sort the dates in chronologica order
        completion_dates.sort()

        #Calculate the streak breaks
        streak_breaks = 0
        for i in range(1, len(completion_dates)):
            #Get the two consecutive completion dates
            current_date = completion_dates[i]
            previous_date = completion_dates[i-1]

            #Calculate the gap between consecutive completions
            gap = (current_date - previous_date).days

            #Check for streak breaks based on the periodicity
            if periodicity == "daily" and gap > 1:
                streak_breaks +=1
            elif periodicity == "weekly" and gap >7:
                streak_breaks +=1
            elif periodicity == "monthly" and gap > 30:
                streak_breaks +=1

        #Track the most challenging habit
        if streak_breaks > max_streak_break:
            max_streak_break = streak_breaks
            most_challenging_habit = habit

    #Display the results
    if most_challenging_habit:
        print("Most challenging habit: ")
        print(f"ID: {most_challenging_habit[0]}| Name: {most_challenging_habit[1]}| Periodicity: {most_challenging_habit[2]}")
        print(f"Number of streak breaks: {max_streak_break}")
    else:
        print("No challenging habits were found. Good job!")

#Function to group habits by periodicity
def group_habits_by_periodicity(user_id):
    print("Group Habits by Periodicity: ")
    print("1. Daily Habits.")
    print("2. Weekly Habits.")
    print("3. Monthly Habits.")

    group_choice = input("Which habits do you want to display? (1/2/3): ")

    if group_choice == "1":
        periodicity = "daily"
    elif group_choice == "2":
        periodicity = "weekly"
    elif group_choice == "3":
        periodicity = "monthly"
    else:
        print("Invalid input. Please enter 1, 2, or 3.")
        return
    
    #Get the habits from database
    habits = get_habits_by_periodicity(user_id, periodicity)

    if habits:
        for habit in habits:
            print(f"ID: {habit[0]}| Name: {habit[1]}")
    else:
        print(f"No {periodicity} habits were found.")

#Function to implement analytics.py
def view_analytics(user_id):
    #Get habit completion data from the database
    habits = get_user_by_username(user_id)
    if not habits: 
        print("No habits available for analytics.")
        return
    #Get data for analytics
    habit_data = {}
    for habit in habits:
        habit_id, habit_name, _ = habit[:3]
        completions = get_completion_history_for_habit(habit_id)
        completion_dates = [completion[0] for completion in completions]
        habit_data[habit_name] = completion_dates
    #Perform analytics
    avg_completion_times = {
        habit: average_completion_time(dates) for habit, dates in habit_data.items()
    }
    consistent_habit = most_consistent_habit(habit_data)
    streak_summary = aggregate_streak_analysis(
        {habit: len(dates) for habit, dates in habit_data.items()}
    )
    #Display results
    print("Habit Analytics: ")
    print("-" * 30)
    print("Average completion time in days: ")
    for habit, avg_time in avg_completion_times.items():
        print(f"{habit}: {avg_time:.2f}" if avg_time else f" {habit}: Not enough data.")
    print(f"Most Consistent Habit: {consistent_habit}")
    print(f"Aggregate Streaks: {streak_summary}")


"""
THE MAIN PROGRAM BEGINS HERE
"""

#Display CLI Home Menu
#Argparse is added here
def parse_args():
    parser = argparse.ArgumentParser(description="HabitTracker CLI")

    #Arguments for user actions that don't require login
    parser.add_argument("--create_account", action="store_true", help="Create a new account.")
    parser.add_argument("--login", action="store_true", help="Log into an existing account.")

    #Arguments for actions that can be performed after login
    parser.add_argument("--create_habit", action="store_true", help="Create a new habit.")
    parser.add_argument("--delete_habit", action="store_true", help="Delete an existing habit.")
    parser.add_argument("--complete_habit", action="store_true", help="Complete a habit.")
    parser.add_argument("--view_streak", action="store_true", help="View habit streak.")
    parser.add_argument("--view_longest_streak", action="store_true", help="View longest streak for a specific habit.")
    parser.add_argument("--view_all_streaks", action="store_true", help="View longest streak across all habits.")
    parser.add_argument("--display_habits", action="store_true", help="Display all habits.")
    parser.add_argument("--challenging_habit", action="store_true", help="Display the most challenging habit.")
    parser.add_argument("--group_habits", action="store_true", help="Group habits by periodicity.")
    parser.add_argument("--analytics", action="store_true", help="View habit analytics.")

    parser.add_argument("--username", type=str, help="Username for login.")
    parser.add_argument("--password", type=str, help="Password for login.")

    return parser.parse_args()

#Main function for starting the app with argparse
def main():
    args = parse_args()

    #Creation of a new account
    if args.create_account:
        username_input = input("Please select your username: ")
        password_input = getpass.getpass("Please select your password: ")
        hashed_password = bcrypt.hashpw(password_input.encode('utf-8'), bcrypt.gensalt())
        insert_new_user(username_input, hashed_password.decode('utf-8'))
        print("Account created successfully!")
    
    #Login via argparse
    elif args.login:
        if not args.username or not args.password:
            print("Username and password are required for login.")
            return
    
        user_data = get_user_by_username(args.username)
        if user_data is None:
            print("Username not found. Please try again or create an account.")
            return
        
        stored_user_id, stored_hashed_password = user_data
        if bcrypt.checkpw(args.password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            print(f"Login successful! Welcome, user {stored_user_id}!")


            #After login: Check for actions
            if args.create_habit:
                create_habit(stored_user_id)
            elif args.delete_habit:
                delete_habit_prompt(stored_user_id)
            elif args.complete_habit:
                complete_habit_prompt(stored_user_id)
            elif args.view_streak:
                view_habit_streak(stored_user_id)
            elif args.view_longest_streak:
                view_longest_streak(stored_user_id)
            elif args.view_all_streaks:
                view_longest_streak_across_all_habits(stored_user_id)
            elif args.display_habits:
                display_user_habits(stored_user_id)
            elif args.challenging_habit:
                display_most_challenging_habit(stored_user_id)
            elif args.group_habits:
                group_habits_by_periodicity(stored_user_id)
            elif args.analytics:
                view_analytics(stored_user_id)
            else:
                print("Invalid action. Please specify a valid argument.")
        else:
            print("Incorrect password. Please try again.")

    #If no arguments are provided, use an interactive menu
    else:
        print("Welcome to HabitTracker!")
        print("1. Create a new account.")
        print("2. Log in to an existing account.")
        choice = input("Please select what you want to do (1/2): ")

        if choice == "1":
            username_input = input("Please select your username: ")
            password_input = getpass.getpass("Please select your password: ")
            hashed_password = bcrypt.hashpw(password_input.encode('utf-8'), bcrypt.gensalt())
            insert_new_user(username_input, hashed_password.decode('utf-8'))
            print("Account created successfully!")

        elif choice == "2":
            entry_username = input("Please enter your username: ")
            entry_password = input("Please enter your password: ")
            user_data = get_user_by_username(entry_username)
            if user_data is None:
                print("Username not found. Please try again or create an account.")
                return
            
            stored_user_id, stored_hashed_password = user_data
            if bcrypt.checkpw(entry_password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                print(f"Login successful! Welcome, user {stored_user_id}!")

                # After login  show the action menu
                while stored_user_id:
                    print("---------------------------------------------------------")
                    print("1. Create Habit.")
                    print("2. Delete Habit.")
                    print("3. Complete Habit.")
                    print("4. View Streak for a Specific Habit.")
                    print("5. View Longest Streak for a Specific Habit.")
                    print("6. View Longest Streak across all Habits.")
                    print("7. Display all Habits.")
                    print("8. Display the Most Challenging Habit.")
                    print("9. Group Habits by Periodicity.")
                    print("10. View Analytics.")
                    print("11. Logout.")
                    action = input("What would you like to do?: ")

                    if action == "1":
                        create_habit(stored_user_id)
                    elif action == "2":
                        delete_habit_prompt(stored_user_id)
                    elif action == "3":
                        complete_habit_prompt(stored_user_id)
                    elif action == "4":
                        view_habit_streak(stored_user_id)
                    elif action == "5":
                        view_longest_streak(stored_user_id)
                    elif action == "6":
                        view_longest_streak_across_all_habits(stored_user_id)
                    elif action == "7":
                        display_user_habits(stored_user_id)
                    elif action == "8":
                        display_most_challenging_habit(stored_user_id)
                    elif action == "9":
                        group_habits_by_periodicity(stored_user_id)
                    elif action == "10":
                        view_analytics(stored_user_id)
                    elif action == "11":
                        print("Goodbye!")
                        break
                    else:
                        print("Invalid option.")
            else:
                print("Incorrect password. Please try again.")

if __name__ == "__main__":
    main()