# Import Libraries
 
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import plotly.express as px
from PIL import Image 
from itertools import combinations# To find every possible pair of aspects in a single review



# =============================================================================================================================================================
# LOAD DATA 
# =============================================================================================================================================================

# READIND DATASET 

df = pd.read_excel('Virtual Assistant Devices Dataset.xlsx')


#==============================================================================================================================================================
# Data Cleaning
# =============================================================================================================================================================
# Create a copy of the original dataset to avoid modifying it directly
df_cleaned = df.copy()
# Keep/ensure consistency in important columns (Device Name, Company, Source)
df_cleaned[['Device Name','Company','Source']] = df_cleaned[['Device Name','Company','Source']].ffill()

# Remove unnecessary column 
df_cleaned = df_cleaned.drop(columns=['Unnamed: 4'])

# Drop rows where Description is missing (since it's important for analysis)
df_cleaned = df_cleaned.dropna(subset=["Description"])
 

# Standardize device names to avoid duplicates with different formats
df_cleaned['Device Name'] = df_cleaned['Device Name'].replace({
    'Amazon Echo (4th Gen) - Smart Home Hub with Alexa': 'Amazon Echo 4th Gen',

    'Apple HomePod (2023, 2nd Generation)': 'Apple HomePod 1st Gen',

    'Google Nest Hub (2nd Gen) Smart Display': 'Google Nest Hub 2nd Gen',

    'Google Nest Hub with Built-In Google Assistant, Chalk (GA00516-US)': 'Google Nest Hub 2nd Gen',

    '\xa0Google Nest Hub 2nd Gen - Smart Home Display with Google Assistant - Charcoal': 'Google Nest Hub 2nd Gen',

    'Lenovo Smart Clock Gen 2 - Blue': 'Lenovo Smart Clock Gen 2',

    'TCL 32" Class 3-Series HD 720p LED Smart Roku TV - 32S355': 'TCL 32" 3-Series Roku TV',

    'Samsung - 75" Class TU690T Crystal UHD 4K Smart Tizen TV': 'Samsung 75" Crystal UHD 4K TV',

    'Google - Nest Learning Smart Wifi Thermostat': 'Google Nest Learning Thermostat',

    'Apple AirPods (2nd Generation) Wireless Ear Buds': 'Apple AirPods 2nd Gen'
})


# List of devices we want to remove from the dataset
values_to_remove = ['TCL 32" 3-Series Roku TV', 'Samsung 75" Crystal UHD 4K TV','Apple AirPods 2nd Gen']
# Remove rows that contain these devices
df_cleaned = df_cleaned[~df_cleaned['Device Name'].isin(values_to_remove)] #



# Combine all aspect columns into one column called "Aspects"
df_cleaned['Aspects'] =list(zip(df_cleaned['Aspect(s)'],df_cleaned['Unnamed: 7'], df_cleaned['Unnamed: 8'],df_cleaned['Unnamed: 9'],df_cleaned['Unnamed: 10']))

# Drop the old columns after combining them
df_cleaned.drop(columns=['Aspect(s)','Unnamed: 7','Unnamed: 8','Unnamed: 9','Unnamed: 10'],inplace=True)

# Remove null values from the Aspects list
df_cleaned['Aspects'] = df_cleaned['Aspects'].apply(
    lambda x: [i for i in x if pd.notnull(i)]
)  #[list comperhention]

# Convert each list inside "Aspects" into separate rows
df_cleaned = df_cleaned.explode('Aspects')

# Remove any empty values in Aspects
df_cleaned= df_cleaned.dropna(subset='Aspects')



# Fix names to make them clear and consistent
df_cleaned['Aspects'] = df_cleaned['Aspects'].replace({
    'Colour':'Color',
    'Alaram':'Alarm',
    'onfiguration':'Configuration',
    'Battery':'Battery Life'

})
# Make the first letter of each aspect capital (for consistency)
df_cleaned['Aspects'] = df_cleaned['Aspects'].str.capitalize()

# Combine all descriptions into one big text
text = " ".join(df_cleaned['Description'].astype(str))
# Convert text to lowercase and split into words
words = text.lower().split()

