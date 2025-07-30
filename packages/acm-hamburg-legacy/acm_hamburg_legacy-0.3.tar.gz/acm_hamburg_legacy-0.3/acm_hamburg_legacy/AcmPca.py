"""
AcmPca

.. moduleauthor:: Conrad Stork <stork@zbh.uni-hamburg.de> and Anke Wilm <wilm@zbh.uni-hamburg.de>

"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from adjustText import adjust_text


class AcmPca:
    """
    Class with a workflow for building a scikit-learn PCA with scaled or unscaled features. Ideal for building 2D scatter Plots of different data sets to see chemical space overlaps and distributions. Can also build loading plot for selected features.

    :param allData: numpy array of all data
    :param y: array (same length like allData) contains the data set number of data point in allData
    :param numberOfDatasets: number of data sets
    :param labels: names of the data sets
    :param descriptorNamesList: List of descriptor names. Needed for descriptor importance calculation. If None the descriptors will be numbered
    :param pca: sklearn PCA object fitted with allData
    :param importanceOfDescriptors: pandasDataFrame with information of importance, names and distance to origin for the descriptors
    """

    def __init__(
        self, dataset, y, labels, scaled=True, descriptorNamesList=None, components=2
    ):
        """
        Constructor of AcmPca, should be called by classmethods see "@classmethod".

        :param dataset: Data sets for initializing the PCA as numpy array
        :param y: Dataset identifiers (number of dataset) as numpy array
        :param labels: Labels of the data sets in same order as datasets
        :param scaled: scales the feature before training default = True
        :param descriptorNamesList: list of names of descriptors in same order like datasets
        :param components: number of components that should be build
        """
        if not len(dataset) == len(y):
            raise TypeError("length of dataset and y are not the same")
        self.allData = dataset
        self.y = y
        self.numberOfDatasets = len(set(y))
        if not len(labels) == self.numberOfDatasets:
            raise TypeError("the number of data sets is not the same as labels")
        self.labels = labels
        if not descriptorNamesList:
            self.descriptorNamesList = []
            for i in range(len(dataset[0])):
                self.descriptorNamesList.append(str(i))
        elif descriptorNamesList:
            self.descriptorNamesList = descriptorNamesList
        if not len(descriptorNamesList) == len(dataset[0]):
            raise TypeError(
                "length of descriptorNamesList is not the same as descriptors"
            )

        # Scale the data
        if scaled:
            scaler = StandardScaler()
            self.allData = scaler.fit_transform(self.allData)
        # Build PCA
        self.pca = PCA(n_components=components, random_state=42)
        self.pca.fit(self.allData)
        self.importanceOfDescriptors = self._calculate_importance_of_descripts()

    @classmethod
    def init_with_list(cls, datasets, labels, scaled=True, descriptorNamesList=None):
        """
        Constructor for init the AcmPca from lists

        :param datasets: List of list of data sets
        :param labels: names of the data sets
        :param scaled: scales the features before training default = true
        :param descriptorNamesList: Names of the descriptors default = None (numbering the descriptors starting with 0)
        :returns: An initialized AcmPca
        """
        allData = []
        y = []
        yCnt = 0
        for dataset in datasets:
            for d in dataset:
                y.append(yCnt)
            yCnt += 1
            allData += dataset
        allData = np.array(allData, dtype=float)
        y = np.array(y)
        return cls(allData, y, labels, scaled, descriptorNamesList)

    @classmethod
    def init_with_pandas(cls, dataFrame, labelKey, scaled=True):
        """
        Constructor for init the AcmPca from Pandas.

        :param dataFrame: pandas DataFrame that includes columns for each descriptor and one column with the identifier of the data sets
        :param labelKey: name of column that contains the identifiers
        :param scaled: scales the features before training default = true
        :returns: An initialized AcmPca
        """
        allData = np.array(dataFrame.drop([labelKey], axis=1).values)
        names = np.array(dataFrame[labelKey].values)
        descriptorNamesList = list(dataFrame.drop([labelKey], axis=1))
        labels = []
        allLabels = dataFrame[labelKey]
        yCnt = 0
        labelInt = dict()
        for l in allLabels:
            if not l in labels:
                labels.append(l)
                labelInt[l] = yCnt
                yCnt += 1
        y = []
        for name in names:
            y.append(labelInt[name])
        return cls(allData, np.array(y), labels, scaled, descriptorNamesList)

    def pca_scatter(
        self,
        savePath=str(sys.path[0]) + "/",
        ratio_datapoints=1,
        colors=None,
        varianceOnAxis=True,
        components=(1, 2),
        legend=True,
    ):
        """
        Produces a scatter 2D Plot for the given PCA

        :param savepath: path and name for saving LoadingPlot.pdf default = pathOfRunningScript
        :param ratio_datapoints: ratio of datapoints that should be plotted default = 1
        :param colors: for the different data sets default = ('b',darkorange)
        :param varianceOnAxis: if the variance should be plotted on axis (default = True)
        :param components: which components should be plotted default = (1,2)
        :param legend: if a legend should be plotted default = True
        """
        components = self._sort_components(components)
        if not colors:
            colors = cm.rainbow(np.linspace(0, 1, self.numberOfDatasets))
        if len(colors) < self.numberOfDatasets:
            print(
                "You need at least as many colors like you have data sets.\n Terminating ..."
            )
            sys.exit()
        if ratio_datapoints > 1 or ratio_datapoints <= 0:
            print(
                "The ratio of datapoints has to be between 0 and 1.\n Terminating ..."
            )
            sys.exit()

        allData, y = self._select_allData_and_y_dependingon_ratio(ratio_datapoints)

        X = self.pca.transform(allData)
        var = self.pca.explained_variance_ratio_

        fig = plt.figure()
        ax = fig.add_subplot(111)

        com0 = components[0] - 1
        com1 = components[1] - 1
        for i in range(self.numberOfDatasets):
            ax.plot(
                X[y == i][:, com0],
                X[y == i][:, com1],
                marker=".",
                linestyle="",
                color=colors[i],
                label=self.labels[i],
            )

        if varianceOnAxis:
            ax.set_xlabel(
                "PC" + str(com0 + 1) + " (" + str(round(var[com0] * 100, 2)) + "%)"
            )
            ax.set_ylabel(
                "PC" + str(com1 + 1) + " (" + str(round(var[com1] * 100, 2)) + "%)"
            )
        else:
            ax.set_xlabel("PC" + str(com0 + 1))
            ax.set_ylabel("PC" + str(com1 + 1))
        if legend:
            ax.legend()
        fig.savefig(savePath + "Plot.pdf")

    def make_loading_plot(
        self,
        savePath=str(sys.path[0]) + "/",
        componentsToAnalyze=(1, 2),
        selectors=[],
        xAxisLim=None,
        yAxisLim=None,
    ):
        """
        Plots the loading plot after assignment importance by the give selectors (see Selectors below)

        :param savePath: path and name for saving LoadingPlot.pdf default = pathOfRunningScript
        :param componentsToAnalyze: principal components of interest default = (1,2)
        :param selectors: classes of selectors to select wished descriptors default = []
        :param xAxisLim: list containing minimal and maximal value for x-Axis
        :param yAxisLim: list containing minimal and maximal value for y-Axis
        """
        componentsToAnalyze = self._sort_components(componentsToAnalyze)
        importanceFrame = self.importanceOfDescriptors
        for s in selectors:
            importanceFrame = s(importanceFrame, componentsToAnalyze)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        texts = []
        for index, row in importanceFrame.iterrows():
            ax.plot(
                row["PC" + str(componentsToAnalyze[0])],
                row["PC" + str(componentsToAnalyze[1])],
                marker=".",
                linestyle="",
                color="black",
            )
            texts.append(
                plt.text(
                    row["PC" + str(componentsToAnalyze[0])],
                    row["PC" + str(componentsToAnalyze[1])],
                    row["descriptorName"],
                    size=8,
                )
            )
        adjust_text(
            texts,
            autoalign="y",
            only_move={"points": "y", "text": "xy"},
            force_points=0.15,
            arrowprops=dict(arrowstyle="->", color="r", lw=0.5),
        )
        if xAxisLim:
            plt.xlim(xAxisLim[0], xAxisLim[1])
        if yAxisLim:
            plt.ylim(yAxisLim[0], yAxisLim[1])
        ax.set_xlabel("PC" + str(componentsToAnalyze[0]))
        ax.set_ylabel("PC" + str(componentsToAnalyze[1]))
        fig.savefig(savePath + "LoadingPlot.pdf")

    def get_transformed_data(self, ratio_datapoints=1):
        """
        Function that returns the transformed data that would be plottet in the pca scatter plot normally

        :param: ratio_datapoints ratio of datapoints that should be plotted default = 1
        :return: np array with the transformed data
        """
        allData, y = self._select_allData_and_y_dependingon_ratio(ratio_datapoints)
        return self.pca.transform(allData)

    def _select_allData_and_y_dependingon_ratio(self, ratio_datapoints):
        """
        Function that selects data from the whole data set according to the ratio of data points that should be plotted or used for further output
        :param: ratio_datapoints ratio of datapoints that should be plotted
        """
        if ratio_datapoints == 1:
            allData = self.allData
            y = self.y
        else:
            eachNthDatapoint = 1 / ratio_datapoints
            allData = []
            y = []
            for i in range(self.numberOfDatasets):
                oneDataSet = self.allData[self.y == i]
                print(oneDataSet)
                np.random.seed(42)
                np.random.shuffle(oneDataSet)
                for ii, element in enumerate(oneDataSet):
                    if ii % eachNthDatapoint == 0:
                        allData.append(element)
                        y.append(i)
            allData = np.array(allData)
            y = np.array(y)
        return allData, y

    def _calculate_importance_of_descripts(self):
        """
        Function returns a data frame containing all importances of the different principal components, name of descriptors and distance to origin for each combination of the principal components. The resulting data frame can be used to select descriptors that should be plotted in the loading plot by the Selector classes

        :return: a data frame containing all importances of the different principal components, name of descriptors and distance to origin for each combination of the principal components.
        """
        components = self.pca.components_
        comp = len(components)
        if comp > 10:
            print(
                "WARNING: You use more than 10 components. The calculation could need a lot of time"
            )
        coeff = np.array(components).transpose()
        importanceFrame = pd.DataFrame([])
        importanceFrame["descriptorName"] = self.descriptorNamesList

        for pcCnt in range(comp):
            importanceFrame["PC" + str(pcCnt + 1)] = coeff[:, pcCnt]
            # calculate importance as distance to origin
            for pcOther in range(pcCnt):
                distList = []
                for i, value in enumerate(importanceFrame["PC" + str(pcCnt + 1)]):
                    dist = (
                        importanceFrame["PC" + str(pcOther + 1)][i] ** 2 + value**2
                    ) ** 0.5
                    distList.append(dist)
                importanceFrame[
                    "distanceToOriginOfPC" + str(pcOther + 1) + "AndPC" + str(pcCnt + 1)
                ] = distList
        return importanceFrame

    def _sort_components(self, components):
        """
        Function that checks if the components that are given are valid, correct length and in right order.

        :param components: components for checking
        :raise: Error if components are invalid
        :return: correct ordered components
        """
        if not len(components) == 2:
            raise TypeError("Lend of components has to be 2")
        if components[0] > components[1]:
            return (components[1], components[0])
        if components[0] == components[1]:
            raise TypeError("Components have to be different")
        return components


class SelectImportantDescriptsName:
    """
    Selector for selection of descriptors by Name
    """

    def __init__(self, descriptNames):
        """
        Constructor of SelectImportantDescriptsName

        :param descriptNames: list with names of descriptors that should be kept
        """
        if not type(descriptNames) == type(list()):
            raise TypeError("given parameter is not of type list")
        self.descriptNames = descriptNames

    def __call__(self, plotDataFrame, componentsToAnalyze):
        """
        Reduces the Data Frame by names.

        :param plotDataFrame: frame that should be filtered
        :return: reduced frame
        """
        reducedDataFrame = plotDataFrame[
            plotDataFrame["descriptorName"].isin(self.descriptNames)
        ]
        return reducedDataFrame


class SelectImportantDescriptsMinDist:
    """
    Selector for selection of descriptors by minimal distance to origin
    """

    def __init__(self, minDist):
        """
        Constructor of SelectImportantDescriptsMinDist

        :param minDist: int of float with minimal distance to origin that should be kept
        """
        if type(minDist) != type(int()) and type(minDist) != type(float()):
            raise TypeError("given parameter is not of type int or float")
        self.minDist = minDist

    def __call__(self, plotDataFrame, componentsToAnalyze):
        """
        Reduces the Data Frame by minDist.

        :param plotDataFrame: frame that should be filtered
        :return: reduced frame
        """
        reducedDataFrame = plotDataFrame[
            plotDataFrame[
                "distanceToOriginOfPC"
                + str(componentsToAnalyze[0])
                + "AndPC"
                + str(componentsToAnalyze[1])
            ]
            > self.inDist
        ]
        return reducedDataFrame


class SelectImportantDescriptsNumber:
    """
    Selector for selection of N descriptors with highest distance to origin
    """

    def __init__(self, number):
        """
        Constructor of SelectImportantDescriptsNumber

        :param number: int of descriptors most far away from origin that should be kept
        """
        if not type(number) == type(int()):
            raise TypeError("given parameter is not of type int")
        self.number = number

    def __call__(self, plotDataFrame, componentsToAnalyze):
        """
        Reduces the Data Frame by number.

        :param plotDataFrame: frame that should be filtered
        :return: reduced frame
        """
        plotDataFrameSorted = plotDataFrame.sort_values(
            "distanceToOriginOfPC"
            + str(componentsToAnalyze[0])
            + "AndPC"
            + str(componentsToAnalyze[1]),
            ascending=False,
        )
        reducedDataFrame = plotDataFrameSorted.head(self.number)
        return reducedDataFrame


class SelectImportantDescriptsFraction:
    """
    Selector for selection of fraction descriptors with highest distance to origin
    """

    def __init__(self, fraction):
        """
        Constructor of SelectImportantDescriptsFraction

        :param fraction: float of descriptors most far away from origin that should be kept
        """
        if not type(fraction) == type(float()):
            raise TypeError("given parameter is not of type float")
        self.fraction = fraction

    def __call__(self, plotDataFrame, componentsToAnalyze):
        """
        Reduces the Data Frame by fraction.

        :param plotDataFrame: frame that should be filtered
        :return: reduced frame
        """
        n_all = len(plotDataFrame.index)
        number = int(n_all * self.fraction)
        return SelectImportantDescriptsNumber(number)(
            plotDataFrame, componentsToAnalyze
        )
