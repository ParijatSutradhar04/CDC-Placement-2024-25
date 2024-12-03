import pandas as pd
import streamlit as st
import plotly.express as px

# Sample DataFrame
df = pd.read_csv('placement_results_day_1.csv')
df = df.applymap(lambda x: x.upper())
df

# Extract Department and Course
df['Department'] = df['Roll No.'].str[2:4]
df['Course'] = df['Roll No.'].apply(lambda x: 'B.Tech' if x[4] == '1' 
                                     else 'Dual' if x[4] == '3' 
                                     else 'Others')

# Group data
grouped = df.groupby(['Department', 'Course']).agg({
    'Name': list,
    'Company': list
}).reset_index()

# Dashboard layout
st.title("Student Analysis Dashboard")
st.sidebar.header("Filters")

# Sidebar filters
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

# Filter data based on selections
filtered_data = grouped[
    (grouped['Department'].isin(departments)) &
    (grouped['Course'].isin(courses))
]

# Display filtered data
st.subheader("Filtered Data")
# Function to expand grouped data into a flat DataFrame
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

# Expand the filtered data
expanded_data = expand_grouped_data(filtered_data)

# Display expanded data as a normal DataFrame
st.subheader("Filtered Data")
st.dataframe(expanded_data)

# Visualize data
st.subheader("Number of Students by Department and Course")
student_counts = df.groupby(['Department', 'Course']).size().reset_index(name='Count')

# Filter visual data
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

