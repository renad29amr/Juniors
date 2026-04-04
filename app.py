# Importing required libraries
import streamlit as st  # Used to build the web app
import pandas as pd  # Used for data manipulation and analysis
import matplotlib.pyplot as plt  # Used for plotting graphs
import seaborn as sns  # Used for advanced visualizations

# Configure the Streamlit page (title + layout)
st.set_page_config(page_title="Car Data Analysis", layout="wide")

# ==========================================================
# LOAD DATA
# ==========================================================

# Read dataset from CSV file
# IMPORTANT: Make sure the file is in the same folder as this script
# Otherwise, provide the full path

df = pd.read_csv("USA_cars_datasets.csv")

# Display main title in the app
st.title("🚗 Car Dataset Analysis")

# ==========================================================
# DATA CLEANING
# ==========================================================

# Create a copy of the original dataframe
# This ensures we do not modify the original dataset directly

df_cleaned = df.copy()

# Drop unnecessary columns
# - 'Unnamed: 0' → usually index column
# - 'vin', 'lot' → not useful for analysis
# errors='ignore' prevents crash if column doesn't exist

df_cleaned.drop(columns=["Unnamed: 0", "vin", "lot"], inplace=True, errors="ignore")

# Remove missing values (NaN rows)
df_cleaned.dropna(inplace=True)

# Remove duplicate rows (if any exist)
df_cleaned.drop_duplicates(inplace=True)

# Clean 'country' column:
# - Remove extra spaces (strip)
# - Convert all text to lowercase for consistency

df_cleaned["country"] = df_cleaned["country"].str.strip().str.lower()

# Convert mileage (miles) → kilometrage (km)
# 1 mile = 1.60934 km
# round() → round values
# astype(int) → convert to integer type

df_cleaned["kilometrage"] = (df_cleaned["mileage"] * 1.60934).round().astype(int)

# Drop original 'mileage' column after conversion
df_cleaned.drop(columns=["mileage"], inplace=True)

# Create a new feature: car age
# Age = current year (2026) - manufacturing year

df_cleaned["car_age"] = 2026 - df_cleaned["year"]

# ==========================================================
# SIDEBAR FILTERS (MULTI-SELECT)
# ==========================================================

# Sidebar title
st.sidebar.header("Filters")

# Allow user to select multiple brands
# Default: first 5 brands

selected_brand = st.sidebar.multiselect(
    "Select Brand",
    options=df_cleaned["brand"].unique(),
    default=df_cleaned["brand"].unique()[:5],
)

# Filter dataset based on selected brands
filtered_df = df_cleaned[df_cleaned["brand"].isin(selected_brand)]

# ==========================================================
# SHOW DATA OPTIONS
# ==========================================================

# Checkbox to show raw (original) data
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.dataframe(df.head())  # Show first 5 rows

# Checkbox to show cleaned data
if st.checkbox("Show Cleaned Data"):
    st.subheader("Cleaned Data")
    st.dataframe(df_cleaned.head())  # Show first 5 rows

# ==========================================================
# 1. KILOMETRAGE VS PRICE
# ==========================================================

st.subheader("Kilometrage vs Price")

# Dropdown to choose X-axis dynamically
# User can explore different relationships
x_axis = st.selectbox(
    "Select X-axis", ["kilometrage", "car_age", "year"], key="plot1_x"
)

# Create scatter plot
fig1, ax1 = plt.subplots()
sns.scatterplot(data=filtered_df, x=x_axis, y="price", ax=ax1)

# Display plot in Streamlit
st.pyplot(fig1)

# ==========================================================
# 2. PRICE DISTRIBUTION
# ==========================================================

st.subheader("Price Distribution")

# Dropdown to control histogram bins
# More bins = more detailed distribution
bins = st.selectbox("Select number of bins", [20, 30, 50, 100], key="bins")

# Create histogram
fig2, ax2 = plt.subplots()
sns.histplot(filtered_df["price"], bins=bins, kde=True, ax=ax2)

st.pyplot(fig2)

# ==========================================================
# 3. TOP BRANDS DISTRIBUTION
# ==========================================================

st.subheader("Top Brands")

# Dropdown to choose number of top brands
brand_top_n = st.selectbox("Top N Brands", [5, 10, 15], key="top_brands")

# Count most frequent brands
brand_counts = df_cleaned["brand"].value_counts().head(brand_top_n)

# Create pie chart
fig3, ax3 = plt.subplots()
ax3.pie(brand_counts, labels=brand_counts.index, autopct="%1.1f%%")

st.pyplot(fig3)

# ==========================================================
# 4. AVERAGE PRICE BY BRAND
# ==========================================================

st.subheader("Average Price by Brand")

# Dropdown to control how many brands to show
brand_price_n = st.selectbox("Top N Brands by Price", [5, 10, 15], key="brand_price")

# Group by brand and calculate mean price
brand_price = df_cleaned.groupby("brand")["price"].mean()

# Sort descending and take top N
brand_price = brand_price.sort_values(ascending=False).head(brand_price_n)

# Create bar chart
fig4, ax4 = plt.subplots()
sns.barplot(x=brand_price.index, y=brand_price.values, ax=ax4)

# Rotate labels for better readability
ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45)

st.pyplot(fig4)

# ==========================================================
# 5. CAR AGE VS PRICE
# ==========================================================

st.subheader("Car Age vs Price")

# Scatter plot to show relationship
fig5, ax5 = plt.subplots()
sns.scatterplot(data=filtered_df, x="car_age", y="price", ax=ax5)

st.pyplot(fig5)

# ==========================================================
# 6. COLOR DISTRIBUTION
# ==========================================================

st.subheader("Top Colors")

# Dropdown for number of colors
color_top_n = st.selectbox("Top N Colors", [5, 8, 10], key="colors")

# Count colors
color_counts = df_cleaned["color"].value_counts().head(color_top_n)

# Pie chart
fig6, ax6 = plt.subplots()
ax6.pie(color_counts, labels=color_counts.index, autopct="%1.1f%%")

st.pyplot(fig6)

# ==========================================================
# 7. CORRELATION HEATMAP
# ==========================================================

st.subheader("Correlation Heatmap")

# Select numerical columns
corr = df_cleaned[["price", "year", "kilometrage", "car_age"]].corr()

# Plot heatmap
fig7, ax7 = plt.subplots()
sns.heatmap(corr, annot=True, ax=ax7)

st.pyplot(fig7)

# ==========================================================
# INSIGHTS
# ==========================================================

st.subheader("Insights")

# Key observations based on analysis
st.write(
    "- Price generally decreases as kilometrage increases (negative relationship)."
)
st.write("- Newer cars (low car_age) tend to have higher prices.")
st.write("- Some brands dominate the dataset more than others.")
st.write("- Correlation heatmap helps understand relationships between variables.")
