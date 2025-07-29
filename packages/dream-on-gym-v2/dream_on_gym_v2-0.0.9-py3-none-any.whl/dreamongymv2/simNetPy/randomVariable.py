# -*- coding: utf-8 -*-
"""
Created on Tue May 17 13:32:05 2022

@author: redno
"""
from numpy.random import Generator, MT19937
import numpy as np


class RandomVariable:

    def __init__(self, seed=1234567, parameter1=10):
        """Constructor
            Args:
                seed:  Default value: 1234567
                parameter1: Default value: 10
        """
        self.__generator = Generator(MT19937(seed))
        self.__parameter1 = parameter1
        self.__dist = self.__generator.uniform(0, 1.0)

    def getDist(self, generator):
        """getDist
            generator: Object that use MT19937 to generate a random variable
            Returns:
                Random Number
        """
        self.__dist = generator.uniform(0, 1.0)
        return self.__dist

    ''' '''
    @property
    def generator(self):
        return self.__generator
    
    @generator.setter
    def bitRate(self,seed):
        self.__generator = Generator(MT19937(seed))

    ''' '''
    @property
    def parameter1(self):
        return self.__parameter1
    
    @parameter1.setter
    def parameter1(self,paramenter):
        self.__parameter1 = paramenter

    ''' '''
    @property
    def dist(self):
        return self.__dist
    
    @dist.setter
    def dist(self,generator):
        self.__dist = generator.uniform(0, 1.0)    