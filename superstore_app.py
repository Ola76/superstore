# import necessary libraries
import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import base64
from pandas.api.types import CategoricalDtype
from datetime 	import datetime

def prepare_data(data):
    """Function to preprocess and enhance the dataset."""
    # Calculate Revenue
    data['Revenue'] = data['Sales'] * data['Quantity']
    
    # Convert columns to datetime format
    data['Order Date'] = pd.to_datetime(data['Order Date'])
    data['Ship Date'] = pd.to_datetime(data['Ship Date'])
    
    # Extract month and year and then convert it to datetime format
    data['order_month_year'] = pd.to_datetime(data['Order Date'].dt.strftime('%Y-%m'))
    data['ship_month_year'] = pd.to_datetime(data['Ship Date'].dt.strftime('%Y-%m'))
    
    # Extract day_of_week, month, and year
    data["day_of_week_num"] = data["Order Date"].dt.dayofweek
    data["month"] = data["Order Date"].dt.month_name()
    data["order_year"] = data["order_month_year"].dt.year
    
    return data

# Initialize feedback list
feedback = []

# Dashboard Header
st.markdown("<h1 style='text-align: center; color: lightblue; font-family: cursive;'>Supermarket USA Dashboard</h1>", unsafe_allow_html=True)

# Sidebar Configurations
st.sidebar.title('Configuration')
uploaded_file = st.sidebar.file_uploader("Upload your dataset", type=["csv"])

# Check if data is uploaded; if not, use the default "supermarket.csv"
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
else:
    data = pd.read_csv("superstore.csv", encoding='ISO-8859-1')

# Prepare the data using the function
data = prepare_data(data)

# Display the data
st.write("Here's the dataset used:")
st.write(data)

# Sidebar navigators for choosing segments and ship modes
unique_segments = data['Segment'].unique()
selected_segments = st.sidebar.multiselect('Select Segments', unique_segments, default=unique_segments)

unique_ship_modes = data['Ship Mode'].unique()
selected_ship_modes = st.sidebar.multiselect('Select Ship Modes', unique_ship_modes, default=unique_ship_modes)

# Filter data based on selected segments and ship modes
filtered_data = data[data['Segment'].isin(selected_segments) & data['Ship Mode'].isin(selected_ship_modes)]

# Function to create a KDE plot
def create_kde_plot(data, column, group_column):
    unique_groups = data[group_column].unique()
    grouped_data = [data[data[group_column] == group][column].values for group in unique_groups]
    
    fig = ff.create_distplot(grouped_data, unique_groups, bin_size=.2, show_rug=False, show_hist=False)
    
    for trace in fig['data']:
        if trace['type'] == 'histogram':
            trace['opacity'] = 0
    fig.update_layout(title_text=f"{column} distribution by {group_column}")
    return fig

# Count values for 'Segment' and 'Ship Mode' from filtered data
segment_counts = filtered_data['Segment'].value_counts()
ship_mode_counts = filtered_data['Ship Mode'].value_counts()

# Pie chart for 'Segment'
fig1 = px.pie(segment_counts, values=segment_counts.values, names=segment_counts.index, title="Distribution of Customer Segments")
st.plotly_chart(fig1)
# Bar graph for 'Ship Mode'
fig2 = px.bar(ship_mode_counts, x=ship_mode_counts.index, y=ship_mode_counts.values, title="Distribution of Customer Shipping Modes")
st.plotly_chart(fig2)

fig1 = create_kde_plot(filtered_data, "Discount", "Segment")
st.plotly_chart(fig1)
fig2 = create_kde_plot(filtered_data, "Quantity", "Ship Mode")
st.plotly_chart(fig2)

# Create a scatter plot for Sales vs. Revenue
fig = px.scatter(data, x='Sales', y='Revenue', title="Sales vs. Revenue")
st.plotly_chart(fig)

st.markdown("<h1 style='text-align: center; color: lightblue; font-family: cursive;'>Products Decriptions</h1>", unsafe_allow_html=True)
fig_sunburst = px.sunburst(data, path=['Category', 'Sub-Category'], values='Revenue',
                color='Revenue',
                color_continuous_scale='Blues')
st.plotly_chart(fig_sunburst)

# Grouping by 'Category' and 'Sub-Category' and counting the occurrences
agg_data = data.groupby(['Category', 'Sub-Category']).size().reset_index(name='counts')

# Creating unique list of categories and sub-categories
categories = agg_data['Category'].unique().tolist()
sub_categories = agg_data['Sub-Category'].unique().tolist()

# Creating a unified list of labels
labels = categories + sub_categories

# Creating sources (for categories)
sources = [categories.index(cat) for cat in agg_data['Category']]

# Creating targets (for sub-categories)
targets = [sub_categories.index(sub_cat) + len(categories) for sub_cat in agg_data['Sub-Category']]

# Values are the counts
values = agg_data['counts'].tolist()

# Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels),
    link=dict(source=sources, target=targets, value=values)
)])

fig.update_layout(title_text="Sankey Diagram of Categories and Sub-Categories", font_size=10)
st.plotly_chart(fig)

# Streamlit checkbox to toggle between Category and Sub-Category
show_subcategory = st.checkbox('Show Sub-Category instead of Category')

if show_subcategory:
    # Count values for 'Sub-Category'
    sub_category_counts = data['Sub-Category'].value_counts()
    fig = px.bar(sub_category_counts, x=sub_category_counts.index, y=sub_category_counts.values, title="Count of Sub-Categories")
else:
    # Count values for 'Category'
    category_counts = data['Category'].value_counts()
    fig = px.bar(category_counts, x=category_counts.index, y=category_counts.values, title="Count of Categories")

