import os
import polars as pl
import ASHC_v3 as ashc
from ASHC_v3.CommonFunction import Polars_toDict

def initiateConfig(saleDir, stockDir, masterDir, dataDir, outDir):
    """This Function initializes this library with various default parameters,
    It is very important to call this function before using any other functions from ASHC_v3"""
    #print("Config initiated")
    ashc.outFolder = outDir
    ashc.budFile = os.path.join(dataDir, '1.1a._DAILY_SALES___TY_vs_PY*.csv')
    ashc.kpiFile = os.path.join(dataDir, 'KPI', '*.csv')
    ashc.sysPriceFiles = os.path.join(dataDir, 'ItemPrice', '*.csv.gz')
    ashc.purchDateFiles = os.path.join(dataDir, 'FirstPurch', '*.csv.gz')
    ashc.stockDumpFiles = os.path.join(stockDir, '*.csv.gz')
    ashc.offerFile = os.path.join(dataDir, 'Configs', 'Offer_Detail.csv')
    ashc.xlConfigFile = os.path.join(dataDir, 'Configs', 'ConfigFile.xlsx')
    ashc.UndizMaster = os.path.join(masterDir, 'UZ-Master.xlsx')
    ashc.VincciMaster = os.path.join(masterDir, 'VI-Master.xlsx')
    ashc.YRMaster = os.path.join(masterDir, 'YR-Master.xlsx')
    ashc.JacadiMaster = os.path.join(masterDir, 'JC-Master.xlsx')
    ashc.OkaidiMaster = os.path.join(masterDir, 'OK-Master.xlsx')
    ashc.PerfoisMaster = os.path.join(masterDir, 'PA-Master.xlsx')
    ashc.LSMaster = os.path.join(masterDir, 'LS-Master.xlsx')
    

    configData = pl.read_excel(source=ashc.xlConfigFile,sheet_name="StoreMaster",)    #engine_options={"skip_empty_lines": True},
    lflData = pl.read_excel(source=ashc.xlConfigFile,sheet_name="LFLMaster",)         #engine_options={"skip_empty_lines": True},
    dateData = pl.read_excel(source=ashc.xlConfigFile,sheet_name="DateMaster",)       #schema_overrides={"Date(Month2nd)":pl.Datetime},engine_options={"skip_empty_lines": True},
    try:
        dateData = dateData.with_columns(pl.col('Date(Month2nd)').str.to_datetime())
    except:
        print(" ")

    #----------------------Store Master---------------------------------------------
    ashc.ShortStoreName = Polars_toDict(configData, 'LocationCode', 'ShortStoreName')
    ashc.StoreName = Polars_toDict(configData, 'LocationCode', 'StoreName')
    ashc.BrandName = Polars_toDict(configData, 'LocationCode', 'BrandCode')
    ashc.Country = Polars_toDict(configData, 'LocationCode', 'Country')
    ashc.City = Polars_toDict(configData, 'LocationCode', 'City')
    ashc.LocationType = Polars_toDict(configData, 'LocationCode', 'LocationType')
    ashc.Status = Polars_toDict(configData, 'LocationCode', 'Status')
    ashc.Area = Polars_toDict(configData, 'LocationCode', 'Area')
    ashc.OpeningDate = Polars_toDict(configData, 'LocationCode', 'OpeningDate')
    ashc.LocCode = Polars_toDict(configData, 'StoreName', 'LocationCode')
    #--------------------------------------------------------------------------------
    ashc.Year_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Date Year Month (Year)')
    ashc.Qtr_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Date Year Month (Quarter)')
    ashc.Month_ = Polars_toDict(dateData, 'Date(Month2nd)', 'Date Year Month (Month)')
    ashc.Week_ = Polars_toDict(dateData, 'Date(Month2nd)', 'FormatedWeekNo')
    ashc.Lyty_ = Polars_toDict(dateData, 'Date(Month2nd)', 'LYTY')
    #--------------------------------------------------------------------------------
    ashc.Lfl = Polars_toDict(lflData, 'Combo', 'Status(LFL)')