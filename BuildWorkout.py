import argparse
import pprint as pp
from itertools import chain
import pandas as pd
from TransitionMatrix import get_matrix
import numpy as np
import random
import os
import sys
import copy

# Declare the global variables
difficulty_levels = ['Easy', 'Medium', 'Hard']

difficulty_cycles = {
    0.00: [0],
    0.13: [0,0,0,1],
    0.17: [0,0,1],
    0.25: [0,1],
    0.33: [0,0,1,2,1],
    0.38: [0,0,1,2],
    0.46: [0,1,1,2,1],
    0.5:  [[0,1,2,1], [0,2]],
    0.62: [0,1,2,2],
    0.63: [0,1,2,2,0],
    0.75: [1,2],
    0.83: [1,2,2],
    0.88: [[1,2,2,2], [1,2,2,2,2]],
    1.0:  [2],
}

tsv_headers = [
        "Name",
        "Target Muscle",
        "Instructions",
        "Difficulty",
        "Impact",
        "Muscle Group(s)",
        "Easier Modification",
        "Harder Modification",
        "Equipment Required",
        "Is Stretch",
        "Smooth Ground Required",
        "Link"]

equipment_list = [
            "wall", 
            "dumbbell",
            "resistance band",
            "resistance loop",
            "kettlebell",
            "foam roller",
            "chair"]      

    
target_subregions = {
    'arms':
            [
            'biceps',
            'triceps'
            ]
    ,
    'core':
        [   
            'abs',
            'upper back',
            'lower back'
        ]
    ,  
    'legs':
        [
            'calves',
            'glutes',
            'hamstrings',
            'quadriceps'
        ]
    ,
    'upper body':
        [
            'arms',
            'chest',
            'shoulders'
        ]
    }            
# The variables above and below are not accidently duplicated
# They are slightly different and serve different roles
target_regions_list = [
    'abs',
    'chest',
    'hip flexor',
    'shoulders',    
    {'arms':
            [
            'biceps',
            'triceps'
            ]
    },
    {'core':
        [   
            'abs',
            'upper back',
            'lower back'
        ]
    },  
    {'legs':
        [
            'calves',
            'glutes',
            'hamstrings',
            'quadriceps'
        ]
    },
    {'upper body':
        [
            'arms',
            'chest',
            'shoulders'
        ]
    }
]

# Create a single unified set of all muscles
all_regions = set()
for region in target_regions_list:
    if isinstance(region, str):
        all_regions.add(region)
    else:
        all_regions |= set(region.keys())
        all_regions |= set(list(region.values())[0])

print("Formatting some variables for pretty printing.")
headers = pp.pformat(tsv_headers)
equipment = pp.pformat(sorted(equipment_list))
target_regions = pp.pformat(target_regions_list)

def valid_equipment(equipment):
    if equipment not in equipment_list:
        raise argparse.ArgumentTypeError(f'{equipment} is not valid equipment.')
    else:
        return equipment

def valid_region(region):
    if region not in all_regions:
        raise argparse.ArgumentTypeError('Invalid body part to target.')
    else:
        return region

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def difficulty_type(x):
    x = int(x)
    if x < 0 or x > 100:
        raise argparse.ArgumentTypeError("Difficulty must be in range 0-100")
    return x

def impact_level(x):
    impact_levels = ['Low', 'Normal', 'High']
    if x not in impact_levels:
        raise argparse.ArgumentTypeError(f"Impact must one of {impact_levels}")
    return x


parser = argparse.ArgumentParser(
            description='Build workout plan from database of excercises.',
            formatter_class=argparse.RawTextHelpFormatter
        )

parser.add_argument(
            'database', 
            type=argparse.FileType('r'),
            help=f".csv database of excercises with these headers:\n{headers}"
        )                    
parser.add_argument(
            'difficulty', 
            type=difficulty_type, 
            help='Pick a difficulty between 0-100 inclusive'
        )
parser.add_argument(
            'smooth_surface', 
            type=str2bool, 
            help='True if a smooth surface (e.g. concrete pad, gym floor) \n' + 
            'is available, else False (e.g. grass, asphalt)'
        )      
