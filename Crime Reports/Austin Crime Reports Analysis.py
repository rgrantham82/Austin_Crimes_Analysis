#!/usr/bin/env python
# coding: utf-8

# # Analyzing Austin PD's Crime Reports Dataset
# 
# The dataset is available from the Austin Police Department on https://data.austintexas.gov/Public-Safety/Crime-Reports/fdj4-gpfu. It is updated weekly and I last downloaded the dataset on 8/10/2020.  
# 
# 
# 
# ## Table of Contents 
# 
#     I. Introduction
#     II. Data Scrubbing
#     III. Exploratory Analysis 
#     IV. Summary
#     
#     Questions:
# ><ul>
# ><li><a href="#q1"> 1. What areas of Austin have the highest crime rates?</a></li>
# ><li><a href="#q2"> 2. How is crime distributed in 78753?</a></li> 
# ><li><a href="#q3"> 3. How is crime distributed in 78741?</a></li>
# ><li><a href="#q4"> 4. How are violent crimes, in particular murder, capital murder, aggrivated assault, and rape distributed?
# ><li><a href="#q5"> 5. What significant does the family violence factor play, in violent crime, over time? 
# ><li><a href="#q6"> 6. How does murder appear on the map?
# </a></li>

# ## I. Introduction
# 
# I began reviewing the Crime Reports dataset, provided by the Austin PD, around the same time I began reviewing its Hate Crimes datasets for analysis, at the beginning of 2020. This is a rather large dataset, containing over 2 million records, spanning from 2003 to the present, and is update weekly. 
# 
# This is a self-paced project, conceived outside of both work and the educational arenas. It is my hope that this project will reveal some actionable insights that will benefit the Austin law enforcement community, news outlets, and anyone else interested in gaining knowledge on how best to combat the problem of crime in the Austin area.
# 
# I originally attempted importing the data into this notebook using Sodapy's Socrata API method but found it cumbersome. Mainly, it didn't want to work with importing the entire dataset, and added several redundant columns. I, therefore, prefer to manually download the entire dataset and re-download each week after it's updated.

# In[1]:


# Importing essential libraries and configurations
import mplleaflet as mpll
import contextily as cxt
import geopandas as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from shapely import speedups

get_ipython().magic('matplotlib inline')
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 
              None)

color = ['magenta', 'red', 'blue', 'yellow']


# In[2]:


plt.style.use('seaborn-dark-palette')


# In[3]:


# Loading the data
df = pd.read_csv('datasets\crime_reports.csv')


# In[4]:


# Examining the dataframe
display(df.info())
print('----------------------------------')
display(df.duplicated().sum())
print('----------------------------------')
display(df.isnull().sum())


# ## II. Data Scrubbing
# 
# There are several columns of data we won't be using in the analysis, mainly other date and geodata columns. So we'll drop those and also scrub some others. Mainly, we want the zip code and address columns to be free of nulls and duplicates. 
# 
# The Clearance Status column contains 3 types of statuses: Y for Yes, N for No, and O which stands for "cleared by other means than arrest." Therefore, I changed the column to bool with Y and O as True, and N as False. However, you may note that areas, where there is no clearance status at all, may or may not contain a corresponding date in the clearance date column. I am incompletely sure how best to handle this so I am open to suggestions or advice.   

# In[5]:


# Helper function for scrubbing the data
def clean_data(df):
    drop_col = ['Occurred Date Time', 
                'Occurred Time', 
                'Report Date', 
                'Report Time', 
                'Census Tract', 
                'UCR Category', 
                'Category Description', 
                'X-coordinate', 
                'Y-coordinate', 
                'Location']
    df.drop(drop_col, 
            axis=1, 
            inplace=True)
    clean_col = ['Zip Code', 
                 'Report Date Time',  
                 'PRA'] 
    df.dropna(subset=clean_col, 
              inplace=True)
    df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"), inplace=True)
    """Convert the following to bools"""
    d = {'Y': True, 
         'N': False}
    e = {'C': True, 
         'O': True, 
         'N': False}
    df.clearance_status = df.clearance_status.map(e)
    df.clearance_status = df.clearance_status.astype('bool')
    df.family_violence = df.family_violence.map(d)
    df.family_violence = df.family_violence.astype('bool') 
    """Convert the following to datetime type"""
    date_col = ['occurred_date', 
                'clearance_date', 
                'report_date_time'] 
    """Convert the following to category type"""
    cat_col = ['highest_offense_description', 
               'location_type', 
               'apd_sector'] 
    df[date_col] = df[date_col].astype('datetime64') 
    df[cat_col] = df[cat_col].astype('category') 
    """Convert the following to integer type"""
    int_col = ['zip_code', 
               'pra']
    df[int_col] = df[int_col].astype('int64')
    """Create a month column for later use in the analysis"""
    df['month'] = df['report_date_time'].dt.month
    """Set the index"""
    df.set_index(['report_date_time'], 
                 inplace=True)
    df.sort_index(inplace=True)
    return df
