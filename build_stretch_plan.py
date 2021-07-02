def build_stretch_plan(args, 
                excercises,  # Can be excercises OR stretches!
                muscle_group_dict,
                count):

    # Start with a random relevant stretch
    plan = excercises.sample()

    target = muscle_group_dict[plan.iloc[0]['Name']]
    target = target.intersection(all_muscle_groups).pop()
    targets.append(target)


    # Finally build the workout plan with N excercises total (excluding stretches)
    print("Building plan")
    while len(plan) < count:
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
                    #if args.verbose:
                    #    print(drop_msg)

                    temp_ex = temp_ex[temp_ex['Name'] != key]
                    continue
            except IndexError as e:
                print(e)

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
                            " of the same muscles as the previous stretch " + \
                            f"{prev_excercise['Name'].values[0]}"
                #if args.verbose:
                #    print(drop_msg)

        # temp_ex now holds excercises that target the muscle in the cycle
        next_ex = temp_ex.sample()

        plan = pd.concat([plan, next_ex])
        targets.append(target)

    plan.insert(loc=1, column="Target Muscle", value=targets)
    print(plan)
    return plan 