# Remove duplicate rows from the dataset
df_cleaned.drop_duplicates(inplace=True)



df_cleaned = df_cleaned.reset_index(drop=True)





# =============================================================================================================================================================
# Analysis
# =============================================================================================================================================================
 


# Create two columns (left for text, right for image)
# The ratio [2, 1] means the left column is wider than the right one
col1, col2 = st.columns([2, 1])

# Left column: contains the main title and subtitle
with col1:
    st.divider()  # Adds a horizontal line above the title
    
    st.title("Assistify")  # Main title of the page
    
    st.subheader("DATA ANALYSIS TEAM")  # Subtitle under the title
    
    st.divider()  # Adds a horizontal line below the subtitle

# Right column: contains the logo/image
with col2:
    img = Image.open("logo of assistify.png") # Open the image file
    st.image(img, width=400) # Display the image with a specified width


# =============================================================================================================================================================
# Description & Our Vision
#
#============================================================================================================================================================

# Add spacing
st.write("")
    
# Description section
st.title("Description:")
st.write("""
    We are a data analysis team. We specialize in analyzing datasets for Personal Assistants.  

    We help companies and developers understand user behavior better. We look at how people use their assistants, what they ask, and how they feel.  

    Our goal is to make Personal Assistants smarter, faster, and more personal. We turn data into useful insights so you can build better experiences for your users.  

    Your data helps us create assistants that understand people more deeply.
    """)

# Add spacing between sections
st.write("")
st.write("")
    
# Vision section
st.title("Our Vision:")
st.write("""
    We believe Personal Assistants should feel like real friends.  

    In the future, every assistant will not only answer questions, but also understand what the user really needs.  

    We want to make technology simple and natural.  

    We dream of a world where your assistant knows you well, helps you quickly, and makes your life easier every day.  

    No more boring or wrong answers — only smart, helpful, and friendly conversations.
    """)

# =============================================================================================================================================================
# Show Data Options
# =============================================================================================================================================================


# Add spacing
st.write("")
st.write("")

# Checkbox to show raw (original) data
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.dataframe(df.head())  # Show first 5 rows

# Checkbox to show cleaned data
if st.checkbox("Show Cleaned Data"):
    st.subheader("Cleaned Data")
    st.dataframe(df_cleaned.head())  # Show first 5 rows









try:
    # Use column index to avoid Name Errors
    # Column 0 = Company Name | Column 1 = Sentiment
    comp_col = df_cleaned.columns[1]
    sent_col = df_cleaned.columns[4]
except Exception as e:
    st.error(f"Please ensure 'Virtual Assistant Devices Dataset.xlsx' is in the same folder. Error: {e}")
    st.stop()

col_left, col_right = st.columns([1, 2]) # Left side narrower

with col_left:
    st.markdown('<p class="company-header">Companies:</p>', unsafe_allow_html=True)
    
    # Selection Box
    company_list = sorted(df_cleaned[comp_col].dropna().unique().tolist())
    selected_company = st.selectbox(
        "", 
        options=company_list,
        placeholder="choose a company",
        label_visibility="collapsed"
    )

# 5. Filter and Calculate Real Percentages
filtered_df = df_cleaned[df_cleaned[comp_col] == selected_company]
counts = filtered_df[sent_col].value_counts()

with col_right:
    # 6. Create Donut Chart (Colors match your image)
    if not counts.empty:
        fig = px.pie(
            values=counts.values, 
            names=counts.index, 
            hole=0.6,
            color=counts.index,
            color_discrete_map={
                'Positive': '#3498db', # Blue
                'Negative': '#9b59b6', # Purple
                'Neutral': '#e67e22'   # Orange
            }
        )
        
        # Format labels like your prototype (Percent + Label)
        fig.update_traces(textinfo='percent+label', textfont_size=14)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Select a company to view analysis.")







#===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
#Sentiment with bichart
#============================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

# 1. Page Settings
st.set_page_config(layout="wide")