df = clean_data(df)


# In[6]:


# Rechecking the dataframe 
display(df.isnull().sum())
print('----------------------------------')
display(df.dtypes)
print('----------------------------------')
display(df.head())
print('----------------------------------')
display(df.tail())


# ## III. Exploratory Analysis

# <a id='q1'></a>
# ### A. Question 1. What areas of Austin have the highest crime rates? 
# 
# ***Note: I am only including zipcodes and crimes, for questions 1 - 3, that >= 1%. Any zipcodes or crime percentages, below 1%, will be discluded to simplify analysis and visualizations.***
# 
# Question 4 regards violent crime. For violent crime, I chose to examine 4 categories: aggrivated assault, rape, murder, and capital murder. I realize there are other types of violent crime, but for now I am sticking with these 4 categories. 

# In[7]:


figsize = [20,10]

# Create and show dataframe for crime rates by zipcode and then as percentages
zip_codes = df.zip_code.value_counts()
display(zip_codes)
print('----------------------------------')
display(df.zip_code.value_counts(normalize=True))


df.zip_code.value_counts().plot.bar(fontsize=14, 
                                    figsize=figsize,   
                                    rot=60)

plt.xlabel('Zip Code')
plt.ylabel('Total Crimes')
plt.title('Crime Rate by Zipcode')
plt.show()

zip_off_desc = pd.crosstab(df.zip_code, 
                           df.highest_offense_description)


# Out of all the areas in Austin, 78741 has the highest percentage of overall crime at 9.06%. This is a significant 1.3 percentage points higher than the number 2 area 78753 which hosts 7.8% of overall crime.

# #### Taking a closer look at particular areas... 
# 
# Because 78753 is my resident zipcode, I chose to examine it first. 
# 
# Next, I'll examine 78741. 

# <a id='q2'></a>
# ### B. Question 2. How is crime distributed in 78753? 

# In[8]:


# Examining crime in the 78753 area
df_53 = df[df.zip_code == 78753]

# Create a dataframe for the top 10 crime categories in the zipcode
df_53_off = df_53.highest_offense_description.value_counts().head(22)

# Display the different crime values & then as percentages 
display(df_53_off)
print('----------------------------------')
display(df_53.highest_offense_description.value_counts(normalize=True).head(22))

df_53_off.plot.pie(figsize=(8,8))
plt.title('Crime Distribution (78753)')


# <a id='q3'></a>
# ### C. Question 3. How is crime distributed in 78741? 

# In[9]:


# Create a dataframe for crime in the 78741 area (the highest amount of crime of any Austin zip code)
df_41 = df[df.zip_code == 78741]

# Create a dataframe for the top 10 crime categories in the zipcode
df_41_off = df_41.highest_offense_description.value_counts().head(21)

# Display the different crime values & then as percentages 
display(df_41_off)
print('----------------------------------')
display(df_41.highest_offense_description.value_counts(normalize=True).head(21))

df_41_off.plot.pie(figsize=(8,8))
plt.title('Crime Distribution (78741)')


# <a id='q4'></a>
# ### D. Question 4. How are violent crimes, in particular murder, capital murder, aggrivated assault, and rape distributed? 

# ***The following line of code shows crime rates only >= 1% per zipcode.***

# In[10]:


df_viol = df.query('highest_offense_description == ["MURDER", "CAPITAL MURDER", "RAPE", "AGG ASSAULT"]') 
df_viol_mur = df.query('highest_offense_description == ["MURDER", "CAPITAL MURDER"]')
df_mur = df[df.highest_offense_description == 'MURDER']
df_mur_cap = df[df.highest_offense_description == 'CAPITAL MURDER']
df_agg_asslt = df[df.highest_offense_description == 'AGG ASSAULT']
df_rape = df[df.highest_offense_description == 'RAPE']

df_viol_zip = df_viol.zip_code.value_counts()

df_viol_zip.plot.bar(figsize=figsize, 
                     fontsize=16,  
                     rot=60)
