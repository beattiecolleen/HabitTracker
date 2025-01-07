#Habit class

#import datetime
from datetime import datetime, timedelta

#Definition of the class
class Habit:
    #Initialisation of the habit
    def __init__(self, name, periodicity, created_at=None):
        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()
        self.streak = 0
        self.completion_history = []
    
    #Definition of the check_off function
    def check_off(self):
        #Log a completion timestamp and update the streak
        timestamp = datetime.now()
        self.completion_history.append(timestamp)
        self.calculate_streak()
        print(f"Habit '{self.name}' marked as complete '{timestamp}'.")

    #Definition of the calculate streak function
    def calculate_streak(self):
        #Calculation of the streak based on the completion history
        streak = 0
        longest_streak = 0
        last_completed = None

        for completion in sorted(self.completion_history)   :
            if not last_completed:
                last_completed = completion
                streak = 1
            else:
                #Check if the streak is continous based on the periodicity
                if self.is_continuous(last_completed, completion):
                    streak += 1
                else:
                    #Update longest streak if current streak ends
                    longest_streak = max(longest_streak, streak)
                    streak = 1 #Resets the streak count
                last_completed = completion

        self.longest_streak = max(longest_streak, streak)
        self.streak = streak
        print(f"Longest streak for '{self.name}': {self.longest_streak} completions in a row.")
        print(f"Current Streak for '{self.name}': {self.streak} completions in a row. ")

    def is_continuous(self, last_completed, current_completed):
        #Check if the habit completion is continuous based on the periodicity
        if self.periodicity == "daily":
            #Check if the current completion date is the next day
            return current_completed.date() == (last_completed + timedelta(days=1)).date()
        
        elif self.periodicity == "weekly":
            #Check if the current completion date is the same day of the week
            return current_completed.weekday() == last_completed.weekday() and (current_completed - last_completed).days <= 7
        
        elif self.periodicity == "monthly":
            #Check if the current completion date is in the same month
            return current_completed.month == last_completed.month and current_completed.year == last_completed.year
        
        return False #Default case if the periodicity doesn't match


    #Definition of the 'streak is broken' function
    def is_broken(self):
        if not self.completion_history:
            print(f"No completions recorded for '{self.name}'. Streak cannot be broken.")
            return False
        last_completed = self.completion_history[-1]
        now = datetime.now()
        if self.periodicity == "daily":
            return now.date() > (last_completed + timedelta(days=1)).date()
        elif self.periodicity == "weekly":
            return (now - last_completed).days > 7
        elif self.periodicity == "monthly":
            next_month = (last_completed.month % 12) + 1
            next_year = last_completed.year + (last_completed.month // 12)
            return now.month > next_month or now.year > next_year
        else:
            raise ValueError(f"Invalid periodicity: {self.periodicity}")