# 2. Custom CSS for the Black Box and White Arrow
st.markdown("""
    <style>
    /* Make selectbox background black and text white */
    div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        color: white !important;
        border: 1px solid #444;
        border-radius: 4px;
    }
    /* Make the dropdown arrow white */
    svg[role="presentation"] {
        fill: white !important;
    }
    /* Style the heading */
    .company-header {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
             """, unsafe_allow_html=True)









with st.expander("Questions",  expanded= True):
  
    with st.expander("what is the sentiment per device"):

        # Group data by Device Name and Sentiment, then count reviews
        grouped = df_cleaned.groupby(['Device Name','Sentiment']).size().unstack().fillna(0)

        # Plot the results as a bar chart
        fig1,ax1 = plt.subplots(figsize=(15, 4))
        grouped.plot(kind='bar', ax=ax1)
        # Add chart title and labels
        plt.title("Sentiment per Device")
        plt.xlabel("Device Name")
        plt.ylabel("Number of reviews")
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=90)

        st.pyplot(fig1)
        st.write("**INSIGHT : Lenovo has the most sentiment for overall reviews.**")




    with st.expander(" What Are the Most Frequent Negative Aspects by Users ?"):
        # Another way to group and reshape the data (same idea as above)
        df_cleaned.groupby(['Device Name', 'Sentiment']).size().unstack(fill_value=0)

        # Create a large figure for a clear and readable chart
        fig, ax = plt.subplots(figsize=(20, 7))

        # Step 1: Filter the data to get only Negative reviews
        # Use .copy() to create a clean, independent DataFrame
        negative_df_cleaned = df_cleaned[df_cleaned["Sentiment"] == "Negative"].copy()


        # Step 2: Count the frequency of each aspect in the negative reviews
        aspect_counts = negative_df_cleaned['Aspects'].value_counts()

        # Step 3: Plot the top 10 most common negative aspects
        # Using a bar chart for easy comparison
        aspect_counts.head(10).plot(kind='bar', ax=ax)

        # Step 4: Add clear titles and labels for the axesative Aspects
        plt.title("Most Frequent Negative Aspects")
        plt.xlabel("negative_df_cleaned")
        plt.ylabel("Count")
        # Rotate labels by 45 degrees to prevent overlapping
        plt.xticks(rotation=45)
        # Adjust layout to make sure everything fits perfectly
        plt.tight_layout()
        st.pyplot(fig)
        st.write("**INSIGHT : Connectivity is mentioned as the most negative aspect.**")

    #==============================================================



    with st.expander("What Are the Most Frequent Positive Aspects?"):

        # Initialize a large figure for better clarity and readability
        fig = plt.figure(figsize=(20, 7))

        # Step 1: Filter the dataset for "Positive" sentiment only
        # Using .copy() to ensure data integrity and avoid memory warnings
        positive_df_cleaned = df_cleaned[df_cleaned["Sentiment"] == "Positive"].copy()


        # Step 2: Compute the frequency of each aspect within the positive results
        aspect_counts = positive_df_cleaned['Aspects'].value_counts()

        # Step 3: Visualize the top 10 aspects using a bar chart
        # Focusing on the top 10 provides a cleaner and more insightful summary
        aspect_counts.head(10).plot(kind='bar')

        # Add descriptive title and axis labels for professional presentation
        plt.title("Most Frequent Positive Aspects")
        plt.title("Most Frequent Positive Aspects")
        plt.xlabel("positive_df_cleaned")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        # Final layout adjustment to prevent elements from overlapping
        plt.tight_layout()

        st.pyplot(fig)
        st.write("**INSIGHT : Clock is the most mentioned positive aspect.**")

    #==============================================================


    # Question: Which aspects frequently appear together in negative reviews?(Identifying Co-occurring Aspects (Advanced Analysis))


    with st.expander("Which aspects frequently appear together in negative reviews?"):
        st.write("(Identifying Co-occurring Aspects (Advanced Analysis))")
        # Filter for "Negative" sentiment to analyze the most common "Pain Points
        negative_reviews = df_cleaned[df_cleaned['Sentiment'] == 'Negative'].copy()

        # Grouping aspects by review index to see which problems appear together in one comment
        # This creates a "List of Aspects" for each individual customer review
        grouped_aspects = negative_reviews.groupby(negative_reviews.index)['Aspects'].apply(lambda x: [item for item in x if pd.notna(item)])

        # Calculate co-occurrence counts(Initialize the Counter for the final result)
        co_counts = Counter()
        # Main Loop: Extracting correlations between negative aspects
        for aspects_list in grouped_aspects:
            # Use combinations to create unique pairs (A, B) and (B, A) are treated as one
            # Sorting ensures consistency, and set() removes duplicate aspects from the same review
                for pair in combinations(sorted(set(aspects_list)), 2):
                    co_counts[pair] += 1
                    


    

        neg_reviews_exploded = df_cleaned[df_cleaned['Sentiment'] == 'Negative'].copy()

        # Group by the original index to collect all aspects from the same review into a list
        grouped_aspects_for_cooccurrence = neg_reviews_exploded.groupby('Description')['Aspects'].apply(lambda x: [item for item in x if pd.notna(item)])

        # Calculate co-occurrence counts
        counts = Counter()

        for aspects_list in grouped_aspects_for_cooccurrence:
            # Only consider lists with more than one aspect to form pairs
            if isinstance(aspects_list, list) and len(aspects_list) > 1:
                # Use sorted(set()) to ensure unique aspects within a list and consistent pairing order
                for pair in combinations(sorted(set(aspects_list)), 2):
                    counts[pair] += 1

        # 1. Transform the "Counter" into a "Symmetric Matrix" (Square Table)
        # This step is essential because Heatmaps require structured data (Rows & Columns)
        all_aspects = sorted(list(set(item for sublist in counts.keys() for item in sublist)))
        # Create an empty matrix
        matrix = pd.DataFrame(0, index=all_aspects, columns=all_aspects)

        # Populate the matrix(Fill the matrix with "Symmetry" (A-B = B-A))  
        # This ensures the heatmap is visually balanced and easy to read
        for (a, b), c in counts.items():
            matrix.loc[a, b] = c
            matrix.loc[b, a] = c # Ensure symmetry

        fig, ax = plt.subplots(figsize=(15, 5))
        #Plot the Heatmap for Visual Insights
        # Using Seaborn to highlight the strongest correlations between aspects
        sns.heatmap(matrix, annot=True, cmap='Reds', fmt='d', ax=ax)
        # Add professional titles and labels to the chart
        plt.title('Aspect Co-occurrence Heatmap (Negative Reviews)')
        plt.xlabel('Aspects')
        plt.ylabel('Aspects')

        st.pyplot(fig)
        st.write("**INSIGHT : Connectivity & Clock are the most aspects which related to each other.**")

    #==============================================================




    with st.expander("Social-Emotional Bondsoc"):
        st.write("Is there an emotional bond betwwen the device and the user")

        #The QUESTION:Is there an emotional bond betwwen the device and the user

        # Step1 : Define a list of positive keywords to identify "Sial-Emotional Bondsoc"
        keywords = ["love", "great", "nice", "good"]

        # Step 2: Create a 'Mask' to filter descriptions that contain our keywords
        # .str.contains('|'.join) helps us search for all keywords at once
        mask = df_cleaned['Description'].str.lower().str.contains('|'.join(keywords), na=False)

        # Step 3: Get only the filtered data that matches our search
        bond_descriptions = df_cleaned[mask]['Description']

        # Step 4: Combine all text into one large string for the WordCloud
        text = " ".join(bond_descriptions)

        # --- Visualizing the WordCloud ---

        # Create the WordCloud with a white background and specific size
        wc = WordCloud(width=700, height=300, background_color='white').generate(text)

        # Plot the WordCloud image
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear')

        # 3. Remove the axes (the numbers on the side)
        ax.axis('off')
        ax.set_title("Social-Emotional Bond Keywords in Descriptions", fontsize=14)

        st.pyplot(fig)
        st.write("**INSIGHT : Impact of the device on users life.**")

    #==============================================================



    #THE QUESTION:How does "Sentiment" vary across different "Sources"?
    # --- Section 1: Sentiment Analysis by Source ---


    with st.expander("How does Sentiment vary across different Sources"):
        st.subheader("Does users reviews among differnt sources differ from each other ?")

        # 1. Group data by 'Source' and 'Sentiment' to count occurrences
        df_cleaned_counts = df_cleaned.groupby(['Source', 'Sentiment']).size().reset_index(name='count')

        # 2. Use a Pivot Table to restructure the data for plotting
        # This makes it easy to see sentiments side-by-side for each source
        df_cleaned_pivot = df_cleaned_counts.pivot(index='Source', columns='Sentiment', values='count').fillna(0)

        #3. Create a 'Stacked Bar Chart' to compare sentiment distributions
        fig1, ax1 = plt.subplots(figsize=(15,6))
        df_cleaned_pivot.plot(kind='bar', stacked=True, ax=ax1)
        ax1.set_title("Sentiment Vs Source")

        st.pyplot(fig1)
        st.write("**INSIGHT : Best Buy is the source that has the most number of reviews.**")








    # --- Section 2: Relationship Between Top Aspects and Device Names  ---
    with st.expander("what are the top 5 most frequent aspects in each device"):
        # 4. Identify the Top 5 most frequent aspects in the dataset
        top_aspects = df_cleaned['Aspects'].value_counts().head(5).index

        # 5. Filter the dataframe to include ONLY these top 5 aspects
        filtered_df_cleaned = df_cleaned[df_cleaned['Aspects'].isin(top_aspects)]

        # 6. Create a Cross-tabulation (Crosstab) to show the relationship between Devices and Aspects
        ct = pd.crosstab(filtered_df_cleaned['Device Name'], filtered_df_cleaned['Aspects'])

        # 7. Plot the results in a bar chart for easy comparison
        fig2, ax2 = plt.subplots()
        ct.plot(kind='bar', ax=ax2)


        # 8. Add professional titles and move the legend for better visibility
        plt.title("Aspects vs Device Name (Top 5 Aspects)")
        plt.xlabel("Device Name")
        plt.ylabel("Number of Mentions")
        plt.xticks(rotation=90)
        plt.legend(title="Aspects", bbox_to_anchor=(1.05, 1))
        plt.tight_layout()

        st.pyplot(fig2)
        st.write("**INSIGHT 1 : Different devices have different dominant problems.**")
        st.write("**INSIGHT 2 : Connectivity is a common issue across all devices.**")



    #==============================================================

    #THE QUESTION: WHICH DEVICE IS THE BEST AND WHICH DEVICE IS THE WORST 

    with st.expander("Which device is the best used ?"):
        # --- STEP 1: Calculate Positive Ratio (Stability Score) ---

        # 1. Count only 'Positive' reviews for each individual device
        positive_counts = df_cleaned[df_cleaned['Sentiment'] == 'Positive'].groupby('Device Name').size()

        # 2. Count the 'Total' number of reviews for each device
        total_counts = df_cleaned.groupby('Device Name').size()

        ## 3. Compute the 'Stability Score' by dividing positive counts by total counts
        # Using .fillna(0) to handle devices with no positive reviews
        stability_score = (positive_counts / total_counts).fillna(0)

        # --- STEP 2: Ranking and Sorting ---

        # 4. Sort the devices from 'Best to Worst' based on their score
        # 'ascending=False' puts the highest scores at the top
        stability_score = stability_score.sort_values(ascending=False)


        # --- STEP 3: Visualizing the Results ---

        # 5. Create a Bar Chart to show the ranking of all devices
        fig, ax = plt.subplots(figsize=(12, 6))
        stability_score.plot(kind='bar', ax=ax)

        # 6. Add professional labels to clearly show the performance ranking
        plt.title("Devices Ranking (Best to Worst)")
        plt.xlabel("Device")
        plt.ylabel("Stability Score (Positive Ratio)")

        # Rotate labels for better readability
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)
        st.write("**INSIGHT : Apple Device has the highest positive ratio according to its review.**")

