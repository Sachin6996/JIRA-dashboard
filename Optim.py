from jira import JIRA
from openpyxl import Workbook
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
from datetime import timedelta
import re
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Client Services Dashboard", page_icon=":bar_chart:",layout="wide")

st.markdown('''
    <style>
        body {
            background-color: white;
            color: white; /* Set text color to white for better visibility */
        }
        .stApp {
            background-color: RGB(153, 200, 255); /* Set Streamlit app background to black */
        }
    </style>
''', unsafe_allow_html=True)

# st.markdown('''
#     <div style="display: flex; align-items: center; justify-content: center;">
#         <h1 style="font-size: 40px; display: inline-block; height: 30px; margin-top: -72px;">
#            JIRA ANALYSIS
#         </h1>
#     </div>
# ''', unsafe_allow_html=True)
st.markdown('''
    <div style="display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #3498db, #e74c3c); padding: 0; border-radius: 10px; margin: -1.5cm 10px 10px 10px; border: 2px solid #3498db;">
        <h1 style="font-size: 35px; margin: 0; color: #ffffff; padding: 5px;">
           Client Services Dashboard
        </h1>
    </div>
''', unsafe_allow_html=True)


with st.container():
    col1, col2,col3,col4,col5 = st.columns(5)
    # Add the option for "Current Month"
    # current_month_option = col1.checkbox("Current Month", value=True)
    # col1.write('Uncheck the Current Month to Select dates')
    date_option = col4.selectbox("Select Date Option", ["Current Month", "Start and End Dates"])
    Project_option=col1.selectbox("Select Your Project Type", ["CSS", "CITI"])
    # If the user selects "Current Month", calculate the start and end date for the current month
    if date_option == "Current Month":
        today = pd.Timestamp.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0).tz_localize('UTC')
        end_date = (today.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + pd.DateOffset(months=1, days=-1)).tz_localize('UTC')
    else:
        # If not using "Current Month", allow the user to choose start and end dates
        today = pd.Timestamp.today()
        stt = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0).tz_localize('UTC')
        cl1,cl2 = col5.columns(2)
        start_date = pd.to_datetime(cl1.date_input("Start Date",stt)).tz_localize('UTC')
        end_date = pd.to_datetime(cl2.date_input("End Date")).tz_localize('UTC')



