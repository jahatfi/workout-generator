# workout-generator
Builds a database of excercises by crawling sworkit.com.  

'''bash
usage: BuildWorkout.py [-h] -t TARGET_REGIONS [-e EQUIPMENT] [-n NUMBER] [-i IMPACT_LEVEL] [-s STRETCH] [-p PRNG_SEED] [-v VERBOSE]
                       database difficulty smooth_surface

Build workout plan from database of excercises.                                                                                                                    ace

positional arguments:
  database              .csv database of excercises with these headers:
                        ['Name',                                                                                                                                   ace
                         'Target Muscle',
                         'Instructions',
                         'Difficulty',
                         'Impact',
                         'Muscle Group(s)',
                         'Easier Modification',
                         'Harder Modification',
                         'Equipment Required',
                         'Is Stretch',
                         'Smooth Ground Required',
                         'Link']
  difficulty            Pick a difficulty between 0-100 inclusive
  smooth_surface        True if a smooth surface (e.g. concrete pad, gym floor)
                        is available, else False (e.g. grass, asphalt)

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET_REGIONS, --target_regions TARGET_REGIONS
                        Pick at least one of the following
                        (Can choose whole regions or specific muscles):
                        ['abs',
                         'chest',
                         'hip flexor',
                         'shoulders',
                         {'arms': ['biceps', 'triceps']},
                         {'core': ['abs', 'upper back', 'lower back']},
                         {'legs': ['calves', 'glutes', 'hamstrings', 'quadriceps']},
                         {'upper body': ['arms', 'chest', 'shoulders']}])
  -e EQUIPMENT, --equipment EQUIPMENT
                        List all of equipment available from the list below:
                        ['chair',
                         'dumbbell',
                         'foam roller',
                         'kettlebell',
                         'resistance band',
                         'resistance loop',
                         'wall']
  -n NUMBER, --number NUMBER
                        The Number of excercises to include (Default: 3* # targets)
  -i IMPACT_LEVEL, --impact-level IMPACT_LEVEL
                        The maximum impact level(e.g. "Low", "Normal", "High" (Default)) (Default: "High")
  -s STRETCH, --stretch STRETCH
                        Include warm up and cool down stretches? (True/False)(Default: True)
  -p PRNG_SEED, --prng-seed PRNG_SEED
                        PRNG seed to ensure reproducibility
  -v VERBOSE, --verbose VERBOSE
                        False by default, but set to True for detailed debugging

python BuildWorkout.py -t arms -t core -e dumbbell -s True results.csv 50 True
Parsing targeted muscle groups
Reading provided database
Dropping irrelevant excercises - this could take a minute
Separating stretches and excercises
Building plan
Finding a stretch to target upper back
Finding a stretch to target triceps
Can't find any stretches for triceps, removing it from ['upper back', 'triceps', 'lower back', 'biceps', 'abs']
Finding a stretch to target lower back
Finding a stretch to target biceps
                         Name Target Muscle Difficulty  Impact          Muscle Group(s)  ...                                Harder Modification Equipment Required Is Stretch Smooth Ground Required                                               Link
368        single-leg-stretch           abs       Easy  Normal  abs, glutes, quadriceps  ...                                                NaN                NaN       True                   True    https://sworkit.com/exercise/single-leg-stretch
9    arm-and-shoulder-stretch    upper back       Easy     Low    upper back, shoulders  ...                                                NaN                NaN       True                  False  https://sworkit.com/exercise/arm-and-shoulder-...
22   bending-windmill-stretch    lower back       Easy  Normal   lower back, hamstrings  ...                                                NaN                NaN       True                  False  https://sworkit.com/exercise/bending-windmill-...
25   biceps-and-wrist-stretch        biceps       Easy     Low                   biceps  ...  Try our 2 hand wrist extension for a bigger st...                NaN       True                  False  https://sworkit.com/exercise/biceps-and-wrist-...

[4 rows x 12 columns]
Should strech all of ['upper back', 'lower back', 'biceps', 'abs']
# of stretches: 4 Total muscles to stretch: 4
Finding best difficulty cycle
Best cycle plan for difficulty lvl 50 targeting ['upper back', 'triceps', 'lower back', 'biceps', 'abs'] is [0, 1, 2, 1] with lvl 0.500
Building plan
                                          Name Target Muscle Difficulty  Impact  ... Equipment Required Is Stretch Smooth Ground Required                                               Link
218                              knee-to-chest           abs       Easy     Low  ...                NaN      False                  False         https://sworkit.com/exercise/knee-to-chest
373                                    skaters    upper back     Medium    High  ...                NaN      False                  False               https://sworkit.com/exercise/skaters
85      dumbbell-high-plank-row-left-and-right       triceps       Hard  Normal  ...           Dumbbell      False                  False  https://sworkit.com/exercise/dumbbell-high-pla...
92                           dumbbell-reach-up    lower back     Medium  Normal  ...           Dumbbell      False                   True     https://sworkit.com/exercise/dumbbell-reach-up
17                                back-scratch        biceps       Easy     Low  ...                NaN      False                   True          https://sworkit.com/exercise/back-scratch
272                        plank-jump-to-squat           abs     Medium    High  ...                NaN      False                  False   https://sworkit.com/exercise/plank-jump-to-squat
8                               archer-push-up    upper back       Hard  Normal  ...                NaN      False                  False        https://sworkit.com/exercise/archer-push-up
86                     dumbbell-overhead-press       triceps     Medium  Normal  ...           Dumbbell      False                  False  https://sworkit.com/exercise/dumbbell-overhead...
132                               forward-fold    lower back       Easy     Low  ...                NaN      False                  False          https://sworkit.com/exercise/forward-fold
362  single-arm-dumbbell-snatch-left-and-right        biceps     Medium  Normal  ...           Dumbbell      False                  False  https://sworkit.com/exercise/single-arm-dumbbe...
329              roll-up-hold-arms-up-and-down           abs       Hard     Low  ...                NaN      False                   True  https://sworkit.com/exercise/roll-up-hold-arms...
75                      dumbbell-bent-over-row    upper back     Medium  Normal  ...           Dumbbell      False                  False  https://sworkit.com/exercise/dumbbell-bent-ove...
433                    wide-leg-stance-arms-up       triceps       Easy  Normal  ...                NaN      False                  False  https://sworkit.com/exercise/wide-leg-stance-a...
335                              scissor-kicks    lower back     Medium  Normal  ...                NaN      False                   True         https://sworkit.com/exercise/scissor-kicks
85      dumbbell-high-plank-row-left-and-right        biceps       Hard  Normal  ...           Dumbbell      False                  False  https://sworkit.com/exercise/dumbbell-high-pla...

[15 rows x 12 columns]
Success! Wrote results to upper_back_triceps_lower_back_biceps_abs_difficulty_50_High_impact_level_dumbbell_smooth_surface_True_stretch_True_PRNG_seed_42_1.csv
```                        