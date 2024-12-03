import pandas as pd
import streamlit as st
import plotly.express as px

df = pd.read_csv('placement_results_day_1.csv')
df = df.applymap(lambda x: x.upper())
df['Department'] = df['Roll No.'].str[2:4]
df['Course'] = df['Roll No.'].apply(lambda x: 'B.Tech' if x[4] == '1' 
                                     else 'Dual' if x[4] == '3' 
                                     else 'Others')

grouped = df.groupby(['Department', 'Course']).agg({
    'Name': list,
    'Company': list
}).reset_index()

st.title("Student Analysis Dashboard")
st.sidebar.header("Filters")

departments = st.sidebar.multiselect(
    "Select Department(s)", 
    options=grouped['Department'].unique(),
    default=grouped['Department'].unique()
)

courses = st.sidebar.multiselect(
    "Select Course(s)", 
    options=grouped['Course'].unique(),
    default=grouped['Course'].unique()
)

filtered_data = grouped[
    (grouped['Department'].isin(departments)) &
    (grouped['Course'].isin(courses))
]

st.subheader("Filtered Data")
def expand_grouped_data(grouped_data):
    expanded_rows = []
    for _, row in grouped_data.iterrows():
        dept = row['Department']
        course = row['Course']
        names = row['Name']
        companies = row['Company']
        
        for name, company in zip(names, companies):
            expanded_rows.append({'Department': dept, 'Course': course, 'Name': name, 'Company': company})
    
    return pd.DataFrame(expanded_rows)

expanded_data = expand_grouped_data(filtered_data)

st.subheader("Filtered Data")
st.dataframe(expanded_data)

st.subheader("Number of Students by Department and Course")
student_counts = df.groupby(['Department', 'Course']).size().reset_index(name='Count')

visual_data = student_counts[
    (student_counts['Department'].isin(departments)) &
    (student_counts['Course'].isin(courses))
]

fig = px.bar(
    visual_data, 
    x='Department', 
    y='Count', 
    color='Course', 
    barmode='group',
    title="Students Distribution by Department and Course"
)
st.plotly_chart(fig)