if Project_option=='CSS':
    summ = []
    email = 'jmokamati@zlti.com'
    api_token ='ATATT3xFfGF0VpZjr8heA1B-QHrHoZybxiql17ydlHdo5N291aIy4vfJ7xHJKTZ6Cjs-pFcp4AQnTgzYwxqPKZfY0tNVI2PRSQSzvjMx24nTwtPDXOdLAG4mrxfCZ9tpUU-PxsHvlSBnnwMY91fm6fMjcalSyJBPf94OddNQr2_mVv9586yDmnY=823EDB49'
    server = 'https://zlcloud.atlassian.net'                                 # Jira server URL


    jira = JIRA(options = {'server': server}, basic_auth = (email, api_token))

    projects = jira.projects()

    headers = ["Issue Key", "Issue Type","Issue Status","Summary","Assignee","Creator","Reporter","Time Spent","Created","Updated","Last Viewed","Resolution Date","Customer Name","Severity","Module Classification","Request Type"]
    for project in projects:
        if project.key == 'CSS':
            issues_in_proj = jira.search_issues(f'project =CSS and createdDate>="{start_date.strftime("%Y-%m-%d %H:%M")}" order by created DESC', maxResults = 0)
            for issue in issues_in_proj:
                iss_summ = issue.fields.summary
                iss_status = issue.fields.status.name
                iss_type = issue.fields.issuetype.name

                if issue.fields.assignee==None:
                    iss_assign = 'Not assigned'
                else:
                    iss_assign = issue.fields.assignee.displayName

                if issue.fields.creator==None:
                    iss_create = 'Not created'
                else:
                    iss_create = issue.fields.creator.displayName

                if issue.fields.reporter==None:
                    iss_repo = 'Not reported'
                else:
                    iss_repo = issue.fields.reporter.displayName

                if issue.fields.timespent==None:
                    iss_time = 0
                else:
                    iss_time = issue.fields.timespent/60

                iss_crtd = issue.fields.created
                iss_uptd = issue.fields.updated
                iss_lst = issue.fields.lastViewed

                #work = jira.worklogs(issue.key)

                iss_res = issue.fields.resolutiondate
                iss_cus = issue.fields.customfield_10034
                if iss_cus!=None:
                    if len(iss_cus)>1:
                        iss_cust = iss_cus[1].value
                    else:
                        iss_cust = iss_cus[0].value

                iss_sev = issue.fields.customfield_10190
                if iss_sev!=None:
                    iss_sevt = iss_sev.value

                iss_mod = issue.fields.customfield_10212
                if iss_mod!=None:
                    iss_modclass = iss_mod.value

                iss_req = issue.fields.customfield_10010
                if iss_req!=None:
                    try:
                        iss_reqt = issue.fields.customfield_10010.requestType.name
                    except:
                        iss_reqt = None

                issue_data = [issue.key,iss_type,iss_status,iss_summ,iss_assign,iss_create,iss_repo,iss_time,iss_crtd,iss_uptd,iss_lst,iss_res,iss_cust,iss_sevt,iss_modclass,iss_reqt]

                #issue_data.append(iss_works if iss_works else '')

                summ.append(issue_data)


    df = pd.DataFrame(summ,columns=headers)

    df['Created'] = pd.to_datetime(df['Created'])

    df['Updated'] = pd.to_datetime(df['Updated'])
    filtered_df = df[(df["Created"] >= start_date) & (df["Created"] <= end_date)]


    col1, col2,col3,col4 = st.columns(4)




    # Count of each request type
    created_count = filtered_df['Request Type'].value_counts()

    # Count of closed issue statuses for each request type
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']['Request Type'].value_counts()

    result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count}).fillna(0)
    result_df['Total'] = result_df['Created'] + result_df['Closed']
    result_df = result_df.sort_values(by='Total', ascending=False)

    col1.write('Request Type')
    fig, ax = plt.subplots(figsize=(10, 8))
    result_df[['Created', 'Closed']].plot(kind='bar', ax=ax)
    ax.set_xlabel('Request Type',fontsize=14)
    ax.set_ylabel('Count',fontsize=14)
    ax.set_title('Issue Status Distribution by Request Type',fontsize=16)
    ax.set_xticklabels(result_df.index, rotation=40, ha='right',fontsize=12)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    col1.pyplot(fig)

    #############################################Module###############
    created_count = filtered_df["Module Classification"].value_counts()

    # Count of closed issue statuses for each request type
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']["Module Classification"].value_counts()

    # Combine the counts into a DataFrame
    result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count}).fillna(0)
    result_df['Total'] = result_df['Created'] + result_df['Closed']
    result_df = result_df.sort_values(by='Total', ascending=False)
    col2.write('Modules')
    fig, ax = plt.subplots(figsize=(10,8))
    result_df[['Created', 'Closed']].plot(kind='bar', ax=ax)
    ax.set_xlabel('Modules',fontsize=14)
    ax.set_ylabel('Count',fontsize=14)
    ax.set_title('Issue Status Distribution by Module Classification',fontsize=16)
    ax.set_xticklabels(result_df.index, rotation=40, ha='right',fontsize=12)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    col2.pyplot(fig)

    ####################################Client################################

    filtered_df.loc[filtered_df['Customer Name'] == 'National Archives & Records Administration (NARA)', 'Customer Name'] = 'NARA'
    filtered_df.loc[filtered_df['Customer Name'] == 'American Council of Life Insurers (ACLI)', 'Customer Name'] = 'ACLI'
    created_count = filtered_df["Customer Name"].value_counts()

    # Count of closed issue statuses for each request type
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']["Customer Name"].value_counts()

    # Combine the counts into a DataFrame
    result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count}).fillna(0)
    result_df['Total'] = result_df['Created'] + result_df['Closed']
    result_df = result_df.sort_values(by='Total', ascending=False)
    col3.write('Clients')
    fig, ax = plt.subplots(figsize=(10,8))
    result_df[['Created', 'Closed']].plot(kind='bar', ax=ax)
    ax.set_xlabel('Client',fontsize=14)
    ax.set_ylabel('Count',fontsize=14)
    ax.set_title('Issue Status Distribution by Clients',fontsize=16)
    ax.set_xticklabels(result_df.index, rotation=34, ha='right',fontsize=12)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    col3.pyplot(fig)

    #######################Aged cases#############################
    td = today.tz_localize('UTC')
    age_cnt = filtered_df[(td-filtered_df['Created'])>timedelta(days=10)]
    age_cnt = age_cnt[age_cnt['Issue Status']!='Closed']
    aged_cases_df = pd.DataFrame({"Aged Cases    ": age_cnt["Issue Key"]})
    aged_cases_df.reset_index(drop=True, inplace=True)  # Reset index starting from 1
    aged_cases_df.index = aged_cases_df.index + 1
    # Display aged cases with custom index starting from 1
    col1.write('Aged cases(10 days):')
    col1.write(aged_cases_df)

    ################################Not Updated######################

    updt_cnt = filtered_df[(td-filtered_df['Updated'])>timedelta(days=5)]
    updt_cnt = updt_cnt[updt_cnt['Issue Status']!='Closed']
    updt_cases_df = pd.DataFrame({"Not Updt Cases": updt_cnt["Issue Key"]})
    updt_cases_df.reset_index(drop=True, inplace=True)  # Reset index starting from 1
    updt_cases_df.index = updt_cases_df.index + 1
    # Display aged cases with custom index starting from 1
    col2.write('Not Updated:')
    col2.write(updt_cases_df)

    ####################################Pie chart####################
    # Calculate counts for "Closed" and "Open" issues
    col4.write('Close Open Issues')
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed'].shape[0]
    open_count = filtered_df[filtered_df['Issue Status'] != 'Closed'].shape[0]

    # Create a list of labels and values for the pie plot
    labels = [f'Closed ({closed_count})', f'Open ({open_count})']
    values = [closed_count, open_count]

    # Create a pie plot using matplotlib
    fig, ax = plt.subplots(figsize=(10,8))
    ax.pie(values, labels=labels, startangle=90, autopct='%1.1f%%',textprops={'fontsize': 22})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Issue Status Distribution',fontsize=16)

    # Display the pie plot
    col4.pyplot(fig)

    ################Worklogs#######################################
    col3.write("Comments:")
    pattern = re.compile(r'delete|update|move|changeRestart|Rename|Renaming|Configuration|Node deletion|SMTP|DB Queue|Script|Schedule|Zl Integration|ZL API', flags=re.IGNORECASE)
    # Function to check if any target word is present in a comment
    def contains_similar_word(comment):
        return bool(pattern.search(comment))
    summ = []
    headers = ["Issue Key   ", "worklogs", "Matched Word"]
    for project in projects:
        if project.key == 'CSS':
            issues_in_proj = jira.search_issues(f'project =CSS and createdDate>="{start_date.strftime("%Y-%m-%d %H:%M")}" order by created DESC', maxResults = 0)
            for issue in issues_in_proj:
                matched_words = []
                iss_works = ""
                x = jira.worklogs(issue.key)
                for i in range(len(x)):
                    work = f"Comment: {x[i].comment if hasattr(x[i], 'comment') else 'No comment'}"
                    iss_works = iss_works  + work+ ";"
                    matches = pattern.findall(work)
                    matched_words.extend(matches)
                matched_words_str = ", ".join(matched_words)
                issue_data = [issue.key,iss_works,matched_words_str]
                summ.append(issue_data)
        df = pd.DataFrame(summ,columns=headers)

    # Regular expression pattern to match the target substrings
    

    # Apply the function to the 'worklogs' column and filter issue keys
    filtered = df[df['worklogs'].apply(contains_similar_word)][['Issue Key   ','Matched Word']]
    filtered.reset_index(drop=True, inplace=True)
    filtered.index = filtered.index + 1
    col3.write(filtered)

