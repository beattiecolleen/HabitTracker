from datetime import datetime

#Calculation of the average time between completions of a habit
def average_completion_time(completion_dates):
    #Need enough data for the calculation
    if len(completion_dates) <2:
        return None
    #Sorting the dates
    sorted_dates = sorted(completion_dates)
    time_differences = [
        (sorted_dates[i] - sorted_dates [i-1]).days for i in range(1, len(sorted_dates))
    ]
    return sum(time_differences) / len(time_differences)

#Calculation of the habit with the most consistent completions
def most_consistent_habit(habit_data):
    def consistency_score(dates):
        if len(dates) <2:
            return float('inf')
        sorted_dates = sorted(dates)
        gaps = [
            (sorted_dates[i] - sorted_dates[i-1]).days for i in range(1, len(sorted_dates))
        ]
        #The smaller the score, the more consistent it is
        return max(gaps) - min(gaps)
    return min(habit_data, key=lambda habit: consistency_score(habit_data[habit]))

#Calculation of total and average streaks across all habits
def aggregate_streak_analysis(habit_data):
    def count_streaks(dates):
        if not dates:
            return 0
        
        streaks = 0
        sorted_dates = sorted(dates)

        #Counts the streak by checking if each completion is on consecutive dates (no gaps, streak not broken)
        curent_streak = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                curent_streak += 1
            else:
                if curent_streak > 1:
                    streaks += 1
                curent_streak = 1
        #Checking the last streak
        if curent_streak > 1:
            streaks += 1
        return streaks

    total_streaks = sum(count_streaks(dates) for dates in habit_data.values())
    avg_streaks = total_streaks / len(habit_data) if habit_data else 0
    return {"total streaks" : total_streaks, "average streaks" : avg_streaks}