#//////////////////////////////////////////////////////////////////

#==============================================================
#THE QUESTION: what aspects are mentioned the most by the users?
#Most discussed aspects in users reviews


with st.expander('Most discussed aspects in users reviews'):

    fig, ax = plt.subplots(figsize=(15,6))
    df_cleaned['Aspects'].value_counts().head(10).plot(kind='barh', ax=ax)
    #THE TITLE
    plt.title("Most Discussed Aspects")
    plt.xlabel("Number of Mentions")

    # It reverses the vertical axis of the current plot,
    # making high values appear at the bottom and low values at the top
    plt.gca().invert_yaxis()
    st.pyplot(plt.gcf())
    st.write("**INSIGHT : Clock , Connectivity and smart assistants are the most important aspect in all devices.**")

#==============================================================
st.header("WHAT ARE THE WEAK POINTS IN EACH DEVICE ACCORDING TO THE SAME ASPECT?")



with st.expander("Clock"):
 
    #1. Convert text to numbers (polarity )
    Sentiment_map = {'Positive':1,'Neutral':0,'Negative':-1}
    # Mapping the sentiment and ensuring the result is numric
    df_cleaned.loc[:,'Polarity']=df_cleaned['Sentiment'].map(Sentiment_map)
    #Pick your asspect
    #Ensuredf_aspect is an independent copy
    df_aspect=df_cleaned[df_cleaned['Aspects']=='Clock']
    #3. Draw the line
    if not df_aspect.empty:
     fig, ax = plt.subplots(figsize=(10, 6))
        
    sns.lineplot(data=df_aspect, x='Device Name', y='Polarity', marker='o', ax=ax)
    plt.xticks(rotation=45)#Help if device names are long
    ax.set_title('Users Sentiment towards Clock for each Device')
    st.pyplot(fig)

