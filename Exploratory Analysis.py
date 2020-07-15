#!/usr/bin/env python
# coding: utf-8

# # Exploratory Analysis
# In between this notebook, and the first, I cleaned the data further in Excel since the dataset was small enough to begin with. First, I combined the various LGBT related biases into one as 'Anti-LGBT'. I also, cleaned up some other biases to make the entire column uniform as possible. Second, I cleaned the offender ethnicity column for the same reason. The resulting dataset lists 56 separate alleged hate crimes, in Austin, TX, since 2017. 
# 
# Out of the total number of reported, alleged incidents, 32.14% were directed at the LGBT Community. 

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')


# In[2]:


# Importing & examining the cleaned dataset
df = pd.read_csv(r'C:\Users\Robert\OneDrive\Desktop\datasets\aus_final.csv')
display(df.shape)
print('----------------------------------')
display(df.head())
print('----------------------------------')
display(df.tail())
print('----------------------------------')
display(df.columns)
print('----------------------------------')
display(df.index)
print('----------------------------------')
display(df.describe())
print('----------------------------------')
display(df.dtypes)


# In[3]:


# Creating an index out of the 'date' column annd converting the non-numeric columns into categories
df['date_of_incident'] = df['date_of_incident'].astype('datetime64')
df.set_index(['date_of_incident'], inplace=True)
df['bias'] = df['bias'].astype('category')
df['offense'] = df['offense'].astype('category')
df['offense_location'] = df['offense_location'].astype('category')
df['offender_ethnicity'] = df['offender_ethnicity'].astype('category')

# Reexamining the dataset
display(df.index)
print('----------------------------------')
display(df.dtypes)


# ### Question 1. How are reported incidences in Austin distributed according to motivation? 

# In[4]:


# Creating a dataframe of the biases
bias = df['bias'].value_counts()
display(bias)

bias_pct = df['bias'].value_counts(normalize=True)

# Displaying the bias values as proportions
print('----------------------------------')
display(df['bias'].value_counts(normalize=True))

# colors = ['blue', 'red', 'yellow', 'cyan', 'green', 'orange', 'cyan', 'blue', 'yellow']

# Visualizing the bias dataframe
bias.plot.bar(figsize=(15,8))
plt.ylabel('Total Crimes since 2017')
plt.title('Distribution of Bias')
plt.show()

# Visualizing bias values as proportions
bias_pct.plot.pie(figsize=(9,9))
plt.title('Distribution of Bias')
plt.show()


# ### Question 2. How are hate crimes perpetuated? 

# In[6]:


# Create a dataframe for the offense values
offense_count = df.offense.value_counts()
display(offense_count)

# Displaying the offense values as proportions
print('----------------------------------')
offense_count_pct = df.offense.value_counts(normalize=True)
display(offense_count_pct)


# Visualizing the offense values
offense_count.plot.bar(figsize=(15,8))
plt.ylabel('Total Crimes since 2017')
plt.title('Distribution of Offenses')
plt.show()


# ### Question 3. What is the race/ethnicity of the offenders?      

# In[7]:


# Create a dataframe for the offender ethnicity values
offenders_count = df['offender_ethnicity'].value_counts()
display(offenders_count)
print('----------------------------------')

# Displaying the offender ethnicity values as proportions
offenders_count_pct = df.offender_ethnicity.value_counts(normalize=True)
display(offenders_count_pct)

# Visualizing the offender ethnicity values
offenders_count.plot.bar(figsize=(15,8))
plt.ylabel('Total Crimes since 2017')
plt.title('Offender Race/Ethnicity')
plt.show()


# Note...the above 'Offender' graph has an instance of 'Hispanic (2), Caucasian (2)' as a single column because of an incident that occurred on 1/19/19 https://www.statesman.com/news/20200124/confrontation-that-ignited-attack-on-austin-gay-couple-questioned-by-detective -- 2 of the offenders were white, and the other 2 were hispanic. 

# ### Question 4. Where in Austin do hate crimes often take place? 

# In[8]:


# Displaying 'offense location'
location = df.offense_location.value_counts()
display(location)
print('----------------------------------')

# Displaying 'offense location' as proportions
location_pct = df.offense_location.value_counts(normalize=True)
display(location_pct)

location.plot.bar(figsize=(15,8))
plt.ylabel('Total Crimes since 2017')
plt.title('Crime Locations')
plt.show()


# As a final look, let's examine the correlations between victims and offenders. 

# In[9]:


# Examining correlations between victims & offenders
df_corr = df.corr()

display(df_corr)
df_corr.plot.bar(figsize=(15,8))
plt.show()

