import pandas as pd
import numpy as np

class infoGain():

    def get_col(self):
        # returns column names 
        # if fIndex = True meaning if first col is index then remove from list 
        columns = list(self.data.columns)
        if self.fIndex == True:
            columns = columns[1:]

        # removing target column
        columns.remove(self.target)

        return columns

    def groupby(self,col):
        # Groups element based on unique elements
        # return a list of dataframes
        grouped = self.data.groupby(col)
        dfs = [group for _, group in grouped]
        return dfs
        

    def entropy(self, data):
        # calculates entropy for each class 
        total_count = data[self.target].value_counts().sum()

        # initialize entropy to 0
        ent = 0

        # getting every unique element in target class 
        # and calculating p for each output
        class_counts = data[self.target].value_counts()
        for count in class_counts:
            p = count / total_count
            if p > 0:
                ent -= p * np.log2(p)


        return ent
    
    def gini(self, data):
        # calculates gini for each class 
        total_count = data[self.target].value_counts().sum()

        # initialize gini to 0
        gini = 0

        # getting every unique element in target class 
        # and calculating p for each output
        class_counts = data[self.target].value_counts()
        p = []
        for count in class_counts:
            p_class = count / total_count
            p.append(p_class)
        
        gini = 1-(sum(x**2 for x in p))
                    
        return gini

    def calculate(self, data,target,criteria='gini',fIndex=True):

        # check if data provided is pandas dataframe 
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas dataframe")
        self.data=data

        # check if data's fIndex is a boolean
        if not isinstance(fIndex, bool):
            raise ValueError("fIndex must be a boolean")
        self.fIndex = fIndex

        # check if criteria is valid
        if criteria not in ['gini','entropy']:
            raise ValueError(f"Invalid criteria value, must be gini or entropy")
        self.criteria = criteria
        # check if target col in data
        if target not in data.columns:
            raise ValueError(f"Target column '{target}' not found in data")
        self.target = target


        # Get Columns name 
        columns = self.get_col()    

        # calculating impurity 
        total_impurity = self.entropy(self.data) if self.criteria == 'entropy' else self.gini(self.data)

        igList =[]

        for i in range(len(columns)):
            # calculates and returns a dictionary containing col & information gain 
            # selecting column 
            groups = self.groupby(columns[i])
            
            weighted_impurity = 0
            
            # calculating weighted entropy
            for group in groups:
                weight = group.shape[0] / self.data.shape[0]

                weighted_impurity += weight * self.entropy(group) if self.criteria == 'entropy' else weight * self.gini(group)

            #calculating info gain
            ig = total_impurity - weighted_impurity

            igList.append(ig)

        
        igList = [float(ig) for ig in igList]

        # Creating dictionary
        igDict = dict(zip(columns, igList))
        return igDict

