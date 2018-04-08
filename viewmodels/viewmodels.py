from abc import ABC, abstractmethod
from models.convertible_bond_tree import FeatureSchedule, ConvertibleBondModelInput, ConvertibleBondTree
from models.sensitivity_analyser import ConvertibleBondSensitivityAnalyzer, Plotter
import numpy as np

class ViewModel(ABC):

    @abstractmethod
    def getInput(self):
        pass

    @abstractmethod
    def update(self, aValue):
        pass

class CheckBoxViewModel(ViewModel):
    def __init__(self, checkBox=None, convertTo=None, convertFrom = None):
        self.checkBox = checkBox
        self.convertTo = convertTo or Converters.boolToInt
        self.convertFrom = convertFrom or Converters.intToBool
        self._checked = False

    def update(self, aValue):
        self._checked = aValue
        self.checkBox.setCheckState( self.convertTo(aValue))

    def getInput(self):
        return self.convertFrom( self.checkBox.checkState() )

class ListViewModel(ViewModel):
    def __init__(self, listView=None, newItemInput=None, convertTo=None, convertFrom = None):
        super().__init__()
        self.newItemInput = newItemInput
        self.listView = listView
        self._rawValue = None
        self.convertTo = convertTo or Converters.floatListToStrList
        self.convertFrom = convertFrom or Converters.strListToFloatList

    def getInput(self):
        return self.convertFrom( self._rawValue )

    def update(self, aValue):
        self.onRemoveAllItems()
        self.listView.addItems( self.convertTo(aValue) )
        self._updateItems()

    def onAddNewItem(self):
        input = self.newItemInput.text()
        self.listView.addItem( input )
        self._updateItems()

    def removeItems( self, itemsToRemove ):
        if not itemsToRemove:
            return
        for item in itemsToRemove:
            self.listView.takeItem( self.listView.row(item) )

        self._updateItems()

    def onRemoveSelectedItems(self):
        self.removeItems(self.listView.selectedItems())

    def onRemoveAllItems(self):
        self.removeItems( self._allListItems() )

    def _allListItems(self):
        return [self.listView.item(i) for i in range(self.listView.count())]

    def _updateItems(self):
        self._rawValue = [item.text() for item in  self._allListItems() ]

class TextViewModel(ViewModel):
    def __init__(self, inputText=None, convertTo=None, convertFrom = None):
        super().__init__()
        self.inputText = inputText
        self._rawValue = ''
        self.convertTo = convertTo or Converters.numberToStr
        self.convertFrom = convertFrom or Converters.strToFloat

    def update(self, aValue):
        self.inputText.setText( self.convertTo(aValue) )

    def getInput(self):
        return self.convertFrom( self._rawValue )

    def onTextChanged(self):
        self._rawValue = self.inputText.text()


class OptionSelectionViewModel(ViewModel):
    def __init__(self, optionsProvider=None, convertTo=None, convertFrom = None):
        self.optionsProvider = optionsProvider
        self.convertTo = convertTo or Converters.nullConverter
        self.convertFrom = convertFrom or Converters.nullConverter
        self._selectedOption = None

    def update(self, aValue):
        self.optionsProvider.clear()
        self.optionsProvider.addItems( self.convertTo(aValue) )
        self._selectedOption = aValue[0]

    def getInput(self):
        return self._selectedOption

    def onOptionSelected(self):
        self._selectedOption = self.optionsProvider.currentText()

class ConvertibleBondViewModel(ViewModel):
    def __init__(self, timeViewModel=None, riskFreeViewModel=None, irVolatilityViewModel=None, deltaTimeViewModel=None,
                 faceValueViewModel=None, riskyZeroCouponsViewModel=None, recoveryViewModel=None,
                 initialStockPriceViewModel=None,stockVolatilityViewModel=None, irStockCorrelationViewModel=None,
                 conversionFactorViewModel=None, featureScheduleViewModel=None):
        super().__init__()
        self.timeViewModel                  = timeViewModel or TextViewModel( convertFrom=Converters.strToInt )
        self.riskFreeViewModel              = riskFreeViewModel or ListViewModel()
        self.irVolatilityViewModel          = irVolatilityViewModel or TextViewModel()
        self.deltaTimeViewModel             = deltaTimeViewModel or TextViewModel()
        self.faceValueViewModel             = faceValueViewModel or TextViewModel()
        self.riskyZeroCouponsViewModel      = riskyZeroCouponsViewModel or ListViewModel()
        self.recoveryViewModel              = recoveryViewModel or TextViewModel()
        self.initialStockPriceViewModel     = initialStockPriceViewModel or TextViewModel()
        self.stockVolatilityViewModel       = stockVolatilityViewModel or TextViewModel()
        self.irStockCorrelationViewModel    = irStockCorrelationViewModel or TextViewModel()
        self.conversionFactorViewModel      = conversionFactorViewModel or TextViewModel()
        self.featureScheduleViewModel       = featureScheduleViewModel or ListViewModel( convertTo=Converters.featureScheduleToStrList,
                                                                                 convertFrom=Converters.strListToFeature)
        self.bondPriceViewModel             = TextViewModel()
        self.model                          = None


    def update(self, aValue):
        self.timeViewModel.update( aValue.time )
        self.riskFreeViewModel.update( aValue.zeroCouponRates )
        self.irVolatilityViewModel.update( aValue.irVolatility )
        self.deltaTimeViewModel.update( aValue.deltaTime )
        self.faceValueViewModel.update( aValue.faceValue )
        self.riskyZeroCouponsViewModel.update( aValue.riskyZeroCoupons )
        self.recoveryViewModel.update( aValue.recovery )
        self.initialStockPriceViewModel.update( aValue.initialStockPrice )
        self.stockVolatilityViewModel.update( aValue.stockVolatility )
        self.irStockCorrelationViewModel.update( aValue.irStockCorrelation )
        self.conversionFactorViewModel.update( aValue.conversionFactor )
        self.featureScheduleViewModel.update( aValue.featureSchedule )

    def getInput(self):
        time                = self.timeViewModel.getInput()
        zeroCouponRates     = self.riskFreeViewModel.getInput()
        irVolatility        = self.irVolatilityViewModel.getInput()
        deltaTime           = self.deltaTimeViewModel.getInput()
        faceValue           = self.faceValueViewModel.getInput()
        riskyZeroCoupons    = self.riskyZeroCouponsViewModel.getInput()
        recovery            = self.recoveryViewModel.getInput()
        initialStockPrice   = self.initialStockPriceViewModel.getInput()
        stockVolatility     = self.stockVolatilityViewModel.getInput()
        irStockCorrelation  = self.irStockCorrelationViewModel.getInput()
        conversionFactor    = self.conversionFactorViewModel.getInput()
        featureSchedule     = self.featureScheduleViewModel.getInput()

        return ConvertibleBondModelInput( zeroCouponRates, irVolatility, deltaTime, faceValue, riskyZeroCoupons, recovery,
                 initialStockPrice, stockVolatility, irStockCorrelation, conversionFactor, featureSchedule, time)

    def onPriceBondClicked(self):
        self.bondPriceViewModel.update(0.0)
        self.setModel()
        self.bondPriceViewModel.update( self.model.priceBond() )

    def setModel(self):
        modelInput = self.getInput()
        self.model = ConvertibleBondTree(modelInput)


