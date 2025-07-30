# -*- coding: utf-8 -*-

import os
import datetime

from ChefsHatGym.KEF import LogManager
from ChefsHatGym.KEF import PlotManager
from ChefsHatGym.KEF import DataSetManager
from ChefsHatGym.KEF import MetricsManager


class ExperimentManager:
    """Experiment Manager Class

    This class manager the experiments. It creates all the folder structures, if necessary and create the log.


    Attributes:
        baseDirectory (String): Base directory of the experiment.
        experimentName (String): Name of the experiment.
        logManager (LogManager):


    Author: Pablo Barros
    Created on: 02.02.2017
    Last Update: 20.02.2017


    """

    @property
    def baseDirectory(self):
        return self._baseDirectory

    @property
    def experimentName(self):
        return self._experimentName

    @property
    def logManager(self):
        return self._logManager

    @property
    def dataSetManager(self):
        return self._dataSetManager

    @property
    def plotManager(self):
        return self._plotManager

    @property
    def metricManager(self):
        return self._metricManager

    @property
    def plotsDirectory(self):
        return self._plotsDirectory

    @property
    def modelDirectory(self):
        return self._modelDirectory

    @property
    def dataSet(self):
        return self._dataSetDirectory

    @property
    def outputsDirectory(self):
        return self._outputsDirectory

    def createLocalFolder(self, parentDirectory, name):
        self._createFolder(os.path.join(parentDirectory, name))

    def _createFolder(self, directoryName):
        """
        Private function that creates a new directory in the baseDirectory folder.
        It will ignore the command if the folder already exist.

        Args:
            folderName (String): the name of the new directory. If a nested directory, use the following notation: "folder1/folder1.1/folder1.1.1".

        """

        if not os.path.exists(
            os.path.join(self.baseDirectory, self.experimentName, directoryName)
        ):
            os.makedirs(
                os.path.join(self.baseDirectory, self.experimentName, directoryName)
            )

    def __init__(
        self,
        baseDirectory,
        experimentName,
        verbose=True,
        saveLog=False,
        save_dataset=False,
    ):
        """
        Function that creates a new experiment. A new folder structure will be created, with a new log file.

        Args:
            baseDirectory (String): the name of the basic directory.
            experimentName (String): the name of the experimentName, which will be updated to experimentName+date_of_the_creation.
            verbose(Boolean): Indicates if the log will also be printed in the console

        """

        assert (
            not baseDirectory == None or not baseDirectory == ""
        ), "Empty Base Directory!"
        assert (
            not experimentName == None or not experimentName == ""
        ), "Empty Experiment Name!"

        self._baseDirectory = baseDirectory
        self._experimentName = experimentName
        """Creating the dataset folder"""
        if save_dataset:
            self._dataSetDirectory = os.path.join(
                self.baseDirectory, self.experimentName, "Datasets"
            )
        else:
            self._dataSetDirectory = None

        self._dataSetManager = DataSetManager.DataSetManager(
            self._dataSetDirectory,
        )
        self._createFolder("Datasets")

        """Creating the log folder"""
        self._createFolder("Log")
        self._logManager = LogManager.Logger(
            os.path.join(self.baseDirectory, self.experimentName, "Log", "Log.log"),
            verbose=verbose,
            saveLog=saveLog,
            experimentName=str(datetime.datetime.now().timestamp()),
        )

        self._metricManager = MetricsManager.MetricsManager(
            os.path.join(self.baseDirectory, self.experimentName, "Log")
        )

        self.logManager.newLogSession("Experiment: " + self.experimentName)
        self.logManager.write(
            "Base Directory: " + os.path.join(self.baseDirectory, self.experimentName)
        )