parser.add_argument(
            '-t',                
            '--target_regions', 
            action="append",
            required=True,
            type=valid_region, 
            help='Pick at least one of the following\n' + 
                 f'(Can choose whole regions or specific muscles):\n' + 
                 f'{target_regions})'
        )                             
parser.add_argument(
            '-e',
            '--equipment',
            type=valid_equipment,
            action='append',
            help=f'List all of equipment available from the list below:\n'+
                f'{equipment}'
        )

parser.add_argument(
            '-n',
            '--number',
            type=int,
            default=0,
            help=f'The Number of excercises to include (Default: 3* # targets)'
        )

parser.add_argument(
            '-i',
            '--impact-level',
            type=str,
            default="High",
            help=f'The maximum impact level' + 
                '(e.g. "Low", "Normal", "High" (Default)) (Default: "High")'
        )

parser.add_argument(
            '-s',
            '--stretch',
            type=str2bool,
            default=True,
            help=f'Include warm up and cool down stretches? (True/False)' +
                 f'(Default: True)'
        )      

parser.add_argument(
            '-p',
            '--prng-seed',
            type=int,
            default=42,
            help=f'PRNG seed to ensure reproducibility'
        )                        

parser.add_argument(
            '-v',
            '--verbose',
            type=str2bool,
            default=False,
            help=f'False by default, but set to True for detailed debugging'
        )  

args = parser.parse_args()
if args.verbose:
    print(args)

np.random.seed(args.prng_seed)
random.seed(args.prng_seed)
if not args.equipment:
    args.equipment = set()
else:
    args.equipment = set(args.equipment)

print("Parsing targeted muscle groups")
all_muscle_groups = set()
for group in args.target_regions:
    if group in target_subregions:
        all_muscle_groups |= set(target_subregions[group])
    else:
        all_muscle_groups.add(group)

all_muscle_groups = sorted(list(all_muscle_groups))[::-1]
if not args.number:
    args.number = len(all_muscle_groups)*3

print("Reading provided database")
df = pd.read_csv(args.database, sep='\t')
df = df.sort_values('Name')
print("Computing transition matrix based on difficulty")
tm = get_matrix(args.difficulty)
#print(df)
plan = []
drop_indices = []
print("Dropping irrelevant excercises - this could take a minute")
df = df.dropna(subset=['Muscle Group(s)']) 
index_names = ''
if args.impact_level == "Low":
   # Get indices where of High and Medium impact excercises
   index_names = df[(df['Impact'] == 'High') | (df['Impact'] == 'Normal')].index

elif args.impact_level == "Normal":
    # Get indices where of High impact excercises
    index_names = df[df['Impact'] == 'High'].index

# Drop any excercises with impact any higher than the max impact specified
if any(index_names):
    df.drop(index_names, inplace=True)

ex_muscle_group_dict = {}
stretch_muscle_group_dict = {}

for row_index, row in df.iterrows():
    row_tgts = set(row['Muscle Group(s)'].split(","))

    # Drop any excercise that don't target the desired muscles
    if not row_tgts.intersection(all_muscle_groups):
        drop_indices.append(row_index)
        #print(f"Dropping {row['Name']}; wrong target regions")

    # If smooth ground is not available, drop any excercises that require it
    elif not args.smooth_surface and row['Smooth Ground Required']:
        drop_indices.append(row_index)
        #print(f"Dropping {row['Name']} as it requires smooth ground")

    # Drop excercises that require equipment that is not available
    elif (isinstance(row['Equipment Required'], str) and 
        not set([x.lower() for x in row['Equipment Required'].split(',')]).issubset(args.equipment)):
        drop_msg =  f"Dropping {row['Name']} due to missing equipment:" + \
                    f" {row['Equipment Required']}"
        if args.verbose:
            print(drop_msg)
        drop_indices.append(row_index)

    # Keep this excercise
    # Also create a dict mapping the excercise name to a set of muscles worked
    else:
        if not row['Is Stretch']:
            ex_muscle_group_dict[row['Name']] = row_tgts
        else:
            stretch_muscle_group_dict[row['Name']] = row_tgts

