from jira import JIRA
from openpyxl import Workbook
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

email = 'jmokamati@zlti.com'
api_token ='ATATT3xFfGF0VpZjr8heA1B-QHrHoZybxiql17ydlHdo5N291aIy4vfJ7xHJKTZ6Cjs-pFcp4AQnTgzYwxqPKZfY0tNVI2PRSQSzvjMx24nTwtPDXOdLAG4mrxfCZ9tpUU-PxsHvlSBnnwMY91fm6fMjcalSyJBPf94OddNQr2_mVv9586yDmnY=823EDB49'
server = 'https://zlcloud.atlassian.net'                                 # Jira server URL


jira = JIRA(options = {'server': server}, basic_auth = (email, api_token))



headers = ["Issue Key", "Issue Type","Issue Status","Summary","Assignee","Creator","Reporter","Time Spent","Created","Updated","Last Viewed","Resolution Date","Customer Name","Severity","Module Classification","Request Type"]

st.set_page_config(page_title="JIRA Analysis", page_icon=":bar_chart:",layout="wide")
with st.container():
    st.header("Choose Date filter: ")
    col1, col2,col3 = st.columns(3)
    # Add the option for "Current Month"
    current_month_option = col1.checkbox("Current Month", value=True)
    col1.write('Uncheck the Current Month to Select dates')

    # If the user selects "Current Month", calculate the start and end date for the current month
    if current_month_option:
        today = pd.Timestamp.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0).tz_localize('UTC')
        end_date = (today.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + pd.DateOffset(months=1, days=-1)).tz_localize('UTC')
    else:
        # If not using "Current Month", allow the user to choose start and end dates
        today = pd.Timestamp.today()
        stt = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0).tz_localize('UTC')
        start_date = pd.to_datetime(col2.date_input("Start Date",stt)).tz_localize('UTC')
        end_date = pd.to_datetime(col3.date_input("End Date")).tz_localize('UTC')

st.title(" :bar_chart: JIRA Analysis")
st.markdown('<style>div.block-container{padding-top:1.5rem;}</style>',unsafe_allow_html=True)

projects = jira.projects()
summ = []

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

            #iss_works = ""
            # x = jira.worklogs(issue.key)
            # for i in range(len(x)):
            #     work = f"Author: {x[i].author.displayName}, Created: {x[i].created}, Time Spent: {x[i].timeSpent}, Comment: {x[i].comment if hasattr(x[i], 'comment') else 'No comment'}"
            #     iss_works = iss_works  + work+ ";"

 

 

            issue_data = [issue.key,iss_type,iss_status,iss_summ,iss_assign,iss_create,iss_repo,iss_time,iss_crtd,iss_uptd,iss_lst,iss_res,iss_cust,iss_sevt,iss_modclass,iss_reqt]

            #issue_data.append(iss_works if iss_works else '')

            summ.append(issue_data)


df = pd.DataFrame(summ,columns=headers)
print(df.head())

df['Created'] = pd.to_datetime(df['Created'])

filtered_df = df[(df["Created"] >= start_date) & (df["Created"] <= end_date)]


col1, col2,col3 = st.columns(3)

#col1.write("Filtered Data")

#col1.write(filtered_df)

 

# Rest of your code for visualization

# assignee_counts = filtered_df['Assignee'].value_counts()

# fig_assignee_counts = px.pie(names=assignee_counts.index + ' (' + assignee_counts.astype(str) + ')',

#                           values=assignee_counts.values, title='Assignee Counts')

# col2.plotly_chart(fig_assignee_counts)
# Map 'Closed' and 'Open' statuses


# Count of each request type
created_count = filtered_df['Request Type'].value_counts()

# Count of closed issue statuses for each request type
closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']['Request Type'].value_counts()

result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count}).fillna(0)
result_df['Total'] = result_df['Created'] + result_df['Closed']
result_df = result_df.sort_values(by='Total', ascending=False)

col1.write('Request Type')
fig, ax = plt.subplots(figsize=(10, 6))
result_df[['Created', 'Closed']].plot(kind='bar', ax=ax)
ax.set_xlabel('Request Type')
ax.set_ylabel('Count')
ax.set_title('Issue Status Distribution by Request Type')
ax.set_xticklabels(result_df.index, rotation=45, ha='right')
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
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
fig, ax = plt.subplots(figsize=(10, 6))
result_df[['Created', 'Closed']].plot(kind='bar', ax=ax)
ax.set_xlabel('Modules')
ax.set_ylabel('Count')
ax.set_title('Issue Status Distribution by Module Classification')
ax.set_xticklabels(result_df.index, rotation=45, ha='right')
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                textcoords='offset points')
col2.pyplot(fig)

####################################Client################################
created_count = filtered_df["Customer Name"].value_counts()

# Count of closed issue statuses for each request type
closed_count = filtered_df[filtered_df['Issue Status'] == 'Closed']["Customer Name"].value_counts()

# Combine the counts into a DataFrame
result_df = pd.DataFrame({'Created': created_count, 'Closed': closed_count}).fillna(0)
result_df['Total'] = result_df['Created'] + result_df['Closed']
result_df = result_df.sort_values(by='Total', ascending=False)
col3.write('Clients:')
fig, ax = plt.subplots(figsize=(10, 6))
result_df[['Created', 'Closed']].plot(kind='bar', ax=ax)
ax.set_xlabel('Client')
ax.set_ylabel('Count')
ax.set_title('Issue Status Distribution by Clients')
ax.set_xticklabels(result_df.index, rotation=45, ha='right')
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                textcoords='offset points')
col3.pyplot(fig)


# filtered_df['Month'] = filtered_df['Created'].dt.to_period('M')
# closed_df = filtered_df[filtered_df['Issue Status'] == 'Closed']
# # Filter data for "Closed" issue status

# # Streamlit app
# col2.title('Closed Issue Status Trend')