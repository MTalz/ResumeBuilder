# Databricks notebook source
import ipywidgets as widgets
import os
import csv
import pandas as pd
from ipywidgets import HTML
import base64
import shutil

# COMMAND ----------

# Clear Experience History button? 

# COMMAND ----------

# Run the Notebook

# COMMAND ----------

# DBTITLE 1,Enter your Basic Details:
ExpHist_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History' 

# Get a list of all files in Resume Components folder
ExpHist_files = os.listdir(ExpHist_path)  

# Filter out only the files (excluding subfolders)
files = [f for f in ExpHist_files]

# if UserInfo.txt exists use that as the template
if 'UserInfo.csv' in files:
    with open(os.path.join(ExpHist_path, "UserInfo.csv")) as f:
        # Create an empty dictionary
        info_dict = {}
        # Loop through each row in the CSV and add to the dictionary
        for row in csv.reader(f):
            key = row[0]
            value = row[1]
            info_dict[key] = value
        name_default = info_dict['Full Name']
        email_default = info_dict['Email Address']
        phone_default = info_dict['Phone Number']
        linkedin_default = info_dict['LinkedIn']
else:
    name_default = ""
    email_default = ""
    phone_default = ""
    linkedin_default = ""

# Create the text area
name = widgets.Text(
    value=name_default,
    description='Full Name:',
    disabled=False
)
email = widgets.Text(
    value=email_default,
    description='Email Address:',
    disabled=False
)
phone = widgets.Text(
    value=phone_default,
    description='Phone:',
    disabled=False
)
linkedin = widgets.Text(
    value=linkedin_default,
    description='LinkedIn:',
    disabled=False
)

# create the submit button
submit_button = widgets.Button(description='Submit text', button_style='success')
output = widgets.Output()

# create clear button
clear_button = widgets.Button(description='Clear Fields')