plt.title('Violent Crime Distribution by Zipcode since 2003')
plt.show()

viol_freq = pd.crosstab(df_viol.zip_code, df_viol.highest_offense_description)
display(viol_freq)

viol_freq.plot.bar(stacked=True, 
                   figsize=figsize, 
                   color=color, 
                   fontsize=16,  
                   rot=60)
plt.title('Violent Crime Distribution by Zipcode and Type since 2003')
plt.show()

viol_mur_freq = pd.crosstab(df_viol_mur.zip_code, df_viol_mur.highest_offense_description)
#display(viol_mur_freq)

viol_mur_freq.plot.bar(stacked=True, 
                       figsize=figsize,
                       fontsize=16, 
                       color=color,  
                       rot=60)
plt.title('Murder Distribution by Zipcode and Type since 2003')
plt.show()


# <a id='q5'></a>
# ### E. Question 5. What significance has the family violence factor, in violent crime, played over time? 

# In[11]:


display(df_viol.family_violence.mean())

print('----------------------------------')
display(df_viol.groupby(df_viol.index.year).family_violence.mean())

hrly_fam_viol_occurrences = df_viol.groupby(df_viol.index.year).family_violence.mean()

fam_viol_avg = df_viol.groupby(df_viol.index.year).family_violence.mean()

fam_viol_avg.plot(rot=60, 
                  figsize=(10,6.25), 
                  fontsize=16)

plt.show()


# <a id='q6'></a>
# ### F. Question 6. How does murder appear on the map? 

# In[12]:


# Create a geodataframe from the df_mur dataframe
gdf_mur = gp.GeoDataFrame(df_mur, 
                          geometry=gp.points_from_xy(df_mur.longitude, 
                                                     df_mur.latitude))

# ...df_mur_cap...
gdf_mur_cap = gp.GeoDataFrame(df_mur_cap, 
                              geometry=gp.points_from_xy(df_mur_cap.longitude, 
                                                         df_mur_cap.latitude))


# In[13]:


gdf_mur.crs = {'init': 'epsg:3857'}
gdf_mur_cap.crs = {'init': 'epsg:3857'}


# In[14]:


# Plot geodataframes on the "map"
ax = gdf_mur.plot(label='Murder', 
                  figsize=(12,12),  
                  alpha=0.85, 
                  markersize=3)  
gdf_mur_cap.plot(label='Capital Murder', 
                 figsize=(12,12),  
                 alpha=1, 
                 markersize=15, 
                 ax=ax)
ax.legend()


# ## IV. Summary
# Needless to say, violent crimes go hand-in-hand with other violent crimes.
# 
# So far, 78753 and 78741 are the top hotspots for all sorts of crime in Austin, including violent crime.
# 
# For non-capital murder, 78741 comes in at number 1 with 10.91%. 
# 
# #### ***It is important to note that murder does not necessarily make the defendant(s) automatically eligible for the death penalty. Under Texas law, we distinguish capital murder, through the motives and actions of the defendant(s) during the commission of a homicide, as whether or not automatically warranting an eventual date with the executioner. This includes such things as if the homicide was premeditated or not, if the defendant(s) murdered a police officer, etc.***
# 
# Regarding capital murder, 78723 comes in to share the number one spot with 78753, with a rate of 13.92% each. The 78741 area drops to the number 3 spot, carrying 8.97%. So, if we're honest, 78753 actually is the number 1 hotspot for murder because it has played host to 40 non-capital murders and 11 capital murders in total, meaning it has hosted 11% of all murders. 78741, if we combine all murders, only accounts for 10.56% of the total since 2003. 
# 
# Next, 78741 climbs back to claim the number 1 spot for rape at 12.09% -- 3.43 percentage points higher than the number 2 spot 78753 carrying 8.66% which is quite a significant lead when you look at it on the graph!! Why does rape occur so much more often in this area than in others?
# 
# A peculiar outlier is zipcode 78731. Although violent crime frequency ranks amongst the lowest there, rape accounts for over 50% of violent crimes committed in that area. Why is that? 
# 
# Astonishingly the family violence factor played an ever increasing role over over time, in regards to violent crime. From 2003 to 2015, family violence increased by nearly 10 percentage points--meaning you were likely to be the victim of a family member, during the commission of a rape, aggrivated assault, murder, or capital murder, only 3.15% of the time in 2003. But by 2015, that same likelihood rose to 12.82%!
