import pandas as pd
import numpy as np
from collections import Counter

class infoGain():

    def getCol(self):
        # returns column names 
        # if fIndex = True meaning if first col is index then remove from list 
        columns = list(self.data.columns)
        if self.fIndex == True:
            columns = columns[1:]

        # removing target column
        columns.remove(self.target)

        return columns

    def groupData(self,col):
        # Groups element based on unique elements
        # return a list of dataframes
        grouped = self.data.groupby(col)
        dfs = [group for _, group in grouped]

        return dfs
        
    
    def clacEntropy1(self, data):
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
    
    def calcEntropy2(self, x):
        # calculates entropy for continious variable
        if isinstance(x, pd.DataFrame):
            x = x[self.target]
        total = len(x)
        counts = Counter(x)

        return -sum((count/total) * np.log2(count/total) for count in counts.values())

    
    def calcGini1(self, data):
        # Gini for categorical variables
        # calculatcalcGs g1ini for each class 
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
        
        return 1-(sum(x**2 for x in p))
                    
    def calcGini2(self, x):
        # calculates Gini for continious variables
        if isinstance(x, pd.DataFrame):
            x = x[self.target]
        total = len(x)
        counts = Counter(x)

        return 1 - sum((count/total) ** 2 for count in counts.values())
       

    def calculate(self, data,target,criteria='gini',fIndex=True):

        # check if data provided is pandas dataframe 
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas dataframe")
        self.data=data
        
        # check if target col in data
        if target not in data.columns:
            raise ValueError(f"Target column '{target}' not found in data")
        self.target = target

        # check if criteria is valid
        if criteria not in ['gini','entropy']:
            raise ValueError(f"Invalid criteria value, must be gini or entropy")
        self.criteria = criteria

        # check if data's fIndex is a boolean
        if not isinstance(fIndex, bool):
            raise ValueError("fIndex must be a boolean")
        self.fIndex = fIndex

        # Get Columns name 
        columns = self.getCol()  

        result = pd.DataFrame(columns=['feature', 'threshold', 'infogain'])
                  
        for col in columns:
                
            # It's either int or float
            if np.issubdtype(self.data[col].dtype, np.number):
                # PROCESSING CONTINOUS VARIABLE

                # calculating total target impurity
                totalImpurity = self.calcEntropy2(dataByCol) if self.criteria =='entropy' else self.calcGini2(dataByCol)

                # Taking out col and target   
                dataByCol = data[[col, target]]
                
                # sorting by ascending order
                dataByCol = dataByCol.sort_values(by=col, ascending=True)

                # getting every unique value
                unique_values = dataByCol[col].unique()

                # initializing a impuriity dictionary
                impurityDict = {} 
                # calculating information gain for each unique value
                for value in unique_values:

                    infoGain=0
                    # splitting data into left and right group
                    leftGroup = dataByCol[dataByCol[col]<= value][self.target]
                    rightGroup = dataByCol[dataByCol[col] > value][self.target]
                    
                    total = len(dataByCol)

                    # if any group has no element skip iteration
                    if len(leftGroup) == 0 or len(rightGroup) == 0:
                        continue
                    
                    # checking criteria
                    if self.criteria == 'entropy':
                        leftImpurity = self.calcEntropy2(leftGroup)
                        rightImpurity = self.calcEntropy2(rightGroup)

                    else:
                        leftImpurity = self.calcGini2(leftGroup)
                        rightImpurity = self.calcGini2(rightGroup)

                    # calculating weighted impurity
                    weightedImpurity = (len(leftGroup)/total) * leftImpurity + (len(rightGroup)/total) * rightImpurity

                    # calculating information gain
                    infoGain = totalImpurity - weightedImpurity

                    # storing innformation gain in dict
                    impurityDict[value] = infoGain


                # storing the maximum value of information gain with its threshold and column name in dataset
                if impurityDict:  # only proceed if impurityDict is not empty
                    bestThreshold = max(impurityDict, key=impurityDict.get)
                    bestInfoGain = impurityDict[bestThreshold]
                    # storing the result in dataframe
                    result = pd.concat([result, pd.DataFrame([{
                        'feature': col,
                        'threshold': bestThreshold,
                        'infogain': bestInfoGain
                    }])], ignore_index=True)


            else:
                # PROCESSING CATEGORICAL VARIABLE

                # calculating total target impurity
                totalImpurity = self.clacEntropy1(self.data) if self.criteria == 'entropy' else self.calcGini1(self.data)
                # grouping data by classes
                groups = self.groupData(col)
                #initialize weighted impurity as 0
                weighted_impurity = 0

                # calculating weighted impurity
                for group in groups:
                    weight = group.shape[0] / self.data.shape[0]

                    weighted_impurity += (weight * self.clacEntropy1(group)) if self.criteria == 'entropy' else (weight * self.calcGini1(group))

                #calculating info gain
                ig = totalImpurity - weighted_impurity

                # storing the result in dataframe
                result = pd.concat([result, pd.DataFrame([{
                'feature': col,
                'threshold': 'none',
                'infogain': ig
                }])], ignore_index=True)

        return result