import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

@st.cache_data
def load_data(uploaded_file):
    '''
    Loads data from a CSV file and preprocess it

    Args:
        uploaded_file (file): The uploaded CSV file

    Returns:
        df: Preprocessed DataFrame
    '''
    df = pd.read_csv(uploaded_file, sep=';')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Testdate'] = pd.to_datetime(df['Testdate'], format='%d/%m/%Y')
    return df

def select_param(key, x, y):
    '''
    Creates selectboxes to choose x-axis and y-axis for chart

    Args:
        key (str): Unique key identifier
        x (int): Index of default x-axis value
        y (int): Index of default y-axis value

    Returns:
        x_axis (str): Selected x-axis
        y_axis (str): Selected y-axis
    '''
    x_axis = st.selectbox(
        'Select x-axis', 
        ['Age Days', 'Age Weeks', 'Testdate', 'Assay'],
        index=x,
        key=key + '_x_axis')

    y_axis = st.selectbox(
        'Select y-axis', 
        ['Mean Titer', 'Min Titer', 'Max Titer', 'GMT', 'Results Count'],
        index=y,
        key=key + '_y_axis')
   
    return x_axis, y_axis

def select_grouping(key, group, color, y_axis):
    '''
    Creates a multiselect and a selectbox to choose grouping and coloring parameters

    Args:
        key (str): Unique key identifier
        group (list): Selected parameter/s for grouping
        color (int): Index of default parameter for chart color
        y_axis (str): Selected y-axis parameter.

    Returns:
        group_by (list): Selected grouping parameter/s
        color_by (str): Selected color parameter
    '''
    options = ['Testdate', 'GMT', 'Assay', 'Result']
    if y_axis == 'Results Count':
        options += ['Result']
    group_by = st.multiselect(
        'Group data by',
        options,
        group,
        key=key + '_group_by')

    color_by = st.selectbox(
        'Color data by',
        ['Assay', 'Result'],
        index=color,
        key=key + '_color_by')

    return group_by, color_by

def date_slider(df, key, x_axis):
    '''
    Creatse a date slider for selecting date range

    Args:
        df (pd.DataFrame): The DataFrame containing the data
        key (str): Unique key identifier
        x_axis (str): Selected x-axis

    Returns:
        selected_min_date (date): Selected minimum date
        selected_max_date (date): Selected maximum date
    '''
    min_date = df['Testdate'].min().date()
    max_date = df['Testdate'].max().date()

    if x_axis == 'Testdate':
        selected_min_date, selected_max_date = st.slider(
            'Select Date Range', 
            min_value=min_date, 
            max_value=max_date, 
            value=(min_date, max_date),
            format="MMM YYYY",
            key=key)
    else:
        selected_min_date = min_date
        selected_max_date = max_date
    
    return selected_min_date, selected_max_date


def create_chart(df, chart, x, y, group_by, color_by, chart_func):
    '''
    Creates and displays pre-defined charts that can be modified

    Args:
        df (pd.DataFrame): The DataFrame containing the data
        chart (str): The selected chart type
        x (int): Index of default x-axis value
        y (int): Index of default y-axis value
        group_by (list): Selected parameter/s for grouping
        color (int): Index of default parameter for chart color
        chart_func (function): Function for chart creation
    '''
    try:
        with st.sidebar.expander(f'{chart} options'):
            show_chart = st.checkbox(f'Show {chart.lower()}', value=True)
            if show_chart:
                x_axis, y_axis = select_param(chart.lower(), x, y)
                group_by, color_by = select_grouping(chart.lower(), group_by, color_by, y_axis)
                selected_min_date, selected_max_date = date_slider(df, chart.lower(), x_axis)

                chart_title = st.text_input('Chart Title', f'{chart}: {y_axis} vs. {x_axis}', key=chart.lower()+'title')
                chart_height = st.slider('Chart Height', min_value=300, max_value=700, value=500, key=chart.lower()+'height')

                df = df[df['Testdate'].dt.date.between(selected_min_date, selected_max_date)]
                if group_by != []:
                    if y_axis == 'Results Count':  
                        df = df.groupby(group_by).size().reset_index(name='Results Count')
                    else:
                        df = df.groupby(group_by).agg({'Age Days': 'mean', 'Age Weeks': 'mean', 'Min Titer': 'mean', 'Max Titer': 'mean', 'Mean Titer': 'mean'}).reset_index()
        if show_chart:
            fig = chart_func(df, x_axis, y_axis, color_by)
            fig.update_layout(title =chart_title, height=chart_height)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
            st.warning("Sorry, an error is encountered. Please check your inputs.")
            return

