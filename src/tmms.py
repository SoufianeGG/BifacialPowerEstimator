import numpy  as np 
import pandas as pd 
import os  
import plotly as plt 
import plotly.express as px
import plotly.graph_objects as go
import bif_power

class TMMS:
    '''Class to run the calculation of the typical meteorological year 
    dataPath : Path of the weather dataset csv file 
    years : number of years from which we define the tmy 
    params : required parameters  
    '''
    def __init__(self, dataPath = None , years = None , params = None):  
        self.dataPath  = dataPath
        self.years  = years 
        self.params  = params 
        
    @classmethod 
    def solcast10y(cls, ): 
        '''10 years solcast data, the input file is located in the data directory'''
        dirPath = os.path.dirname(os.path.dirname(__file__))
        dataPath = os.path.join(dirPath, 'data\\tmyData.csv')
        params  = ['dni', 'dhi', 'albedo', 'temperature', 'snowDepth']
        return cls(dataPath, 10, params )
    
    
    def weightMonth(self,  month : int, param: str ) :
        '''
        Calculte the weight that corresponds to each month using the principal component analysis,
        the assigned weight is assumed equal to  ∑ a_i √λi (a_i is the loading, λ_i is the corresponding 
        eigen value of the month) this give is the month that has the most variance and most correlation. 
        
        Parameters  
        ----------
        data  : weather datafarame from Solcast
                Historical Data :  https://solcast.com/time-series
        years : number of years to conduct the dimentionality reduction technique  
                recommended at least 10 years.
        month : index of the month [1-12]
        param : name of the selected parameter  
        
        Returns
        -------
        explained_variance: variance of each month
        cumulative_variance: cumulative variance used to identify the threshold  
        weight_months  : ordered array of weights that correspond to each month 
        '''
        data =  pd.read_csv(self.dataPath)
        data  = bif_power.solcastData(data_file = self.dataPath)
        #params_df  = data[self.params]

        last_y = data.max().date.year  # avoid the recent year
        end_y  = last_y - self.years   
        # Dataframe generation 
        month0  = 'y'
        months_data  = pd.DataFrame()
        if month == 2 : 
            for i in range(0, self.years): 
                cmonth  = month0 + str(i)
                months_data[cmonth]  = data[(data.date.dt.month == month) & (data.date.dt.day <=28 ) & (data.date.dt.year == end_y +i)][param].values
        else :        
            for i in range(0,self.years): 
                cmonth  = month0 + str(i)
                months_data[cmonth]  = data[(data.date.dt.month == month) & (data.date.dt.year == end_y +i)][param].values
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
        weight_months  = np.empty(self.years)
        for i in range(self.years):
            weight_months[i] =  np.sum(np.sqrt(sorted_eigenvalues[:threshold[1]])*selected_pci[:, i:i+1])
        return  sorted_eigenvectors, explained_variance, weight_months 

    def selected_month(self, month : int ): 
        ''' 
        Parameters
        ----------
        month : index of the month 
        Returns
        -------
        month_index : year index of the selected month that has the maximum correlation & variance 
        '''
        param_matrix = np.empty([len(self.params), self.years])
        # remove the months with zeros values -> snowDepth 
        for param in self.params : 
            if (param == 'snowDepth') & (month in range(5,11 )): 
                weights = np.zeros(self.years)
                param_matrix[self.params.index(param)] = weights 
            else : 
                _ , _ , weights  = self.weightMonth(month, param)
                norm  = np.linalg.norm(weights)
                weights = 1/len(self.params)*weights/norm 
                param_matrix[self.params.index(param)] = weights
        total_weights = np.sum(param_matrix, axis = 0)
        month_index  =  np.argmax(total_weights) 
        return month_index
    
    @staticmethod
    def pareto_plot(explained_variance, show : bool, save : bool): 
        '''' Pareto plot of the given month 
        Paramters
        ---------
        explained_variance : array of the explained variance 
        show : show the figure   
        save : save the svg file
        
        Returns
        -------  
        Download the svg file of the pareto front 
        
        '''
        cumulative_variance  = np.cumsum(explained_variance)
        fig = px.line(template  ='plotly_white')
        fig.add_hline(y=80, line_dash  ='dot', annotation_text =  'Selection Criterion ( Cum σ  >  0.8)', line_color  = 'black', line_width  = 1,)
        fig.add_trace(go.Bar(name = 'explained variance',x= np.arange(1,11), y =explained_variance*100, marker_line_width=1, marker_color  ='#87CEEB', marker_line_color='black'
                            ))
        fig.add_scatter( name = 'cumulative_variance',x= np.arange(1,11), y  = np.round(cumulative_variance, 2) *100,line  = dict(color  = 'black'), 
                        text  = [str(round(x, 1))+"%"  for x in cumulative_variance*100] , textposition= "bottom center",  
                        textfont  = dict(family  = 'Calibri light', color  = 'black', size  = 16), mode  = 'lines+markers+text', )
        fig.update_layout(xaxis_title  ='Principal component index', yaxis_title  = 'Cumulative variance [%]', 
                        font_family  =  'Calibri light', font_size  = 18, font_color  = 'black',)    
        if show : fig.show()
        if save : plt.offline.plot(fig,image = 'svg', image_height=800,  image_width= 1400 )