#==============================================================
with st.expander("Price"):

    #1. Convert text to numbers (polarity )
    Sentiment_map = {'Positive':1,'Neutral':0,'Negative':-1}
    # Mapping the sentiment and ensuring the result is numric
    df_cleaned.loc[:,'Polarity']=df_cleaned['Sentiment'].map(Sentiment_map)
    #Pick your asspect
    #Ensure df_aspect is an independent copy
    df_aspect=df_cleaned[df_cleaned['Aspects']=='Price']
    #3. Draw the line
    if not df_aspect.empty:
     fig10, ax10 = plt.subplots(figsize=(12, 6))
        
    sns.lineplot(data=df_aspect, x='Device Name', y='Polarity', marker='o', ax=ax10)
    plt.xticks(rotation=45)#Help if device names are long
    ax10.set_title('Users Sentiment towards Price for each Device',fontsize=15)
    
    st.pyplot(fig10)

#==============================================================
with st.expander("Connectivity"):

    #1. Convert text to numbers (polarity )
    Sentiment_map = {'Positive':1,'Neutral':0,'Negative':-1}
    # Mapping the sentiment and ensuring the result is numric
    df_cleaned.loc[:,'Polarity']=df_cleaned['Sentiment'].map(Sentiment_map)
    #Pick your asspect
    #Ensure df_aspect is an independent copy
    df_aspect=df_cleaned[df_cleaned['Aspects']=='Connectivity']
    #3. Draw the line
    if not df_aspect.empty:
     fig20, ax20 = plt.subplots(figsize=(12, 6))
        
    sns.lineplot(data=df_aspect, x='Device Name', y='Polarity', marker='o', ax=ax20)
    plt.xticks(rotation=45)#Help if device names are long
    ax20.set_title('Users Sentiment towards Connectivity for each Device',fontsize=15)
    
    st.pyplot(fig20)

