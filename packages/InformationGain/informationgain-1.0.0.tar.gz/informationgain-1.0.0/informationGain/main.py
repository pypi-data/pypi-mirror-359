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

        # initialize entroy to 0
        ent = 0

        # getting every unique element in target class 
        # and calculating p for each output
        class_counts = data[self.target].value_counts()
        for count in class_counts:
            p = count / total_count
            if p > 0:
                ent -= p * np.log2(p)


        return ent

    def calculate(self, data,target,fIndex=True):

        # check if data provided is pandas dataframe 
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas dataframe")
        self.data=data

        # check if data's fIndex is a boolean
        if not isinstance(fIndex, bool):
            raise ValueError("fIndex must be a boolean")
        self.fIndex = fIndex

        # check if target col in data
        if target not in data.columns:
            raise ValueError(f"Target column '{target}' not found in data")
        self.target = target

        # Get Columns name 
        columns = self.get_col()    

        # grouping data in each column
        total_entropy = self.entropy(self.data)

        igList =[]

        for i in range(len(columns)):
            # calculates and returns a dictionary containing col & information gain 
            # selecting column 
            groups = self.groupby(columns[i])
            
            weighted_entropy = 0
            # calculating weighted entropy
            for group in groups:
                weight = group.shape[0] / self.data.shape[0]
                weighted_entropy += weight * self.entropy(group)
            #calculating info gain
            ig = total_entropy - weighted_entropy
            igList.append(ig)

        # Creating dictionary
        igList = [float(ig) for ig in igList]

        igDict = dict(zip(columns, igList))
        return igDict

