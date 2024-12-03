import pandas as pd
import streamlit as st
import plotly.express as px

# Load and preprocess the data
df = pd.read_csv('placement_results_day_1.csv')
df = df.apply(lambda col: col.str.upper() if col.dtype == 'object' else col)

df['Department'] = df['Roll No.'].str[2:4]
df['Special_Dep'] = df['Roll No.'].str.slice(5, 7).apply(lambda x: x if pd.notnull(x) and x.isalpha() else None)
df['Department'] = df.apply(lambda row: row['Special_Dep'] if pd.notnull(row['Special_Dep']) else row['Department'], axis=1)
df.drop(columns=['Special_Dep'], inplace=True)
df['Course'] = df['Roll No.'].apply(lambda x: 'B.Tech' if x[4] == '1' 
                                     else 'Dual' if x[4] == '3' 
                                     else 'Others')

grouped = df.groupby(['Department', 'Course']).agg({
    'Name': list,
    'Company': list
}).reset_index()

st.title("Student Analysis Dashboard")
st.sidebar.header("Filters")

# Add "Select All" option
all_departments = ['Select All'] + list(grouped['Department'].unique())
all_courses = ['Select All'] + list(grouped['Course'].unique())

# Sidebar for selecting departments
departments = st.sidebar.multiselect(
    "Select Department(s)", 
    options=all_departments,
    default='Select All'
)

# Sidebar for selecting courses
courses = st.sidebar.multiselect(
    "Select Course(s)", 
    options=all_courses,
    default='Select All'
)

# Apply filtering logic for "Select All"
if 'Select All' in departments:
    departments = list(grouped['Department'].unique())

if 'Select All' in courses:
    courses = list(grouped['Course'].unique())

filtered_data = grouped[
    (grouped['Department'].isin(departments)) & 
    (grouped['Course'].isin(courses))
]

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

if visual_data.empty:
    st.warning("No data available for the selected filters.")
else:
    fig = px.bar(
        visual_data, 
        x='Department', 
        y='Count', 
        color='Course', 
        barmode='group',
        title="Students Distribution by Department and Course"
    )
    st.plotly_chart(fig)
