#!/usr/bin/env python
# coding: utf-8

# # Exploratory Analysis - Ford Bike System

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import statsmodels.api as sm
import seaborn as sns


# In[2]:


#read bike data
df = pd.read_csv('../201904-fordgobike-tripdata.csv')


# In[3]:


#view data
df.head()


# In[4]:


#data size
df.shape


# In[5]:


df.columns


# In[6]:


#data types
df.dtypes


# # Exploratory Data Analysis

# Where are the bike stations located?

# In[7]:


#view start station groups
df.groupby(['start_station_id']).count().head()


# In[8]:


#find lat / long extremities given a dataframe
def geoBound(df,lat_name,lon_name):
    lonmax = df[lon_name].max()
    lonmin = df[lon_name].min()
    latmax = df[lat_name].max()
    latmin = df[lat_name].min()
    return lonmax,lonmin,latmax,latmin


# In[9]:


#look for anomalies
df.sort_values(by=['start_station_latitude'])[['start_station_latitude','start_station_longitude']].head()


# In[10]:


#drop anomalous value
df = df.drop([40680])


# In[11]:


bounds = geoBound (df,'start_station_latitude','start_station_longitude')
bounds


# In[12]:


# map of station - view of san francisco area
my_dpi=96
plt.figure(figsize=(1300/my_dpi, 900/my_dpi), dpi=my_dpi)

# Make the background map
#m=Basemap(llcrnrlon=bounds[1], llcrnrlat=bounds[3],urcrnrlon=bounds[0],urcrnrlat=bounds[2])
m=Basemap(llcrnrlon=-135, llcrnrlat=50,urcrnrlon=-110,urcrnrlat=25)
m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
m.fillcontinents(color='#ffa07a', alpha=0.3)
m.drawcoastlines(linewidth=0.1, color="steelblue")
m.drawstates(color='white')

# Add a point per position
m.scatter(df['start_station_longitude'], df['start_station_latitude'], s=10, alpha=0.5, c = 'black',zorder=2)
plt.title('Bike Stations in Bay Area',fontsize=18)
plt.show()


# **Bikes stations in this data set are in northern california**

# In[13]:


# zoom in view of start stations
my_dpi=96
plt.figure(figsize=(1300/my_dpi, 900/my_dpi), dpi=my_dpi)

# Make the background map
m=Basemap(llcrnrlon=bounds[1], llcrnrlat=bounds[3],urcrnrlon=bounds[0],urcrnrlat=bounds[2])
m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
m.fillcontinents(color='#ffa07a', alpha=0.3)
m.drawcoastlines(linewidth=0.1, color="steelblue")
m.drawstates(color='white')

# Add a point per position
m.scatter(df['start_station_longitude'], df['start_station_latitude'], s=10, alpha=0.5, c = 'black',zorder=2)
plt.title('Bike Stations (Zoomed In)',fontsize=18)
plt.show()


# **Zoomed in view of bike stations**

# How many bikes are there?

# In[14]:


#find number of unique bike ids 
df['bike_id'].nunique()


# **There are 4520 unique bikes in this dataset**

# Which types of customers are using the bikes?

# In[15]:


#group data by user type to find number of customers vs subscribers
df.groupby('user_type')[['user_type']].size()


# In[16]:


#barplot of user types (ie no of customers vs subscribers for all observations)
users = df.groupby('user_type')[['user_type']].size().values
index = ('Customer','Subscriber')
y_pos = np.arange(len(index))
plt.bar(y_pos, users)
plt.xticks(y_pos, index)
plt.title('User Type')
plt.xlabel('Type')
plt.ylabel('Count')
plt.show()


# **35914 trips were taken by customers, 203196 trips were taken by subscribers**

# Do men or women ride the bikes more?

# In[17]:


#group observations by gender
df.groupby('member_gender')[['member_gender']].size()


# In[18]:


#barplot of observations by gender
genders = df.groupby('member_gender')[['member_gender']].size().values
index = ('Female','Male','Other')
y_pos = np.arange(len(index))
plt.bar(y_pos, genders)
plt.xticks(y_pos, index)
plt.title('Genders')
plt.xlabel('Gender')
plt.ylabel('Count')
plt.show()


# **55498 trips were taken by females, 168139 trips were taken by males, and 4274 trips were taken by other**

# In general which linear variables affect trip duration?

# In[19]:


#create an intercept for a linear regresssion
df['intercept'] = 1


# In[20]:


#drop missing value for linear regression
df2 = df.copy()
df2 = df2.dropna()
#linear regression with linear variables 
X = df2[['start_station_latitude','start_station_longitude','end_station_id','end_station_latitude','end_station_longitude','bike_id','member_birth_year','intercept']]
Y = df2[['duration_sec']]
model = sm.OLS(Y,X.astype(float)).fit()


# In[21]:


#low r squared, so only .5% of variation in y can be explained by the model. yikes
model.summary()