print("Separating stretches and excercises")

df = df.drop(index=drop_indices)
stretches = df[df['Is Stretch']]
excercises = df[~df['Is Stretch']]
targets = []

def build_plan(args, 
                excercises,  # Can be excercises OR stretches!
                muscle_group_dict,
                stretch=False):
    if stretch:
        args.number = len(muscle_group_dict)


    


    # Finally build the workout plan with N excercises total (excluding stretches)
    print("Finding best difficulty cycle")
    best_cycle = None
    best_cycle_dist = 10
    best_cycle_key = 0
    for key, value in difficulty_cycles.items():
        print(f"Examining {key}:{value}")

        if not isinstance(value[0], list):
            if  key == 0 or \
                key == 1 or \
                (len(all_muscle_groups) != len(value) and (len(all_muscle_groups)%len(value))):
                if abs(args.difficulty/100 - key) < best_cycle_dist:
                    best_cycle = value
                    best_cycle_key = key
                    best_cycle_dist = abs(args.difficulty/100 - key )
                    print(f"Updating current best as {best_cycle_dist} {key}:{value}")

        else:
            for cycle in value:
                if len(all_muscle_groups) != len(cycle) and (len(all_muscle_groups)%len(cycle)):
                    if abs(args.difficulty/100 - key) < best_cycle_dist:
                        print(f"Updating current best as {key}:{value}")

                        best_cycle = cycle
                        best_cycle_key = key
                        best_cycle_dist = abs(args.difficulty/100 - key )
                        print(f"Updating current best as {best_cycle_dist} {key}:{value}")

    # Difficulty level determines the difficulty of the first excercise
    # Randomly pick the first exercise from the corresponding difficulty levels
    '''
    if args.difficulty < 33:
        plan = excercises[excercises['Difficulty'] == 'Easy'].sample(random_state=args.prng_seed)
        state = 0
    elif args.difficulty < 67:
        plan = excercises[excercises['Difficulty'] == 'Medium'].sample(random_state=args.prng_seed)
        state = 1
    else:
        state = 2
        plan = excercises[excercises['Difficulty'] == 'Hard'].sample(random_state=args.prng_seed)
    '''
    plan = excercises[excercises['Difficulty'] == difficulty_levels[best_cycle[0]]].sample(random_state=args.prng_seed)
    target = muscle_group_dict[plan.iloc[0]['Name']]
    target = target.intersection(all_muscle_groups).pop()
    targets.append(target)

    print(f"Best cycle plan for difficulty lvl {args.difficulty} targeting {all_muscle_groups} is {best_cycle} with lvl {best_cycle_key:1.3f}")
    print("Building plan")
    while len(plan) < args.number:
        # Select the next muscle to target 
        # by cycling through the list of muscles selected by the user
        target = all_muscle_groups[(all_muscle_groups.index(target)+1)%len(all_muscle_groups)]
        target = target.strip()
        # difficult level based on the transition matrix
        # Roll a 100-sided dice to help pick the next level

        dice = random.randrange(0,100,1)
        sum = 0

        #print(f"Old state: {state}")
        # Get the next difficulty level (0-2) using the dice roll 
        # and the computed transition matrix
        '''
        state = difficulty_levels.index(plan.tail(1)['Difficulty'].values[0])
        for i in range(3):
            sum += tm[state,i]
            if dice < sum:
                state = i
                break
        '''
        state = best_cycle[len(plan)%len(best_cycle)]
        #print(f"New state: {state}")
        # Convert the level (0-2) to a string, e.g. 0->"Easy"
        new_difficulty = difficulty_levels[state]
        if args.verbose:
            print(f"Looking for a(n) {new_difficulty} excercise to target {target} - ")        

        # What muscle groups were used in the previous excercise?
        prev_excercise = plan.tail(1)
        prev_muscle_groups = prev_excercise['Muscle Group(s)']
        prev_muscle_groups = set(prev_muscle_groups.values[0].split(','))

        # Before choosing the next excercise, 
        # drop excercises that don't target the next muscle in the list

        # In addition, 
        # count the number of overlapping muscles used in the previous excercise,
        # and temporarily drop any excercises with greater that 33% overlap
        # This prevents working the same muscles back-to-back 

        # Create a temporary (shallow) copy of the excercises dataframe
        temp_ex = excercises.copy()
        for key, value in muscle_group_dict.items():
            # Does this excercise target the next muscle? 
            # If not, drop it temporarily and continue
            try:
                #print(f"{key}:{temp_ex[temp_ex['Name'] == key]['Muscle Group(s)'].values[0]}")
                if target not in temp_ex[temp_ex['Name'] == key]['Muscle Group(s)'].values[0]:
                    drop_msg =  f"Temporarily dropping {key:<60} b/c it doesn't" + \
                                f" target the next primary muscle: {target} " +\
                                f"| ({temp_ex[temp_ex['Name'] == key]['Muscle Group(s)'].values[0]})"
                    if args.verbose:
                        print(drop_msg)

                    temp_ex = temp_ex[temp_ex['Name'] != key]
                    continue
            except IndexError as e:
                print(e)

            if len(all_muscle_groups) > 1:
                # Get the number of overlapping muscles
                overlap = len(prev_muscle_groups.intersection(value))
                # Exclude any excercises that have any overlap 
                # of greater than 1/3 of the muscle groups used
                overlap_percent = round(overlap / len(prev_muscle_groups), 2)*100
                if overlap_percent > 34:
                    temp_ex = temp_ex[temp_ex['Name'] != key]
                    drop_msg =  f"Temporarily dropping {key:<30}" + \
                                f" b/c it uses {overlap}/{len(prev_muscle_groups)}"+ \
                                f" ({overlap_percent:>5}%)" + \
                                " of the same muscles as the previous excercise " + \
                                f"{prev_excercise['Name'].values[0]}"
                    #if args.verbose:
                    #    print(drop_msg)

        # temp_ex now holds excercises that 
        # don't overlap the previous msucles too much
        try:
            next_ex = temp_ex[temp_ex['Difficulty'] == new_difficulty].sample(random_state=args.prng_seed*len(plan))
        except ValueError as e:
            try:
                if state == 0 or state == 2:
                    try:
                        next_ex = temp_ex[temp_ex['Difficulty'] == 'Medium'].sample()
                    except ValueError:
                        print("no mediums found")
                        next_ex = temp_ex.sample()

                elif args.difficulty <= 50:
                    try:
                        next_ex = temp_ex[temp_ex['Difficulty'] == 'Easy'].sample()
                        print("no easy found")

                    except ValueError as e:
                        next_ex = temp_ex.sample()

                else:
                    try:
                        next_ex = temp_ex[temp_ex['Difficulty'] == 'Hard'].sample()
                    except ValueError as e:
                        print("No hard ones found - sampling randomly")
                        next_ex = temp_ex.sample()                
                #next_ex = temp_ex.sample(random_state=args.prng_seed)
                err_msg =   f"Failed to find a {new_difficulty} excercise targeting" + \
                            f" {target} and avoiding previous muscle groups" + \
                            f" ({prev_muscle_groups}); randomly picked " + \
                            f"{next_ex['Name'].item()} with {next_ex['Difficulty'].item()} difficulty instead"    
                #if args.verbose:
                print(err_msg)
            except ValueError as e:
                #if args.verbose:
                print(f"Couldn't target {target} AND give proper muscle rest")
                #print("Skipping it as the primary target")
                continue

        plan = pd.concat([plan, next_ex])
        targets.append(target)

    plan.insert(loc=1, column="Target Muscle", value=targets)
    print(plan)
    return plan 