################################ CEAP or CITI ##################################
else:
    
    email = 'jmokamati@ziplip.net' # Jira username
    api_token = 'ATATT3xFfGF0HSwkOy0keuOILBifLvO72_o4ux0MAaMePZIYcVuKxwkCSWoJ83Ty0frs2e3q8pt8IUY8Eq0gpB5x_3G93s2KvKh_dnc0FAy6-Gm_T7ATGCL59WLtf7e5231xhjWKXnahXNgHHCUxfQI4I8LQJJ71QAOFT28JLsEjmy6SxSR9bYE=5D94E8EB' # Jira API token
    server = 'https://zlservicedesk.atlassian.net'    
    jira = JIRA(options = {'server': server}, basic_auth = (email, api_token))# Jira server URL
    projects = jira.projects()
    headers = ["Issue Key", "Issue Type","Issue Status","Summary","Priority","Assignee","Creator","Reporter","Time Spent","Created","Updated","Last Viewed","Resolution Date","Request Type"]
    summ = []
    for project in projects:
        if project.key == 'CEAP':
            issues_in_proj = jira.search_issues(f'project =CEAP and createdDate>="{start_date.strftime("%Y-%m-%d %H:%M")}" order by created DESC', maxResults = 0)
            for issue in issues_in_proj:
                iss_summ = issue.fields.summary
                iss_status = issue.fields.status.name
                iss_type = issue.fields.issuetype.name
                iss_prior = issue.fields.priority.name
                iss_assign = issue.fields.assignee.displayName if issue.fields.assignee else 'Not assigned'
                iss_create = issue.fields.creator.displayName if issue.fields.creator else 'Not created'
                iss_repo = issue.fields.reporter.displayName if issue.fields.reporter else 'Not reported'
                iss_time = issue.fields.timespent / 60 if issue.fields.timespent else 0
                iss_crtd = issue.fields.created if issue.fields.created else 'None'
                iss_uptd = issue.fields.updated if issue.fields.updated else 'None'
                iss_lst = issue.fields.lastViewed if issue.fields.lastViewed else 'None'
                #work = jira.worklogs(issue.key)
                iss_res = issue.fields.resolutiondate if issue.fields.resolutiondate else 'None'
                iss_req = issue.fields.customfield_10012
                if iss_req!=None:
                    try:
                        iss_reqt = issue.fields.customfield_10012.requestType.name
                    except:
                        iss_reqt = None
                issue_data = [issue.key,iss_type,iss_status,iss_summ,iss_prior,iss_assign,iss_create,iss_repo,iss_time,iss_crtd,iss_uptd,iss_lst,iss_res,iss_reqt]
                #issue_data.append(iss_works if iss_works else '')
                summ.append(issue_data)
    df = pd.DataFrame(summ,columns=headers)


    df['Created'] = pd.to_datetime(df['Created'])
    df['Updated'] = pd.to_datetime(df['Updated'])

    filtered_df = df[(df["Created"] >= start_date) & (df["Created"] <= end_date)]


    col1, col2,col3,col4 = st.columns(4)




    # Count of each request type
    created_count = filtered_df['Request Type'].value_counts()

    # Count of closed issue statuses for each request type
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']['Request Type'].value_counts()
    open_count = filtered_df[filtered_df['Issue Status']!= 'Closed']['Request Type'].value_counts()

    result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count,"Opened":open_count}).fillna(0)
    result_df['Total'] = result_df['Created'] + result_df['Closed'] + result_df['Opened']
    result_df = result_df.sort_values(by='Total', ascending=False)

    col1.write('Request Type')
    fig, ax = plt.subplots(figsize=(12, 8))
    result_df[['Created', 'Closed','Opened']].plot(kind='bar', ax=ax)
    ax.set_xlabel('Request Type',fontsize=14)
    ax.set_ylabel('Count',fontsize=14)
    ax.set_title('Issue Status Distribution by Request Type',fontsize=16)
    ax.set_xticklabels(result_df.index, rotation=40, ha='right',fontsize=12)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    col1.pyplot(fig)

    #####################Issue Type##########################################

    # Count of each request type
    created_count = filtered_df['Issue Type'].value_counts()

    # Count of closed issue statuses for each request type
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']['Issue Type'].value_counts()
    open_count = filtered_df[filtered_df['Issue Status']!= 'Closed']['Issue Type'].value_counts()

    result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count,"Opened":open_count}).fillna(0)
    result_df['Total'] = result_df['Created'] + result_df['Closed'] + result_df['Opened']
    result_df = result_df.sort_values(by='Total', ascending=False)

    col2.write('Issue Type')
    fig, ax = plt.subplots(figsize=(12, 8))
    result_df[['Created', 'Closed','Opened']].plot(kind='bar', ax=ax)
    ax.set_xlabel('Issue Type',fontsize=14)
    ax.set_ylabel('Count',fontsize=14)
    ax.set_title('Issue Status Distribution by Issue Type',fontsize=16)
    ax.set_xticklabels(result_df.index, rotation=45, ha='right',fontsize=12)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    col2.pyplot(fig)

    ###################Open Issues###############################################
    open_count = filtered_df[filtered_df['Issue Status']!= 'Closed']['Issue Type'].value_counts()

    result_df = pd.DataFrame({"Opened":open_count}).fillna(0)
    result_df = result_df.sort_values(by='Opened', ascending=False)

    col3.write('Open Issues')
    fig, ax = plt.subplots(figsize=(12, 8))
    result_df['Opened'].plot(kind='bar', ax=ax)
    ax.set_xlabel('Issue Type',fontsize=14)
    ax.set_ylabel('Count',fontsize=14)
    ax.set_title('Open Status Distribution by Issue Type',fontsize=16)
    ax.set_xticklabels(result_df.index, rotation=40, ha='right',fontsize=12)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    col3.pyplot(fig)
    ####################################Pie chart####################
    # Calculate counts for "Closed" and "Open" issues
    col4.write('Close Open Issues')
    closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed'].shape[0]
    open_count = filtered_df[filtered_df['Issue Status'] != 'Closed'].shape[0]

    # Create a list of labels and values for the pie plot
    labels = [f'Closed ({closed_count})', f'Open ({open_count})']
    values = [closed_count, open_count]

    # Create a pie plot using matplotlib
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.pie(values, labels=labels, startangle=90, autopct='%1.1f%%',textprops={'fontsize': 22})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Issue Status Distribution',fontsize=16)

    # Display the pie plot
    col4.pyplot(fig)
    #######################Aged cases#############################
    td = today.tz_localize('UTC')
    age_cnt = filtered_df[(td-filtered_df['Created'])>timedelta(days=10)]
    age_cnt = age_cnt[age_cnt['Issue Status']!='Closed']
    aged_cases_df = pd.DataFrame({"Aged Cases      ": age_cnt["Issue Key"]})
    aged_cases_df.reset_index(drop=True, inplace=True)  # Reset index starting from 1
    aged_cases_df.index = aged_cases_df.index + 1
    # Display aged cases with custom index starting from 1
    col1.write('Aged cases(10 days):')
    col1.write(aged_cases_df)

    ################################Not Updated######################

    updt_cnt = filtered_df[(td-filtered_df['Updated'])>timedelta(days=5)]
    updt_cnt = updt_cnt[updt_cnt['Issue Status']!='Closed']
    updt_cases_df = pd.DataFrame({"Not Updt Cases": updt_cnt["Issue Key"]})
    updt_cases_df.reset_index(drop=True, inplace=True)  # Reset index starting from 1
    updt_cases_df.index = updt_cases_df.index + 1
    # Display aged cases with custom index starting from 1
    col2.write('Not Updated:')
    col2.write(updt_cases_df)
    
    ################Worklogs#######################################
    col3.write("Comments:")
    # Regular expression pattern to match the target substrings
    pattern = re.compile(r'delete|update|move|change', flags=re.IGNORECASE)
    # Function to check if any target word is present in a comment
    def contains_similar_word(comment):
        return bool(pattern.search(comment))
    summ = []
    headers = ["Issue Key    ", "worklogs", "Matched Word"]
    for project in projects:
        if project.key == 'CEAP':
            issues_in_proj = jira.search_issues(f'project =CEAP and createdDate>="{start_date.strftime("%Y-%m-%d %H:%M")}" order by created DESC', maxResults = 0)
            for issue in issues_in_proj:
                matched_words = []
                iss_works = ""
                x = issue.fields.comment.raw['comments']
                for i in range(len(x)):
                    work = x[i]['body']
                    iss_works = iss_works  + work+ ";"
                    matches = pattern.findall(work)
                    matched_words.extend(matches)
                matched_words_str = ", ".join(matched_words)
                issue_data = [issue.key,iss_works,matched_words_str]
                summ.append(issue_data)
        df = pd.DataFrame(summ,columns=headers)


    # Apply the function to the 'worklogs' column and filter issue keys
    filtered = df[df['worklogs'].apply(contains_similar_word)][['Issue Key    ',"Matched Word"]]
    filtered.reset_index(drop=True, inplace=True)
    filtered.index = filtered.index + 1
    col3.write(filtered)

# filtered_df['Month'] = filtered_df['Created'].dt.to_period('M')
# closed_df = filtered_df[filtered_df['Issue Status'] == 'Closed']
# # Filter data for "Closed" issue status

# # Streamlit app
# col2.title('Closed Issue Status Trend')
