import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Function to load and preprocess data for the selected day(s)
def load_data(day):
    try:
        if day == "All Days":
            dfs = []
            for file in os.listdir():
                if file.startswith("placement_results_day_") and file.endswith(".csv"):
                    df = pd.read_csv(file)
                    df['Day'] = file.split('_')[-1].replace('.csv', '').title()
                    dfs.append(df)
            if dfs:
                df = pd.concat(dfs, ignore_index=True)
            else:
                st.warning("DATA NOT AVAILABLE FOR ALL DAYS")
                return None
        else:
            filename = f'placement_results_{day.lower().replace(" ", "_")}.csv'
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                df['Day'] = day
            else:
                st.warning(f"DATA NOT AVAILABLE FOR {day.upper()}")
                return None
        
        df = df.apply(lambda col: col.str.upper() if col.dtype == 'object' else col)
        df['Department'] = df['Roll No.'].str[2:4]
        df['Special_Dep'] = df['Roll No.'].str.slice(5, 7).apply(lambda x: x if pd.notnull(x) and x.isalpha() else None)
        df['Department'] = df.apply(lambda row: row['Special_Dep'] if pd.notnull(row['Special_Dep']) else row['Department'], axis=1)
        df.drop(columns=['Special_Dep'], inplace=True)
        df['Course'] = df['Roll No.'].apply(lambda x: 'B.Tech' if x[4] == '1' 
                                             else 'Dual' if x[4] == '3' 
                                             else 'Others')
        return df
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Load data
st.title("Student Analysis Dashboard")
selected_day = st.sidebar.selectbox("Select Day", ["Day 1", "Day 2", "Day 3", "All Days"])
df = load_data(selected_day)

if df is not None:
    # Option to group by company's first name
    group_by_company_first_name = st.sidebar.checkbox("Group by First Name of Company")

    if group_by_company_first_name:
        df['Company'] = df['Company'].str.split().str[0]  # Keep only the first word

    grouped = df.groupby(['Department', 'Course', 'Company']).agg({
        'Name': list
    }).reset_index()

    # Sidebar Filters
    st.sidebar.header("Filters")

    # Add "Select All" option for departments, courses, and companies
    all_departments = ['Select All'] + list(grouped['Department'].unique())
    all_courses = ['Select All'] + list(grouped['Course'].unique())
    all_companies = ['Select All'] + list(grouped['Company'].unique())

    departments = st.sidebar.multiselect(
        "Select Department(s)", 
        options=all_departments,
        default='Select All'
    )

    courses = st.sidebar.multiselect(
        "Select Course(s)", 
        options=all_courses,
        default='Select All'
    )

    companies = st.sidebar.multiselect(
        "Select Company(s)", 
        options=all_companies,
        default='Select All'
    )

    # Filtering logic
    if 'Select All' in departments:
        departments = list(grouped['Department'].unique())
    if 'Select All' in courses:
        courses = list(grouped['Course'].unique())
    if 'Select All' in companies:
        companies = list(grouped['Company'].unique())

    filtered_data = grouped[
        (grouped['Department'].isin(departments)) & 
        (grouped['Course'].isin(courses)) &
        (grouped['Company'].isin(companies))
    ]

    # Expand grouped data for detailed view
    def expand_grouped_data(grouped_data):
        expanded_rows = []
        for _, row in grouped_data.iterrows():
            dept = row['Department']
            course = row['Course']
            company = row['Company']
            names = row['Name']
            
            for name in names:
                expanded_rows.append({'Department': dept, 'Course': course, 'Company': company, 'Name': name})
        
        return pd.DataFrame(expanded_rows)

    expanded_data = expand_grouped_data(filtered_data)

    st.subheader("Filtered Data")
    st.dataframe(expanded_data)

    # Visualization
    st.subheader("Number of Students by Department, Course, and Company")
    student_counts = df.groupby(['Department', 'Course', 'Company']).size().reset_index(name='Count')

    visual_data = student_counts[
        (student_counts['Department'].isin(departments)) & 
        (student_counts['Course'].isin(courses)) &
        (student_counts['Company'].isin(companies))
    ]

    if visual_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        fig = px.bar(
            visual_data, 
            x='Department', 
            y='Count', 
            color='Company', 
            barmode='group',
            title=f"Students Distribution by Department, Course, and Company ({selected_day})"
        )
        st.plotly_chart(fig)
else:
    st.warning("No data available.")
