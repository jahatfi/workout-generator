import argparse
import pprint as pp
from itertools import chain
import pandas as pd
from TransitionMatrix import get_matrix
import numpy as np
import random

difficulty_levels = ['Easy', 'Medium', 'Hard']

tsv_headers = [
        "Name",
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
            "dumbells",
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

all_regions = set()
for region in target_regions_list:
    if isinstance(region, str):
        all_regions.add(region)
    else:
        all_regions |= set(region.keys())
        all_regions |= set(list(region.values())[0])
#print(all_regions)
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
        raise argparse.ArgumentTypeError('Invalid bdy part to target.')
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

parser = argparse.ArgumentParser(
            description='Build workout plan from database of excercises.',
            formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
            'database', 
            type=argparse.FileType('r'),
            help=f"Tab-separated database of excercises with these headers:\n{headers}")                    
parser.add_argument(
            'difficulty', 
            type=difficulty_type, 
            help='Pick a difficulty between 0-100 inclusive')
parser.add_argument(
            'smooth_surface', 
            type=str2bool, 
            help='True if a smooth surface (e.g. concrete pad, gym floor) \n' + 
            'is available, else False (e.g. grass, asphalt)')      
parser.add_argument(
            '-t',                
            '--target_regions', 
            action="append",
            required=True,
            type=valid_region, 
            help='Pick at least one of the following\n' + \
                 f'(Can choose whole regions or specific muscles):\n{target_regions}')                             
parser.add_argument(
            '-e',
            '--equipment',
            type=valid_equipment,
            action='append',
            help=f'List all of equipment available from the list below:\n{equipment}')

parser.add_argument(
            '-n',
            '--number',
            type=int,
            default=12,
            help=f'The Number of excercises to include in the plan (Default: 12)')

parser.add_argument(
            '-i',
            '--impact-level',
            type=str,
            default="High",
            help=f'The maximum impact level (e.g. "Low", "Normal", "High") (Default: "High")')            

parser.add_argument(
            '-s',
            '--stretch',
            type=str2bool,
            default=True,
            help=f'Include warm up and cool down stretches? (True/False) (Default: True)')                

args = parser.parse_args()
print(args)


all_muscle_groups = set()
for group in args.target_regions:
    if group in target_subregions:
        all_muscle_groups |= set(target_subregions[group])
    else:
        all_muscle_groups.add(group)

df = pd.read_csv(args.database, sep='\t')
tm = get_matrix(args.difficulty)
#print(df)
plan = []
drop_indices = []
df = df.dropna(subset=['Muscle Group(s)']) 
for row_index, row in df.iterrows():
    row_tgts = set(row['Muscle Group(s)'].split(","))
    if not row_tgts.intersection(all_muscle_groups):
        drop_indices.append(row_index)
        #print(f"Dropping {row['Name']}; wrong target regions")

    elif not args.smooth_surface and row['Smooth Ground Required']:
        drop_indices.append(row_index)
        #print(f"Dropping {row['Name']} as it requires smooth ground")
    elif isinstance(row['Equipment Required'], str) and not set(row['Equipment Required'].split(',') ).issubset(set(args.equipment)):
        #print(f"Dropping {row['Name']:40} due to missing equipment: {row['Equipment Required']}")
        drop_indices.append(row_index)



df = df.drop(index=drop_indices)
stretches = df[df['Is Stretch']]
excercises = df[~df['Is Stretch']]

if args.difficulty < 33:
    plan = excercises[excercises['Difficulty'] == 'Easy'].sample()
    state = 0
elif args.difficulty < 67:
    plan = excercises[excercises['Difficulty'] == 'Medium'].sample()
    state = 1
else:
    state = 2
    plan = excercises[excercises['Difficulty'] == 'Hard'].sample()

while len(plan) < args.number:
    dice = random.randrange(0,100,1)
    #print(f"Dice: {dice}")
    sum = 0

    #print(f"Old state: {state}")
    # Get the next difficulty level
    for i in range(3):
        sum += tm[state,i]
        if dice < sum:
            state = i
            break

    #print(f"New state: {state}")

    new_difficulty = difficulty_levels[state]

    plan = pd.concat([plan, excercises[excercises['Difficulty'] == new_difficulty].sample()])
print(plan)
    

    





