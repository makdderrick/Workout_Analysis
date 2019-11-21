# Workout Analysis using pandas and matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
pd.options.mode.chained_assignment = None

# Retrieves the data from the xlsx file
exercise_data = pd.read_excel('my_exercises_2.xlsx')
data_min = exercise_data[['Date','Exercise Name','Weight','Reps']]

# Removes the (Barbell) part of the exercise names which came with the data
has_barbell = data_min['Exercise Name'].str.endswith(' (Barbell)')
data_min['Exercise Name'][has_barbell] = data_min['Exercise Name'][has_barbell].str.slice(0,-10)

# Function that grabs values for a specific exercise from the data
def grab_exercise():
    exercise_name = input('Enter the name of the exercise: ')
    exercise_data = data_min[data_min['Exercise Name'] == exercise_name].iloc[::-1].reset_index(drop=True)
    exercise_data['Date'] = exercise_data['Date'].str.slice(0,-9)
    return exercise_data

# Function that calculates an estimate of the highest weight achievable given amount of reps completed for a given weight
def one_RM(weight,rep):
    top_calc = weight * (1 + rep/30)
    return round(top_calc)    

# Function that creates a dataframe of the one rep maxes for each set of each workout and takes the highest one rep max set for that day
def df_RM():  
    df = grab_exercise()
    gb = df.groupby('Date')
    l = []
    l_top_index = []
    l_RM = []
    num = 0
    groups = dict(list(gb))
    #For each date in this dictionary, find the one RM for each set and takes index of highest one RM for that day
    for key in groups.keys():
        #Iterates through each key and calculates a list of rep maxes 
        for i in range(len(groups[key])):
            weights = groups[key]['Weight'][num]
            reps = groups[key]['Reps'][num]
            top = one_RM(weights, reps)
            l.append(top)
            num+=1
        #Finds the rep max per key and adds both the index in each key and the value of that max to two lists, l_RM and l_top_index
        top_value = max(l)
        l_RM.append(top_value)
        top_index = l.index(top_value)
        l_top_index.append(top_index)
        l = []
        
    # Creates a list of the date, exercise name, weights, and reps for each daily rep max
    num = 0
    top_sets = []
    for key in groups.keys():
        top_sets.append(groups[key].iloc[l_top_index[num]])
        num+=1

    #Dataframe of all my top sets for that exercise
    df_top = pd.DataFrame(top_sets) 
    df_top['One RM'] = l_RM

    return df_top.set_index(['Date']).reset_index()

# Function that creates a dataframe of the volume (sets times reps) for each day
def df_vol():
    df = grab_exercise()
    l = []
    l_vol = []
    num = 0
    gb = df.groupby('Date')
    groups = dict(list(gb))
    
    for key in groups.keys():
        for i in range(len(groups[key])):
            weights = groups[key]['Weight'][num]
            reps = groups[key]['Reps'][num]
            volume = weights*reps
            l.append(volume)
            num +=1
            
        l_vol.append(sum(l))
        l = []
    d = {'Date' : pd.Series(list(groups.keys())),
         'Exercise Name' : pd.Series(df['Exercise Name']),
         'Volume' : pd.Series(l_vol)}
    df_vol = pd.DataFrame(d).dropna()
    return df_vol

# Function that counts the number of sets for each exercise and graphs the exercises that have more than 150 sets completed
def set_count():
    #Groups all the sets of a particular exercise
    gb = data_min.groupby(['Exercise Name'])
    gb_new = dict(list(gb))
    #Finds the number of sets completed for each exercise
    gb_count = gb.count()
    
    #Creates a dataframe of the exercise name and how many sets have been completed for that exercise
    df = pd.DataFrame()
    df['Exercise Name'] = list(gb_new.keys())
    df['Sets'] = list(gb_count['Reps'])
    
    # Creates a new dataframe that only contains exercises with more than 100 sets
    df_final = df[df['Sets']>150]
    
    
    
    #Graphing 
    ypos = np.arange(len(df_final['Exercise Name']))
    plt.yticks(ypos, df_final['Exercise Name'])
    plt.gcf().subplots_adjust(left=0.3)
    plt.barh(ypos, df_final['Sets'],color=(1, 0, 0, .2))
    plt.show()

# Function that plots the rep maxes for specific exercises
def plot_RM(df_RM):
    #Converts the Date column of df_top from strings to pandas datetime 
    df_RM['Date'] = pd.to_datetime(df_RM['Date'])

    #Plot Date vs One RM 
    plt.plot(df_RM['Date'], df_RM['One RM'], label = df_RM['Exercise Name'][0])
    ax = plt.gca()

    #Increases the space on the bottom
    plt.gcf().subplots_adjust(bottom=0.25)

    #Sets the x-axis to be divided into months at an interval of three months per tick
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval = 3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    #Rotates the xticks
    plt.xticks(rotation=50)

    #Plot Labels
    plt.xlabel('Date')
    plt.ylabel('One RM (lbs)')
    plt.title('Daily Estimated Rep Maxes Over Several Years')

# Function that plots the volumes for specific exercises
def plot_vol(df_vol):
    df_vol['Date'] = pd.to_datetime(df_vol['Date'])
    
    #Plot Date vs Volume
    plt.plot(df_vol['Date'], df_vol['Volume'], label = df_vol['Exercise Name'][0])
    ax = plt.gca()

    #Increases the space on the bottom
    plt.gcf().subplots_adjust(bottom=0.25)

    #Sets the x-axis to be divided into months at an interval of three months per tick
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval = 3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    #Rotates the xticks
    plt.xticks(rotation=50)

    #Plot Labels
    plt.xlabel('Date')
    plt.ylabel('Volume')
    plt.title('Daily Change in Volume Over Several Years')
    
# Calling functions
data_type = int(input("""What kind of data are you looking for (Enter Number)?:
Options: 
1) One RMs 
2) Volume 
3) Percentage Increase from Start
4) Most Popular Exercises (Over 150 Sets)
You entered: """))

if data_type == 1:
    num = int(input('How many exercises do you want to plot: '))
    for i in range(num):
        exercise = df_RM()
        plot_RM(exercise)
    plt.legend(loc = 'upper left')
    plt.tight_layout()
    plt.show()

elif data_type == 2:
    num = int(input('How many exercises do you want to plot: '))
    for i in range(num):
        exercise = df_vol()
        plot_vol(exercise)
    plt.legend(loc = 'upper left')
    plt.tight_layout()
    plt.show()
    
elif data_type == 3:
    num = int(input('How many exercises do you want to plot: '))
    for i in range(num):
        exercise = df_RM()
        exercise['One RM']/=exercise['One RM'][0]/100
        plot_RM(exercise)
    plt.xlabel('Date')
    plt.ylabel('One RM Percentage')
    plt.title('Percentage Compared to Initial One RM Over Several Years')
    plt.legend(loc = 'upper left')
    plt.tight_layout()
    plt.show()
    
elif data_type == 4:
    set_count()