#==============================================================

with st.expander("Smart assistant"):
    #1. Convert text to numbers (polarity )
    Sentiment_map = {'Positive':1,'Neutral':0,'Negative':-1}
    # Mapping the sentiment and ensuring the result is numric
    df_cleaned.loc[:,'Polarity']=df_cleaned['Sentiment'].map(Sentiment_map)
    #Pick your asspect
    #Ensure df_aspect is an independent copy
    
    df_aspect=df_cleaned[df_cleaned['Aspects']=='Smart assistant']
    #3. Draw the line
    if not df_aspect.empty:
     fig30, ax30 = plt.subplots(figsize=(12, 6))
        
    sns.lineplot(data=df_aspect, x='Device Name', y='Polarity', marker='o', ax=ax30)
    plt.xticks(rotation=45)#Help if device names are long
    ax30.set_title('Users Sentiment towards Smart assistant for each Device',fontsize=15)
    
    st.pyplot(fig30)

#==============================================================

with st.expander("Configuration"):
    #1. Convert text to numbers (polarity )
    Sentiment_map = {'Positive':1,'Neutral':0,'Negative':-1}
    # Mapping the sentiment and ensuring the result is numric
    df_cleaned.loc[:,'Polarity']=df_cleaned['Sentiment'].map(Sentiment_map)
    #Pick your asspect
    #Ensure df_aspect is an independent copy
    df_aspect=df_cleaned[df_cleaned['Aspects']=='Configuration']
    #3. Draw the line
    if not df_aspect.empty:
     fig40, ax40 = plt.subplots(figsize=(12, 6))
        
    sns.lineplot(data=df_aspect, x='Device Name', y='Polarity', marker='o', ax=ax40)
    plt.xticks(rotation=45)#Help if device names are long
    ax40.set_title('Users Sentiment towards Configurationt for each Device',fontsize=15)
    
    st.pyplot(fig40)