def build_stretch_plan(args, 
                excercises,  # Can be excercises OR stretches!
                muscle_group_dict,
                all_muscle_groups):

    # Start with a random relevant stretch
    plan = excercises.sample(random_state=args.prng_seed)

    target = muscle_group_dict[plan.iloc[0]['Name']]
    target = target.intersection(all_muscle_groups).pop()
    targets = [target]
    


    # Finally build the workout plan with N excercises total (excluding stretches)
    print("Building plan")
    while len(plan) < len(all_muscle_groups):
        # Select the next muscle to target 
        # by cycling through the list of muscles selected by the user
        target = all_muscle_groups[(all_muscle_groups.index(target)+1)%len(all_muscle_groups)]
        target = target.strip()
        print(f"Finding a stretch to target {target}")

        # What muscle groups were used in the previous excercise?
        prev_excercise = plan.tail(1)
        prev_muscle_groups = prev_excercise['Muscle Group(s)']
        prev_muscle_groups = set(prev_muscle_groups.values[0].split(','))

        # Before choosing the next excercise, 
        # drop excercises that don't target the next muscle in the list

        # In addition, 
        # count the number of overlapping muscles used in the previous excercise,
        # and temporarily drop any excercises with greater that 33% overlap
        # This prevents working the same muscles back-to-back 

        # Create a temporary (shallow) copy of the excercises dataframe
        temp_ex = excercises.copy()
        for key, value in muscle_group_dict.items():
            # Does this excercise target the next muscle? 
            # If not, drop it temporarily and continue
            try:
                #print(f"{key}:{temp_ex[temp_ex['Name'] == key]['Muscle Group(s)'].values[0]}")
                if target not in temp_ex[temp_ex['Name'] == key]['Muscle Group(s)'].values[0]:
                    drop_msg =  f"Temporarily dropping {key:<60} b/c it doesn't" + \
                                f" target the next primary muscle: {target} " +\
                                f"| ({temp_ex[temp_ex['Name'] == key]['Muscle Group(s)'].values[0]})"
                    if args.verbose:
                        print(drop_msg)

                    temp_ex = temp_ex[temp_ex['Name'] != key]
                    continue
            except IndexError as e:
                print(e)



        # temp_ex now holds excercises that target the muscle in the cycle
        try:
            next_ex = None
            next_ex = temp_ex.sample(random_state=args.prng_seed)
        except ValueError as e:
            # Can't find a stretch for this muscle.  Remove it from list.
            print(f"Can't find any stretches for {target}, removing it from {all_muscle_groups}")
            del_target = target
            target = all_muscle_groups[(all_muscle_groups.index(target)-1)%len(all_muscle_groups)]
            all_muscle_groups.remove(del_target)
            continue

        if any(next_ex):
            plan = pd.concat([plan, next_ex])
            targets.append(target)

        else:
            print("Skipping adding a stretch")

    plan.insert(loc=1, column="Target Muscle", value=targets)
    print(plan)
    print(f"Should strech all of {all_muscle_groups}")
    print(f"# of stretches: {len(plan)} Total muscles to stretch: {len(all_muscle_groups)}" )
    return plan 
    
if args.stretch:
    stretch_plan = build_stretch_plan(args, stretches, stretch_muscle_group_dict, copy.deepcopy( all_muscle_groups))

plan = build_plan(args, excercises, ex_muscle_group_dict)

if args.stretch:
    plan = pd.concat([stretch_plan, plan])


outfile =   str('_'.join(all_muscle_groups) + 
            '_difficulty_'+str(args.difficulty) + 
            '_'+args.impact_level+"_impact_level_"+
            '_'.join(args.equipment) +
            '_smooth_surface_'+str(args.smooth_surface)+
            '_stretch_'+str(args.stretch) +  
            '_PRNG_seed_'+str(args.prng_seed))
outfile = outfile.replace(" ", '_')
for i in range(1000):
    if not os.path.isfile(outfile + '_' + str(1) + '.csv'):
        break
if i > 1000:
    print(f"Too many files with the same name.")
    print("Please delete one of the files you have with the prefix: {outfile}")
    sys.exit(1)
outfile = outfile + '_' + str(1) + '.csv'
plan.to_csv(outfile, sep="\t", na_rep="N/A", index=False)
print(f"Success! Wrote results to {outfile}")
