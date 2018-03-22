
# coding: utf-8

# # Analyzing Fundraising Effectiveness
# ### Data from Kaggle Challenge *Funding and Organization Mission*

# In[116]:

get_ipython().magic(u'reset')


# In[137]:

import os
import json
import pandas as pd
import numpy as np
import datetime as dt
from datetime import date
import requests
import io
import csv
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go
from plotly import tools
import matplotlib as plt
import seaborn as sns


# ### Define data preparation functions

# In[118]:

# function to open, read in, and convert text file to pandas dataframe
def txt_opener(filename,delim):
    frame = []
    with open(filename,'r') as f:
        rows = (line.replace('\n','').split(delim) for line in f)
        frame = pd.DataFrame(rows)
        frame.columns = frame.iloc[0]
        frame = frame[1:]
        
    return frame    

def get_zip_code_data():
    # get FIPS codes for zips
    zip_to_county = requests.get('http://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt').text
    
    #iterate through file and create fips dataframe
    rows = zip_to_county.split('\n')
    frame = []
    for r in range(0,len(rows)):
        row = rows[r].split(',')
        map(lambda x: x.replace('\n',''),row)
        frame.append(row)
    frame = pd.DataFrame(frame)
    fips = frame
    fips.columns = fips.iloc[0].apply(lambda x: str(x).lower())
    fips = fips.drop(fips.index[0])
    
    return fips
    
def join_data(left,right):
    
    # join datasets
    zframe = pd.merge(left,right,how='left',left_on='zip',right_on='zcta5')
    
    # change data type for numeric analysis fields
    zframe.amount = zframe.amount.astype('float')
    zframe.donated = zframe.donated.astype('float')
    
    # get state abbreviation data
    states = requests.get('https://www2.census.gov/geo/docs/reference/state.txt').text.split('\n')

    # store state abbreviation data as a dictionary
    state_dict = {}
    for state in states:
        key = str(state[0:2])
        val = str(state[3:5])
        state_dict[key] = val
    
    # map state abbreviation to each row of data
    zframe['state_alpha'] = zframe['state'].map(state_dict)
    
    return zframe


# ### Define data analysis and visualization functions

# In[140]:

#def set_style():
    
    # set colorscale
    
def group_by_state(data):
    
    # group donation data by state; aggregate total donated and avg donation
    states = data.groupby('state_alpha').agg({'amount':['sum','mean'],'donated':['sum','count']})
    states['donors per thousand prospects'] = states['donated']['sum']/states['donated']['count']
    top = states.index[0:3]
    
    return top, states
    
def prospects_and_donors_choropleth(states,style=None):
    
    # define data and layout for prospects per state choropleth
    prospect_data = [dict(
         type='choropleth',
         locations = states.index,
         z = states['donated']['count'],
         locationmode = 'USA-states'
     )]
    
    prospect_layout = dict(
        title = 'Number of Prospects by State',
        geo = dict(
            scope='usa',
            projection=dict(type='albers usa')
        )
    )

    # return prospects per state choropleth
    trace1 = dict(data=prospect_data, layout=prospect_layout)

    # define data and layout for donors per thousand prospects choropleth
    donor_data = [dict(
         type='choropleth',
         locations = states.index,
         z = states['donors per thousand prospects'],
         locationmode = 'USA-states'
     )]
    
    donor_layout = dict(
        title = 'Donors per Thousand Prospects',
        geo = dict(
            scope='usa',
            projection=dict(type='albers usa')
        )
    )
    
    # return donors per thousand prospects choropleth
    trace2 = dict(data=donor_data, layout=donor_layout)
    
    # return figs
    return trace1, trace2

def average_donation_histogram(data):

    donation_histogram = [go.Histogram(data.amount)]
    
    return donation_histogram
    
def average_donation_by_phase(data):
    
    frames = []
    
    for p in dat.phase.unique():
        f = dat[dat.phase==p]
        frames.append(f)

    traces = list(map(lambda x: 'trace' + str(x),frames))

    plots = {}

    for t in range(0,len(traces)):
        key = traces[t]
        val = go.Histogram(frames[t]['amount'],opacity=.75)
        
#def top_states_choropleth(top,style=None):
    # group donation data in top 3 best performing counties by county; aggregate total donated and avg donation


# ### Define init functions

# In[152]:

def __init_prep__(path):
    left = txt_opener(path,delim=',')
    right = get_zip_code_data()
    try:
        dat = join_data(left=left,right=right)
        return dat
    except ValueError as e:
        print("Could not join zipcodes to data; here's the sample on its own")
        print(e)
        return left

def __init_viz__(data):
    top, states = group_by_state(data)
    prospect_fig, donor_fig = prospects_and_donors_choropleth(states=states)
    #hist_fig = average_donation_histogram(data=data)
    return prospect_fig, donor_fig


# ### Function call

# In[123]:

data = __init_prep__(path='competitions/Raising-Money-to-Fund-an-Organizational-Mission/training_sample.txt')


# In[156]:

prospect_fig, donor_fig = __init_viz__(data=data)


# In[157]:

py.iplot(prospect_fig, filename='fundraising_data_choropleth')


# In[155]:

py.iplot(donor_fig, filename='fundraising_data_choropleth')

