'''
Draw randomly from applications Emergency Relief Fund to Support the Packard Foundation Fellows 

https://updates.sciphil.org/apply-for-packard-fellows-emergency-relief-fund?hs_preview=WEbFTGDa-205255484080

Written by Tom Stafford for SPA 2026

uses the conda environment defined in environment.yml

(conda env create -f environment.yml)

'''


# region----- customisation


# inputs THESE ARE THE ONLY BITS THAT NEED CHANGING

# 1 THE BUDGET
#budget = 3.3*1000*1000 #3.3 million
budget = 0.5*1000*1000
#2 APPLICATION FILE
application_file = 'example.csv'


# TOGGLES
SAVEENV = False #toggle, export conda environment
PAUSES = True #True #toggle, pause before each step

#endregion


# region-----------------------------------------------   set up environment


# ---- libraries we'll use

import os #file and folder functions
import pandas as pd #dataframes!
import numpy as np #number functions
import datetime
from hashlib import sha512 as _sha512
from time import sleep
# ---- set up working directory

print("We are in :" + os.getcwd())
    
#export environment in which this was last run
if SAVEENV:
    os.system('conda env export > environment.yml') 

print("Our conda environment is : " + os.environ['CONDA_DEFAULT_ENV'])

#get datetime in ISO8601 format
now=datetime.datetime.now().isoformat()[:16]
print("Time is now : " + now)



#endregion


# region ----------- initialise

# RANDOM SEED
# get random seed by loading the Merriam-Webster word of the day

url = 'https://www.merriam-webster.com/word-of-the-day'

#curl
os.system('curl -s ' + url + ' > word.txt')

#load file line by line until the <title> tag is found
with open('word.txt', 'r') as f:
    for line in f:
        if '<title>' in line:
            break

#drop everything after the |
line = line.split('|')[0]

#drop everything before the :
line = line.split(':')[1]

#drop leading and trailing spaces
line = line.strip()

print("The word of the day and our random seed is : " + line +"\n\n")


# convert to integer
# following https://stackoverflow.com/questions/67577068/why-does-numpy-disallows-string-seed-but-the-random-library-allows-it-in-python

seed = line.encode()
seed = int.from_bytes(seed + _sha512(seed).digest(), 'big')

#take remaineder so is right size
seed = seed % 2**32

#seed = 13 #you can overrule the seed for testing 

#seed is set below, just before the draw

# LOAD DATA
# Now read in data, validate data, confirm budget



print ("Budget is " + str(budget) + " USD")
estimated_projects = budget / 82500
print ("Estimated number of fundableprojects is " + str(estimated_projects))


print ("Loading application data from " + application_file)
df = pd.read_csv(application_file,sep='\t') #tab seperated in case titles contain commas

print ("Application file has " + str(len(df)) + " rows")

print("Breaking applications by career level")
print(df.groupby('career-level')['title'].count().to_string())

#total request
total_request = df['budget'].sum() + df['indirect'].sum()
print ("Total request is " + str(total_request) + " USD")

if total_request > budget:
    print ("Total request is greater than budget\n\n")
else:
    print ("WARNING: Total request is less than budget\n\n")

df['award'] = df['budget']+df['indirect']

df['weight'] = 1
#df['weight] should be 2 if career-level is "mid", 1 otherwise
# iterate over df, set weight to 2 if career-level is "mid"
for index, row in df.iterrows():
    if row['career-level'][:3] == 'mid':
        df.loc[index, 'weight'] = 2


if PAUSES:
    #require key to continue
    key = input("Press enter to continue")


if PAUSES:
    print ("We are now ready for the draw,")
    key = input("Press enter to continue")


#endregion


#region ----------- draw

# THIS IS WHERE THE MAGIC HAPPENS
print("- - NOW THE DRAW - - - \n")
np.random.seed(seed) #set a random seed, which allows the same draw to be reproduced

remaining_budget = budget #we need to track the budget as we allocate awards

winners = pd.DataFrame() #we will store the winners here

# now we make random draws until we run out of budget
while (remaining_budget > 0) and not df.empty:

    #pick a random row, respecting the weighting
    row = df.sample(n=1, weights='weight')

    #add row to list of winners
    winners = pd.concat([winners, row])

    #update remaining budget
    remaining_budget = remaining_budget - row['award'].values[0]

   #report
    print ("We have drawn: " + row['title'].values[0] + "; request = " + str(row['award'].values[0]) + " USD; Remaining budget is " + str(remaining_budget) + " USD")

    #delete winning row from df, so it can't be picked again
    df = df.drop(row.index)

    #a delay to slow things down
    if PAUSES:
        sleep(0.5)

# for the final row in winners, subtract remaining budget from the award value
last_index = winners.index[-1]
winners.at[last_index, 'award'] += remaining_budget


print("\n\nAll done!")
print ("We have drawn " + str(len(winners)) + " winners")

#endregion

# region ----------- report

#summarise by career level, reporting only one column
print(winners.groupby('career-level')['title'].count().to_string())

#total award
print ("Total award is " + str(winners['award'].sum()) + " USD")


#save winners to file
winners.to_csv('winners.csv')
print("winners.csv saved")


#endregion
