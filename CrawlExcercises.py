import requests
from bs4 import BeautifulSoup 
from datetime  import datetime 
import re
import pprint as pp
import time
links = set()

footer_text = "Customize your workouts simply by adding or removing Sworkit exercises. Sign in or sign up to get started."

# Download the HTML file https://sworkit.com/exercises and save as "sworkit_excercise_library.html"
with open("sworkit_excercise_library.html", 'r') as home:
    for line_number, line in enumerate(home):
        #print(line_number)
        new_links = re.findall(r'https://sworkit.com/exercise/[^\"]+', line)
        if new_links:
            print(new_links)
            links |= set(new_links)


pp.pprint(links)
headers = {
"Host": "sworkit.com",
"User-Agent": "curl/7.55.1",
"Accept": "*/*"}

results = []
csv_headers = ["Name",
        "Difficulty",
        "Impact",
        "Muscle Group(s)",
        "Instructions",
        "Easier Modification",
        "Harder Modification",
        "Equipment Required",
        "Is Stretch",
        "Smooth Ground Required",
        "Link"]

with open("results4.csv", 'w') as outfile:
    outfile.write("\t".join(csv_headers)+"\n")

    for link_num, link in enumerate(list(links)):
        ex_name = link.split("/")[-1]

        if ex_name.endswith('-left'):
            ex_name += '-and-right'
        elif ex_name.endswith('-right'):
            continue
        print(f"GET {link}; {link_num}/{len(links)}")
        ex_page = requests.get(link, headers=headers)
        #print(ex_page.content)
        #print(ex_page.text)
        diff = re.search(b"<strong>Difficulty: </strong>([A-Za-z]+)", ex_page.content)
        try:
            diff = diff.groups()[0].decode("utf")
        except:
            diff = "N/A"
        impact = re.search(b"<strong>Impact Level: </strong>([A-Za-z]+)", ex_page.content)
        try:
            impact = impact.groups()[0].decode("utf")
        except:
            impact = "N/A"
        muscles = re.search(b"<strong>Target Body Parts: </strong>([A-Za-z, ]+)", ex_page.content)
        try:
            muscles = muscles.groups()[0].decode("utf")
        except:
            muscles = "N/A"


        instructions = re.search(b"<h2>Instructions</h2>", ex_page.content)
        instructions_text = "N/A"
        if instructions:
            instructions_text = re.search(rb"<p>(.*)(?=</p>)",  ex_page.content[instructions.end(0):])
            if instructions_text:
                instructions_text = instructions_text.groups()[0].decode("utf")

        easy_mod = re.search(b"<h2>How to make .{0,100} easier", ex_page.content)
        hard_mod = re.search(b"<h2>How to make .{0,100} more challenging", ex_page.content)
        footer =   re.search(b"Looking to add this exercise to your workouts?", ex_page.content)

        easy_text = ""
        if easy_mod:
            if hard_mod:
                easy_text = re.search(rb"<p>(.*)(?=</p>)",  ex_page.content[easy_mod.end(0):hard_mod.start(0)])
                if not easy_text:
                    easy_text = re.findall(rb"https://sworkit.com/exercise/[^\"]+",  ex_page.content[easy_mod.end(0):hard_mod.start(0)])

                else:
                    print(easy_text)
                    easy_text = easy_text.groups()[0].decode("utf")
                                
            elif footer:
                easy_text = re.search(rb"<p>(.*)(?=</p>)",  ex_page.content[easy_mod.end(0):footer.start(0)])
                if not easy_text:
                    easy_text = re.findall(rb"https://sworkit.com/exercise/[^\"]+",  ex_page.content[easy_mod.end(0):footer.start(0)])                
        print(easy_text)
        if easy_text:
            if isinstance(easy_text, list):
                easy_text = ",".join([x.decode("utf-8").split("/")[-1] for x in easy_text])
            elif isinstance(easy_text, re.Match):
                easy_text = easy_text.groups()[0].decode("utf")
        else:
            easy_text = "N/A"
        

        hard_text = "N/A"
        if hard_mod:
            hard_text = re.search(br"<p>(.*)(?=</p>)", ex_page.content[hard_mod.end(0):footer.start(0)])
            if not hard_text and footer:
                hard_text = re.findall(rb"https://sworkit.com/exercise/[^\"]+",  ex_page.content[hard_mod.end(0):footer.start(0)])                

        if hard_text != "N/A":
            if isinstance(hard_text, list):
                hard_text = ",".join([x.decode("utf-8").split("/")[-1] for x in hard_text])
            else:
                print(hard_text)
                hard_text = hard_text.groups()[0].decode("utf")


        equipment_required = []
        if "dumbbell" in ex_name.lower():
            equipment_required.append("Dumbbell")
        elif "resistance" in ex_name.lower():
            if "band" in ex_name.lower():
                equipment_required.append("Resistance Band")
            elif 'loop' in ex_name.lower():
                equipment_required.append("Resistance Loop") 
        if b"chair" in ex_page.content:
            equipment_required.append("chair")
        if "foam roller" in ex_name.lower():
            equipment_required.append("Foam Roller")
        if "kettlebell" in ex_name.lower():
            equipment_required.append("Kettlebell")
        if "wall" in ex_name.lower():
            equipment_required.append("wall")
        if not equipment_required:
            equipment_required = "N/A"
        else:
            equipment_required = ",".join(equipment_required)

        smooth_ground = False
        if any(substring in instructions_text for substring in ["on a mat", 
                                                                "flat surface",
                                                                "in a kneeling position",
                                                                "sit on the floor",
                                                                "sit down",
                                                                "Sit on the floor",
                                                                "Lay down",
                                                                "lay down",
                                                                "Lie down",
                                                                "lie down",
                                                                "on your back"]):
            smooth_ground = True

        is_stretch = "stretch" in ex_name
        #print(easy_mod)
        #print(hard_mod)
        if easy_text == footer_text:
            easy_text = "N/A"
        if hard_text == footer_text:
            hard_text = "N/A"

        if isinstance(hard_text, re.Match) or isinstance(easy_text, re.Match):
            x = 4
            pass
            
        new_result = [ex_name, 
                        diff, 
                        impact, 
                        muscles, 
                        instructions_text,
                        easy_text, 
                        hard_text, 
                        equipment_required,
                        str(is_stretch),
                        str(smooth_ground),
                        link]
        print(new_result)
        results.append(new_result)
        #time.sleep(.5)


    for result in results:
        try:
            outfile.write("\t".join(result)+'\n')
        except Exception as e:
            print(e)
            print(result)
            pass


