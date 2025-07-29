# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:45:23 2022

@author: redno
"""

class Node:
    __id = -1
    __label = ""
    
    def __init__(self, id : int, label: str=""):
        """Constructor
            Args:
                id: Id for Node
                label: Is optional, the name of node.
        """
        self.__id = id
        self.__label = label
    
    def info(self):
        """
        Print the label of the node.
        """
        print(self.__id,self.__label)   

    ''' '''
    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self,id):
        self.__id = id

    ''' '''
    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self,label):
        self.__label = label 

    