def custom_chart(df):
    '''
    Creates and displays a custom chart based on user-selected options

    Args:
        df (pd.DataFrame): The DataFrame containing the data
    '''
    try:
        all_columns = df.columns.tolist()
        with st.sidebar.expander('Custom chart'):
            show_chart = st.checkbox('Add custom chart')
            if show_chart:
                chart = st.selectbox("Select Chart Type", ["Line Chart", "Scatter Plot", "Bar Chart", "Box Plot", "Violin Plot"])
                x_axis = st.selectbox('Select x-axis', all_columns, key='custom' + '_x_axis')
                y_axis = st.selectbox('Select y-axis', all_columns, key='custom' + '_y_axis')
                group_by = st.multiselect('Group data by', all_columns, key='custom' + '_group_by')
                color_by = st.selectbox('Color data by',all_columns, key='custom' + '_color_by')
                selected_min_date, selected_max_date = date_slider(df, 'custom', x_axis)

                chart_title = st.text_input('Chart Title', f'{chart}: {y_axis} vs. {x_axis}')
                chart_height = st.slider('Chart Height', min_value=300, max_value=800, value=500)
                
                df = df[df['Testdate'].dt.date.between(selected_min_date, selected_max_date)]
                if group_by != []:
                    if y_axis == 'Result':  
                        df = df.groupby(group_by).size().reset_index(name='Results Count')
                        y_axis = 'Results Count'
                    else:
                        df = df.groupby(group_by).agg({y_axis: 'mean'}).reset_index()
        if show_chart:
            if chart == "Line Chart":
                fig = line_chart(df, x_axis, y_axis, color_by)
            elif chart == "Bar Chart":
                fig = bar_chart(df, x_axis, y_axis, color_by)
            elif chart == "Box Plot":
                fig = box_plot(df, x_axis, y_axis, color_by)
            elif chart == "Violin Plot":
                fig = violin_plot(df, x_axis, y_axis, color_by)
            elif chart == "Scatter Plot":
                fig = scatter_plot(df, x_axis, y_axis, color_by)           
            fig.update_layout(title =chart_title, height=chart_height)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
            st.warning("Sorry, the chart cannot be generated. Please check your inputs.")
            return

def line_chart(df, x_axis, y_axis, color_by):
    '''
    Creates specific chart using Plotly Express

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        x_axis (str): Selected x-axis parameter
        y_axis (str): Selected y-axis parameter
        color_by (str): Selected color parameter

    Returns:
        plotly figure
    '''
    return px.line(df, x=x_axis, y=y_axis, color=color_by)

def scatter_plot(df, x_axis, y_axis, color_by):
    return px.scatter(df, x=x_axis, y=y_axis, color=color_by)
    
def box_plot(df, x_axis, y_axis, color_by): 
    return px.box(df, x=x_axis, y=y_axis, color=color_by)

def violin_plot(df, x_axis, y_axis, color_by): 
    return px.violin(df, x=x_axis, y=y_axis, color=color_by)

def bar_chart(df, x_axis, y_axis, color_by):
    if x_axis != 'Assay':
        fac = 'Assay'
    else:
        fac = None
    return  px.bar(df, x=x_axis, y=y_axis, color=color_by, facet_col=fac)

# File Upload
if 'loaded_data' not in st.session_state:
    st.session_state.loaded_data = None

uploaded_file = st.sidebar.file_uploader('Choose a CSV file', type=["csv"])
if uploaded_file is not None and st.session_state.loaded_data is None:
    st.session_state.loaded_data = load_data(uploaded_file) 
    st.toast('File uploaded successfully!')
    time.sleep(.5)

df = st.session_state.loaded_data
if df is not None:
    st.toast('Loading dashboard...')

    # Metrics
    col5, col6, col7, col8 = st.columns(4)
    col5.metric('Total Number of Samples',  df.shape[0])
    col6.metric('Number of Assays', df['Assay'].nunique())
    col7.metric('Minimum GMT', df['GMT'].min())
    col8.metric('Maximum GMT', df['GMT'].max())

    st.sidebar.divider()
    # Layout for charts
    st.sidebar.write("Chart Options")
    col1, col2 = st.columns(2)
    with col1:
        create_chart(df, 'Box plot', 2, 3, None, 0, box_plot)
    with col2:
        create_chart(df, 'Violin plot', 2, 3, None, 0,  violin_plot)
    create_chart(df, 'Line chart', 2, 3, ['Testdate', 'GMT', 'Assay'], 0, line_chart)
    col3, col4 = st.columns(2)
    with col3: 
        create_chart(df, 'Bar chart', 2, 4,  ['Assay', 'Testdate', 'Result'], 1, bar_chart)
    with col4:
        create_chart(df, 'Scatter plot', 0, 3, ['Testdate', 'GMT', 'Assay'], 0, scatter_plot)
    custom_chart(df)