# **Really weak r squared. 0.5% of the variation in trip duration can be explained by the model**

# In[22]:


df2 = df2.drop('intercept',axis=1)


# In[23]:


corr = df2.corr()
corr


# In[24]:


# Correlation Matrix Heatmap
f, ax = plt.subplots(figsize=(10, 6))
hm = sns.heatmap(round(corr,2), annot=True, ax=ax, cmap="coolwarm",fmt='.2f',linewidths=.05)
f.subplots_adjust(top=0.93)
t= f.suptitle('Bike Rides Correlation Heatmap', fontsize=14)


# Duration is not strongly correlated with any variable 

# How does user type affect trip duration?

# In[25]:


#ride durations for customers, subscribers separately
customers = df[df['user_type']=='Customer'][['duration_sec']].values
subscribers = df[df['user_type']=='Subscriber'][['duration_sec']].values
data_to_plot = [customers, subscribers]


# In[26]:


#create box plots to compare trip durations between customers and subscribers
fig = plt.figure(1, figsize=(9, 6))
ax = fig.add_subplot(111)
bp = ax.boxplot(data_to_plot,showfliers=False)
ax.set_xticklabels(['Customers', 'Subscribers'])
plt.title('Trip Durations by User Type')
plt.xlabel('User Type')
plt.ylabel('Seconds')


# In[27]:


#trip duration quartiles for customers 
df[df['user_type']=='Customer'][['duration_sec']].describe()


# In[28]:


#trip duration quartiles for subscribers
df[df['user_type']=='Subscriber'][['duration_sec']].describe()


# **Customers have median trip duration of 879 seconds, subscribers have median duration of 521 seconds. THere is more variation in customer trip duration**

# How does gender affect trip duration?

# In[29]:


#trip durations for females, males, and other separately
female = df[df['member_gender']=='Female'][['duration_sec']].values
male = df[df['member_gender']=='Male'][['duration_sec']].values
other = df[df['member_gender']=='Other'][['duration_sec']].values
data_to_plot = [female, male, other]


# In[30]:


#create box plots to compare trip durations by gender 
fig = plt.figure(1, figsize=(9, 6))
ax = fig.add_subplot(111)
bp = ax.boxplot(data_to_plot,showfliers=False)
ax.set_xticklabels(['Female', 'Male','Other'])
plt.title('Trip Durations by Gender')
plt.xlabel('Gender')
plt.ylabel('Seconds')


# In[31]:


#trip duration quartiles for females
df[df['member_gender']=='Female'][['duration_sec']].describe()


# In[32]:


#trip duration quartile for males
df[df['member_gender']=='Male'][['duration_sec']].describe()


# In[33]:


#trip duration quartile for other
df[df['member_gender']=='Other'][['duration_sec']].describe()


# **Females have median trip duration of 623 seconds, males have median duration of 532 seconds, and other have median duration of 586 seconds. The three distributions are fairly similar**

# What is the relationship between age (birth year) and trip duration?

# In[34]:


#scatter birth year vs trip duration
plt.scatter(df['member_birth_year'],df['duration_sec'])
plt.title('Birth Year vs Trip Duration')
plt.xlabel('Year')
plt.ylabel('Seconds');


# No clear linear trend, but older people dont take long trips. More variation in younger riders.

# What is the age distribution of riders?

# In[35]:


df['member_birth_year'].hist()
plt.xlabel('Year')
plt.ylabel('Count')
plt.title('Age Distribution of Riders');


# # Summary of Main Findings

# The goal of this analysis was to have a high level understanding and overview of the Ford Go Bike System. In order to have the most current view of the company, the April 2019 dataset was pulled from this site https://s3.amazonaws.com/fordgobike-data/index.html .

# After scanning the data, I was interested in exploring the following two topics: 
# 
# 1. Where are the bikes located and how many are there?
# 2. Who is using the bikes and how often?

# During the data cleaning process, I reviewed data types, dropped anomalous values, and dropped NaN line items when necessary. I then used maps, bar charts, and box plots from the matplotlib library to visualize my data.

# My analysis yeiled the following findings:
# - Bike stations are in Northern California (San Jose area).
# - There are 4520 unique bikes. 
# - More trips are taken by subscribers than by customers. (203196 by subscribers, 35914 by customers)
# - More trips are taken by men than by women and other. (55498 by females, 168139 males, and 4274 by other)
# - One-time customers take longer trips than regular subscribers. (Customers median trip is 879 sec, subscribers median trip is 521 sec)
# - Females trips are longer than male or other trips. Female median is 623 sec, male median is 532 sec, and other median is 586)
# - No continuous variable is strongly correlated with trip duration. 
# - Older people dont take long trips, there is more variation in younger generation. 
# - There are more young riders than older riders.

# Note that the numbered bullets are included in the explanatory analysis. The duplicated numbering indicates that multiple findings are on the same slide. 

# In[ ]:




