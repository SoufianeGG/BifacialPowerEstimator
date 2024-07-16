
import numpy as np 
import pandas as pd 
import bif_power
from tmms import TMMS 
tmms_data  = TMMS.solcast10y()
#! testing 
data =  pd.read_csv(tmms_data.dataPath)
data  = bif_power.solcastData(data_file = tmms_data.dataPath)
#params_df  = data[tmms_data.params]

last_y = data.max().date.year  # avoid the recent year
end_y  = last_y - tmms_data.years   
# Dataframe generation 
month0  = 'y'
months_data  = pd.DataFrame()
for i in range(0,tmms_data.years): 
    cmonth  = month0 + str(i)
    months_data[cmonth]  = data[(data.date.dt.month == 1) & (data.date.dt.year == end_y +i)]['temperature'].values
# Standirzation 
# Standirzation 
norm_data  =   (months_data - np.mean(months_data))/months_data.std()
# idea normalization of the dataset as we have the same variable 
covariance_matrix = np.cov(norm_data, ddof=0, rowvar=0)
eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
order_of_importance = np.argsort(eigenvalues)[::-1] 
sorted_eigenvalues = eigenvalues[order_of_importance]
sorted_eigenvectors = eigenvectors[:,order_of_importance] # sort the columns
explained_variance = sorted_eigenvalues / np.sum(sorted_eigenvalues)
cumulative_variance= np.cumsum(explained_variance)
threshold = [x[0] for x in enumerate(cumulative_variance) if x[1] >= 0.8 ] 
selected_pci  = sorted_eigenvectors[:threshold[1]]
weight_months  = np.empty(tmms_data.years)
param_matrix = np.empty([len(tmms_data.params), tmms_data.years])
# remove the months with zeros values -> snowDepth 
mlist  = np.zeros(10)
                          
for i in range(3, 13): 
    for param in tmms_data.params : 
        if (param == 'snowDepth') & (i in range(5,10 )): 
            weights = np.zeros(10)
            param_matrix[tmms_data.params.index(param)] = weights
        else : 
            _ , _ , weights  = tmms_data.weightMonth(i, param)
            norm  = np.linalg.norm(weights)
            weights = 1/len(tmms_data.params)*weights/norm 
            param_matrix[tmms_data.params.index(param)] = weights
    total_weights = np.sum(param_matrix, axis = 0)
    month_index  =  np.argmax(total_weights)
    mlist[i-3]= month_index

print(mlist)