def button_click_UserInfo(b):
    """
    on button click save the skills to the UserInfo.csv file.
    """
    output_path = os.path.join(ExpHist_path, "UserInfo.csv")
    with open(output_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Full Name",name.value])
        writer.writerow(["Email Address",email.value])
        writer.writerow(["Phone Number",phone.value])
        writer.writerow(["LinkedIn",linkedin.value])
    with output:
        print("Submitted!")

def button_click_ClearFields(b):
    name.value = ''
    email.value = ''
    phone.value = ''
    linkedin.value = ''

# display the text area and the submit button
display(name,
        email,
        phone,
        linkedin,
        submit_button,
        clear_button,
        output)

# Do the button thing
submit_button.on_click(button_click_UserInfo)
clear_button.on_click(button_click_ClearFields)

# COMMAND ----------

# DBTITLE 1,Enter your Hard Skills:

# if AllSkills.txt read that instead 
if "Skills.txt" in files:
    with open(os.path.join(ExpHist_path, "Skills.txt")) as f:
        skills_template = f.read()
else:
    skills_template = ""

# Create the text area
text_area = widgets.Textarea(
    value=skills_template,
    placeholder='Enter Skills here',
    description='Skills:',
    disabled=False,
    layout=widgets.Layout(width='480px', height='380px')
)

# create the submit button
submit_button = widgets.Button(description='Submit text', button_style='success')
output = widgets.Output()

def button_click_skills(b):
    """
    on button click save the skills to the AllSkills.txt file.
    """
    output_skills_path = os.path.join(ExpHist_path, "AllSkills.txt")
    with open(output_skills_path, "w") as f:
        f.write(text_area.value)
    with output:
        print("Submitted!")

# display the text area and the submit button
display(text_area, submit_button, output)

# Do the button thing
submit_button.on_click(button_click_skills)

# COMMAND ----------

# DBTITLE 1,Enter your Education History:
# Education History
if "AllEducation.txt" in files:
    with open(os.path.join(ExpHist_path, "AllEducation.txt")) as f:
        ed_template = f.read()
else:
    ed_template = ""

# Create the text area
text_area = widgets.Textarea(
    value=ed_template,
    placeholder='Enter Education here',
    description='Education:',
    disabled=False,
    layout=widgets.Layout(width='680px', height='400px')
)

# create the submit button
submit_button = widgets.Button(description='Submit text', button_style='success')
output = widgets.Output()

def button_click_ed(b):
    """
    on button click save the skills to the AllEducation.txt file.
    """
    output_path = os.path.join(ExpHist_path, "AllEducation.txt")
    with open(output_path, "w") as f:
        f.write(text_area.value)
    with output:
        print("Submitted!")

# display the text area and the submit button
display(text_area, submit_button, output)

# Do the button thing
submit_button.on_click(button_click_ed)

# COMMAND ----------

# DBTITLE 1,Enter your Work History: 


# if WorkHistory_Roles.csv exists use that as the template
if 'WorkHistory_Roles.csv' in ExpHist_files:
    df = pd.read_csv(os.path.join(ExpHist_path, "WorkHistory_Roles.csv"), index_col='role_id')
else:
    cols = ["role_id", "role", "company", "location", "period"]
    df = pd.DataFrame(columns=cols)
    df.set_index('role_id', inplace=True)

# Not in use yet
jobs = df['role'] + " - " + df['company'] + ' (' + df['period'] + ')'
job_options = jobs.tolist()

#if WorkHistory_Achievments.csv exist use that
if 'WorkHistory_Achievments.csv' in ExpHist_files:
    achievements_df = pd.read_csv(os.path.join(ExpHist_path, "WorkHistory_Achievments.csv"), index_col=["role_id", "achievement_id"])
else:
    cols = ["role_id", "achievement_id", "achievement"]
    achievements_df = pd.DataFrame(columns=cols)
    achievements_df.set_index(["role_id","achievement_id"], inplace=True)


job_dropdown = widgets.Dropdown(
    # options=job_options,
    options=df.index,
    # value='',
    description='Jobs:',
    disabled=False,
)

# needed to fit the full description
style = {'description_width': 'initial'}

job_input = widgets.Text(
    value = df.at[1, 'role'],
    placeholder = 'Enter Job Title',
    description = 'Job Title:',
    style = style,
    disabled = False
)

Company_input = widgets.Text(
    value = df.at[1, 'company'],
    placeholder = 'Enter Company',
    description = 'Company Name: ',
    style=style,
    disabled=False
)

Location_input = widgets.Text(
    value = df.at[1, 'location'],
    placeholder = 'Enter Location',
    description = 'Location:',
    style = style,
    disabled = False
)

Period_input = widgets.Text(
    value = df.at[1, 'period'],
    placeholder = 'Enter period',
    description = 'Period:',
    style = style,
    disabled = False
)

# start_date = widgets.DatePicker(
#     placeholder='Enter Start Date',
#     description='Start Date:',
#     disabled=False
# )

# end_date = widgets.DatePicker(
#     placeholder='Enter Finish Date',
#     description='End Date:',
#     disabled=False
# )

# present = widgets.Checkbox(
#     value=False,
#     description='I still work here',
#     disabled=False
# )

# Create the text area
Achievements_area = widgets.Textarea(
    value='\n'.join(achievements_df.loc[1, 'achievement']),
    placeholder='Enter Achievements here',
    description='Achievements:',
    style=style,
    disabled=False,
    layout=widgets.Layout(width='680px', height='200px')
)

# Create Submit Button
submit_button = widgets.Button(
    description='Submit Changes',
    disabled=True,
    button_style='success'
)

# Function to enable the Submit button when changes are made
def enable_submit(change):
    submit_button.disabled = False

job_input.observe(enable_submit, names='value')
Company_input.observe(enable_submit, names='value')
Location_input.observe(enable_submit, names='value')
Period_input.observe(enable_submit, names='value')
Achievements_area.observe(enable_submit, names='value')


# Function to update Text widgets based on Dropdown selection
def update_values(change):
    selected_roleID = job_dropdown.value

    job_input.value = df.at[selected_roleID, 'role']
    Company_input.value = df.at[selected_roleID,'company']
    Location_input.value = df.at[selected_roleID,'location']
    Period_input.value = df.at[selected_roleID,'period']

    selected_achievements = achievements_df.loc[selected_roleID, 'achievement'].tolist()
    Achievements_area.value = '\n'.join(selected_achievements)

    # Disable the Submit button after changes are saved
    submit_button.disabled = True


# Link Dropdown's value change to the update function
job_dropdown.observe(update_values, names='value')

# Function to update DataFrame when the Submit button is clicked
def update_df(button_click):
    selected_roleID = job_dropdown.value
    
    df.at[selected_roleID, 'role'] = job_input.value
    df.at[selected_roleID, 'company'] = Company_input.value
    df.at[selected_roleID, 'location'] = Location_input.value
    df.at[selected_roleID, 'period'] = Period_input.value

    df.to_csv(os.path.join(ExpHist_path, "WorkHistory_Roles.csv"))

    new_achievements = Achievements_area.value.split('\n')
    
    # Update the descriptions for the selected roleID
    existing_rows = achievements_df.loc[selected_roleID].index.tolist()
    for i, achievement in enumerate(new_achievements):
        if i < len(existing_rows):
            achievements_df.at[(selected_roleID, existing_rows[i]), 'achievement'] = achievement
        else:
            achievements_df.loc[(selected_roleID, i + 1), 'achievement'] = achievement

    # save to the WorkHistory_Achievments.csv
    achievements_df.to_csv(os.path.join(ExpHist_path, "WorkHistory_Achievments.csv"))
    
    # Disable the Submit button after changes are saved
    submit_button.disabled = True

# Link the Submit button's click event to the update_df function
submit_button.on_click(update_df)

# Create a button to add a new role
add_button = widgets.Button(
    description='Add New Role',
    button_style='info'
)

# Function to add a new role to the DataFrame
def add_role(button_click):
    new_roleID = df.index.max() + 1
    new_row_df = { 
        'role': '', 
        'company': '',
        'location': '',
        'period' : ''
        }

    df.loc[new_roleID] = new_row_df

    achievements_df.loc[(new_roleID, 1), 'achievement'] = ""  

    job_dropdown.options = df.index
    job_dropdown.value = new_roleID  # Automatically select the newly added role

# Link the Add button's click event to the add_role function
add_button.on_click(add_role)

# Create a button to delete a role
delete_button = widgets.Button(
    description='Delete Selected Role',
    button_style='danger'
)

# Function to delete the selected role from the DataFrame
def delete_role(button_click):
    selected_roleID = job_dropdown.value
    df.drop(selected_roleID, inplace=True)

    # save the updated df to WorkHistory_Roles.csv
    df.to_csv(os.path.join(ExpHist_path, "WorkHistory_Roles.csv"))

    # update achievements_df
    achievements_df.drop(index=selected_roleID, level='role_id', inplace=True)

    # save the updated achievements_df to the WorkHistory_Achievments.csv
    achievements_df.to_csv(os.path.join(ExpHist_path, "WorkHistory_Achievments.csv"))

    job_dropdown.options = df.index.tolist()
    job_dropdown.value = min(df.index)

# Link the Delete button's click event to the delete_role function
delete_button.on_click(delete_role)    

# display the text area and the submit button
display(
    job_dropdown,
    job_input, 
    Company_input,
    Location_input,
    Achievements_area,
    Period_input,
    # start_date,
    # end_date,
    # present,
    submit_button,
    add_button,
    delete_button
    # output
    )

# COMMAND ----------

# DBTITLE 1,Paste Job Ad Below:

# Output path for job ad
jobAd_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Job Ads/New Ad/jobAd.txt'

# Create the text area
job_ad_text = widgets.Textarea(
    value="",
    placeholder='Paste Job Ad here',
    description='Job Ad:',
    disabled=False,
    layout=widgets.Layout(width='980px', height='1000px')
)

# Create Submit Button
submit_ad = widgets.Button(
    description='Submit Job Ad',
    disabled=False,
    button_style='success'
)

# Function to enable the Submit button when changes are made
def enable_submit(change):
    submit_ad.disabled = False

# When you add something to the text area enable the button
job_ad_text.observe(enable_submit, names='value')

# Function to update Text widgets based on Dropdown selection
def upload_ad(change):

    # writes the job ad to jobAd_path
    with open(jobAd_path, "w") as f:
        f.write(job_ad_text.value)

    # clears the text area
    job_ad_text.value = ""

    # Disable the Submit button after changes are saved
    submit_ad.disabled = True

# on click upload the ad
submit_ad.on_click(upload_ad)

# display the two elements
display(
    job_ad_text,
    submit_ad
)


# COMMAND ----------

# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Orchestration/Orchestration"

# COMMAND ----------

# DBTITLE 1,The resume and cover letter should appear in the output folder after running the Orchestration Notebook

output_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Output'


# COMMAND ----------

# DBTITLE 1,Download your Resume!
# We couldn't get the download button to work unfortunately

source_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Job Ads/New Ad'  # Replace with the actual source file path
destination_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Job Ads/Processed Ad'  # Replace with the actual destination folder path
output_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Output'
# job ads in job ads folder
job_ads_list = os.listdir(source_path)

# move the ad to the processed folder and stick a date on the end of it
for ad in job_ads_list:
    shutil.move(os.path.join(source_path, ad), destination_path)

# get the folder of processed ads
job_output_dir = [d for d in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, d))]

# file in the first folder
res = 'computed results'

#FILEs
resume_path = str(os.path.join(output_path, job_output_dir[0], 'Resume.docx'))
cover_letter_path = str(os.path.join(output_path, job_output_dir[0],'Cover_Letter.docx'))

b64 = base64.b64encode(res.encode())
payload = b64.decode()

#BUTTONS
html_button_1 = '''<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<a download="{filename}" href="data:text/csv;base64,{payload}" download>
<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-warning">Download Resume</button>
</a>
</body>
</html>
'''

#BUTTONS
html_button_2 = '''<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<a download="{filename}" href="data:text/csv;base64,{payload}" download>
<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-warning">Download Cover Letter</button>
</a>
</body>
</html>
'''

html_button_resume = html_button_1.format(payload=payload, filename=resume_path)
html_button_cl = html_button_2.format(payload=payload, filename=cover_letter_path)

display(HTML(html_button_resume))
display(HTML(html_button_cl))