#===================================================================================

   












data = {
    "Company": ["company"]*6,
    "Sentiment": ["Positive"]*3 + ["Negative"]*3,
    "Aspect": ["Clock", "Smart Assistant", "Sound", "Connectivity", "Clock", "Smart Assistant"]
}
df = pd.DataFrame(data)

st.title("Top Aspects")


company = df['Company'].unique()[0]
df_c = df[df['Company'] == company]


top_pos = df_c[df_c['Sentiment']=="Positive"]['Aspect'].value_counts().head(3)
top_neg = df_c[df_c['Sentiment']=="Negative"]['Aspect'].value_counts().head(3)


top_pos_list = top_pos.index.tolist() + [""]*(3 - len(top_pos))
top_neg_list = top_neg.index.tolist() + [""]*(3 - len(top_neg))


table_df = pd.DataFrame({
    "Top Positive Aspects": top_pos_list,
    "Top Negative Aspects": top_neg_list
})

#st.subheader(f"Company: {company}")
st.table(table_df)





st.title("**Recommendations :**")
st.write("Developers should give priority to focusing on improving connectivity of devices.")
st.write("Developers should pay attention to improving & solving the problems that users are facing.")
st.write("It is important to enhance product quality and reliability to reduce negative customer feedback.")
st.write(" The company should focus on improving devices with high negative reviews, especially those with frequent complaints about performance and connectivity.")
st.write("The company should maintain and promote devices with high positive sentiment, as they reflect strong customer satisfaction.")
st.write("Developers should pay close attention to common negative aspects and work on fixing user-reported issues.")
st.write("improving weak devices while maintaining strong-performing ones will help increase overall customer satisfaction.")
st.write("Continue enhancing the most frequently mentioned positive aspects.")
st.write("Apply device-specific improvements instead of one solution for all products.")
st.write("Companies should focus on using AI to improve ideas and reach people better.")








st.title("CONNECT WITH US:")


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("[⬛ Roaa Ehab ](https://www.linkedin.com/in/roaa-ehab-wagih-717102379?utm_source=share_via&utm_content=profile&utm_medium=member_android)")
    st.markdown("[⬛ Jana Sherif ](https://www.linkedin.com/in/janasherifhathout)")

with col2:
    st.markdown("[⬛ Halima Mohamed](https://www.linkedin.com/in/halima-mohamed-3570593b3?utm_source=share_via&utm_content=profile&utm_medium=member_android)")
    st.markdown("[⬛ Mariam Ahmed ](https://www.linkedin.com/in/mariam-ahmed-kareem-1ab6b63b2?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)")

with col3:
    st.markdown("[⬛ Yossra Mohamed](https://www.linkedin.com/in/yossra-mohamed-6b0a133b2)")
    st.markdown("[⬛ Mariam Amr](https://www.linkedin.com/in/mariam-amr-abdelsalam-9772443ba)")