st.plotly_chart(fig)

st.markdown("<h1 style='text-align: center; color: lightblue; font-family: cursive;'>Revenue by States</h1>", unsafe_allow_html=True)

# Streamlit checkbox to toggle between Category and Sub-Category
show_subcategory = st.checkbox('Show States instead of Regions', key="unique_checkbox_key")

if not show_subcategory:
    # Region
    category_counts = data['Region'].value_counts()
    fig = px.bar(category_counts, x=category_counts.index, y=category_counts.values, title="Distribution across Regions")
    st.plotly_chart(fig)
else:
    agg_data_count = data.groupby('State').size().reset_index(name='Count')
    
    fig_bar = px.bar(agg_data_count, 
            x='State', 
            y='Count',
            title='Count of Entries by U.S. State',
            labels={'Count':'Number of Entries'},
            color='Count', 
            color_continuous_scale='Blues'
            )
    fig_bar.update_layout(coloraxis_showscale=False)  # To hide the color scale if not needed
    st.plotly_chart(fig_bar)

# Group by State and sum the revenues and quantity
grouped_data = data.groupby(['State', 'Region']).agg({'Revenue': 'sum', 'Quantity': 'sum'}).reset_index()
# Sort by revenue in descending order and display the top 10
sorted_data = grouped_data.sort_values(by='Revenue', ascending=False).head(10)
# Display top 10 states by revenue
st.subheader("Top 10 States by Revenue")
st.dataframe(sorted_data)

# Coloring based on a threshold value
def color_by_threshold(s, threshold=100000):
    return ['background-color: green' if v > threshold else 'background-color: red' for v in s]

styled_data = grouped_data.style.apply(lambda s: color_by_threshold(s), subset=['Revenue'])

# Use expander to show all states with styled data
with st.expander("Click to see revenue for all states"):
    st.write(styled_data)

# Download link for grouped data
def create_download_link(df, filename="data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() 
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'

download_link = create_download_link(grouped_data[['State', 'Region', 'Quantity', 'Revenue']])
st.markdown(download_link, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: lightblue; font-family: cursive;'>Time Series Analysis</h1>", unsafe_allow_html=True)
# Creating columns for side by side date inputs
col1, col2 = st.columns(2)
# Get start and end dates from user in the created columns
with col1:
    start_date = pd.Timestamp(st.date_input("Start Date", data['Order Date'].min()))

with col2:
    end_date = pd.Timestamp(st.date_input("End Date", data['Order Date'].max()))

# Filter data based on the chosen date range
filtered_data = data[(data['Order Date'] >= start_date) & (data['Order Date'] <= end_date)]
# Radio button for selecting the view
option = st.radio(
    'Choose a view:',
    ('day_of_week_num', 'month', 'order_month_year')
)

# Aggregate filtered data based on the selected option
if option == 'day_of_week_num':
    agg_data = filtered_data.groupby('day_of_week_num').agg({'Revenue':'sum'}).reset_index()
    # Plot using the numbers
    title = "Revenue by Day of Week (0=Monday, 6=Sunday)"
    fig = px.line(agg_data, x='day_of_week_num', y='Revenue', title=title)
elif option == 'month':
    # Order the months starting from January
    month_order = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]
    cat_dtype = CategoricalDtype(categories=month_order, ordered=True)
    filtered_data['month'] = filtered_data['month'].astype(cat_dtype)
    agg_data = filtered_data.groupby('month').agg({'Revenue':'sum'}).reset_index()
    title = "Revenue by Month"
    fig = px.line(agg_data, x='month', y='Revenue', title=title)
else:
    agg_data = filtered_data.groupby('order_month_year').agg({'Revenue':'sum'}).reset_index()
    title = "Revenue by Month-Year"

# Create a line chart using Plotly
fig = px.line(agg_data, x=option, y='Revenue', title=title)
st.plotly_chart(fig)

st.markdown("<h1 style='text-align: center; color: lightblue; font-family: cursive;'>Order tracker</h1>", unsafe_allow_html=True)
# Create search bar with title "Order tracker bar"
order_id_search = st.text_input("Please type Order ID:", "")

# Check if the entered Order ID is in the database
if order_id_search:
    matched_data = data[data['Order ID'] == order_id_search]
    if not matched_data.empty:
        st.write(matched_data)
        # Convert matched data to CSV and let the user download it
        csv = matched_data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # Encode to UTF8 and then decode to string
        href = f'<a href="data:file/csv;base64,{b64}" download="matched_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("Order ID not found in the database!")

# Feedback system in sidebar
st.sidebar.subheader("Feedback System")
feedback_date = st.sidebar.date_input('Feedback Date', datetime.now())
feedback_text = st.sidebar.text_input('Feedback (max 100 chars)', max_chars=100)
col_save, col_delete = st.sidebar.columns(2)

# Save Feedback
with col_save:
    if st.button('Save Feedback'):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        feedback_item = {
            'feedback_date': feedback_date,
            'feedback_text': feedback_text,
            'timestamp': current_time
        }
        feedback.append(feedback_item)
        st.sidebar.write("Thank you for your feedback!")
        
        # Convert feedback list to DataFrame
        feedback_df = pd.DataFrame(feedback)
        # Download link if feedback DataFrame is not empty
        if not feedback_df.empty:
            st.sidebar.markdown(generate_download_link(feedback_df, 'feedback.csv', 'Download Feedback as CSV'), unsafe_allow_html=True)

# Delete Last Feedback
with col_delete:
    if st.button('Delete Last Feedback') and feedback:
        feedback.pop()
        st.sidebar.write("Last feedback deleted!")