class SensitivityAnalyzerViewModel(ViewModel):
    def __init__(self, convertibleBondViewModel, optionsViewModel=None, fromViewModel=None,
                 toViewModel=None, numberOfPointsViewModel=None, includeNoConversionViewModel=None,newGraphViewModel=None):
        self.convertibleBondViewModel = convertibleBondViewModel
        self.optionsViewModel = optionsViewModel or OptionSelectionViewModel()
        self.fromViewModel = fromViewModel or TextViewModel()
        self.toViewModel = toViewModel or TextViewModel()
        self.numberOfPointsViewModel = numberOfPointsViewModel or TextViewModel( convertFrom=Converters.strToInt )
        self.plotter = Plotter()
        self.includeNoConversionViewModel = includeNoConversionViewModel or CheckBoxViewModel()
        self.newGraphViewModel = newGraphViewModel or CheckBoxViewModel()

    def onIncludeNoConvesionChanged(self):
        pass

    def onAnalyzeClicked(self):
        data = self.getInput()
        self.convertibleBondViewModel.setModel()
        model = self.convertibleBondViewModel.model.clone()
        analyzer = ConvertibleBondSensitivityAnalyzer( model )
        selectedAtribute = data['selected_option']
        dependentValues = np.linspace(data['from'], data['to'], data['points'])
        independentValues = analyzer.analyzeBondPrice(selectedAtribute, dependentValues)
        dataToPlot = [{'x':dependentValues, 'y':independentValues, 'color':'r',
                           'label':'Bond Price({})'.format(selectedAtribute)}]

        if self._includeNoConversionPrice():
            independentValues = analyzer.analyzeBondPriceNoConversion(selectedAtribute, dependentValues)
            dataToPlot.append({'x':dependentValues, 'y':independentValues, 'color':'b',
                           'label':'Bond No Conversion Price({})'.format(selectedAtribute)})

        self.plotter.plot(dataToPlot, newGraph=self._useNewGraph())

    def _includeNoConversionPrice(self):
        return self.includeNoConversionViewModel.getInput()

    def _useNewGraph(self):
        return self.newGraphViewModel.getInput()

    def update(self, aValue):
        self.optionsViewModel.update( aValue['options'] )
        self.fromViewModel.update( aValue.get('from',0.0) )
        self.toViewModel.update( aValue.get('to',1.0) )
        self.numberOfPointsViewModel.update( aValue.get('points',0) )

    def getInput(self):
        return {'selected_option':self.optionsViewModel.getInput(), 'from':self.fromViewModel.getInput(),
                'to':self.toViewModel.getInput(), 'points':self.numberOfPointsViewModel.getInput()}

class Converters:

    @staticmethod
    def nullConverter(value):
        return value

    @staticmethod
    def strToFloat(value):
        return float(value)

    @staticmethod
    def boolToInt(value):
        return int(value)

    @staticmethod
    def intToBool(value):
        return bool(value)

    @staticmethod
    def strToInt(value):
        return int(value)

    @staticmethod
    def numberToStr(value):
        return str(value)

    @staticmethod
    def strToInt(value):
        return int(value)

    @staticmethod
    def strListToFloatList(value):
        return [Converters.strToFloat(aValue) for aValue in value]

    @staticmethod
    def floatListToStrList(value):
        return [Converters.numberToStr(aValue) for aValue in value]

    @staticmethod
    def featureScheduleToStrList(value):
        result = []
        sortedKeys = sorted(list(value.features.keys()))
        for k in sortedKeys:
            feature = value.feature( k )
            result.append('{},{},{}'.format( k,feature.callValue(), feature.putValue() ) )

        return result

    @staticmethod
    def strListToFeature(value):
        featureSchedule = FeatureSchedule()
        for aValue in value:
            parsedValue = aValue.split(',')
            period = int(parsedValue[0])
            callValue = float(parsedValue[1])
            putValue = float(parsedValue[2])
            featureSchedule.addFeature( period, callValue=callValue, putValue=putValue)

        return featureSchedule