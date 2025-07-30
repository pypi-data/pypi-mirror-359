import polars as pl
import ASHC_v3 as ashc
from ASHC_v3.CommonFunction import Polars_toDict

# Functions - jacadiWeeklySellthruReport, okaidiWeeklyBestSellerReport, okaidiWeeklySellthruReport
def jacadiWeeklySellthruReport(combFile, reportWeek, comp):     # comp = TY24
    inputFileDataType = {"Country":pl.String,"City":pl.String,"Location Code":pl.String,"StoreName":pl.String,"ShortName":pl.String,"Location Type":pl.String,"LFL Status":pl.String,"Comp":pl.String,"Year":pl.String,"Quarter":pl.String,"Month":pl.String,"MerchWeek":pl.String,"Posting Date":pl.String,"Brand Code":pl.String,"Item No_":pl.String,"Style Code":pl.String,"Colour Code":pl.String,"Size":pl.String,"Season Code":pl.String,"Sale_Period":pl.String,"Division":pl.String,"Product Group":pl.String,"Item Category":pl.String,"Item Class":pl.String,"Item Sub Class":pl.String,"Sub Class":pl.String,"Theme":pl.String,"Type":pl.String,"Description":pl.String,"Remarks":pl.String,"Disc_Status":pl.String,"Unit_Cost":pl.Float32,"Unit_Price":pl.Float32,"Unit_CurrentPrice":pl.Float32,"Buyers":pl.Float32,"Visitors":pl.Float32,"Season_Group":pl.String,"Target Amount":pl.Float32,"SaleQty":pl.Float32,"Total Sale Cost(AED)":pl.Float32,"Total Sale Retail(AED)":pl.Float32,"Total Sale Org. Retail(AED)":pl.Float32,"GrossMargin Value":pl.Float32,"Discount Value":pl.Float32,"Closing Stock":pl.Float32,"Total Stock Cost(AED)":pl.Float32,"Total Stock Retail(AED)":pl.Float32,"Total Purchase Qty":pl.Float32,"FC Cost (AED)":pl.Float32,"ST_Qty":pl.Float32,"ST_Cost(AED)":pl.Float32,"ST_Retail(AED)":pl.Float32,"OfferDetail":pl.String}
    df_OKSS01 = pl.read_csv(combFile, schema_overrides=inputFileDataType)
    df_OKSS01 = df_OKSS01.fill_null(0)
    df_OKSS01 = df_OKSS01.fill_nan(0)
    df_OKSS01 = df_OKSS01.with_columns((pl.col('Style Code')+ pl.col('Colour Code')).alias('RefCode'),)
    df_OKSS01 = df_OKSS01.with_columns(pl.col('RefCode').str.strip_chars().str.replace('All111','0').cast(pl.Int64))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('RefCode').cast(pl.Int64))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Remarks').map_elements(lambda x: "Non Carryover" if (str(x) == "Blocked") or (str(x) == "0") or (x == 0) else x, return_dtype=pl.String).alias('Remarks2'),)
    df_OKSS01 = df_OKSS01.with_columns((pl.col('Division') + " " + pl.col('Product Group') + " " + pl.col('Item Category')).alias('Departmant'))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Remarks2').alias('Remarks3'),)
    df_OKSS01 = df_OKSS01.fill_null(0)
    df_OKSS01 = df_OKSS01.fill_nan(0)
    df_OKSS01 = df_OKSS01.filter(pl.col('Comp') == comp)        
    df_OKSS02 = df_OKSS01.filter(pl.col('MerchWeek') == reportWeek)
    pIdx = ['Country','ShortName','RefCode','Departmant','Division','Product Group','Item Category','Item Class','Theme','Season Code','Season_Group','Remarks2','Remarks3']
    pVal = ["SaleQty","Total Sale Cost(AED)","Total Sale Retail(AED)","Discount Value","GrossMargin Value","Closing Stock","Total Stock Cost(AED)","Total Stock Retail(AED)"]
    Lwk_Dpt = df_OKSS02.group_by(pIdx).agg(pl.sum(pVal))
    Lwk_Dpt = Lwk_Dpt.fill_null(0)
    Lwk_Dpt = Lwk_Dpt.fill_nan(0)
    Lwk_Dpt = Lwk_Dpt.rename({"SaleQty":"LW SaleQty","Total Sale Retail(AED)":"LW Amt(AED)","Discount Value":"LW Discount Value","GrossMargin Value":"LW GrossMargin Value"})
    pIdx = ['Country','ShortName','RefCode','Departmant','Division','Product Group','Item Category','Item Class','Theme','Season Code','Season_Group','Remarks2','Remarks3']
    pVal = ["SaleQty","Total Sale Cost(AED)","Total Sale Retail(AED)","Discount Value","GrossMargin Value"]
    LSes_Dpt = df_OKSS01.group_by(pIdx).agg(pl.sum(pVal))
    LSes_Dpt = LSes_Dpt.fill_null(0)
    LSes_Dpt = LSes_Dpt.fill_nan(0)
    LSes_Dpt = LSes_Dpt.rename({"SaleQty":"Total SaleQty","Total Sale Cost(AED)":"Total COGS(AED)","Total Sale Retail(AED)":"Sale Retail(AED)"})
    LSes_Dpt = LSes_Dpt.with_columns(pl.col('Sale Retail(AED)').alias('Total Amt(AED)'),)
    sesDept = pl.concat([Lwk_Dpt, LSes_Dpt], how="diagonal")
    sesDept = sesDept.fill_null(0)
    sesDept = sesDept.fill_nan(0)
    pIdx = ['Country','ShortName','RefCode','Departmant','Division','Product Group','Item Category','Item Class','Theme','Season Code','Season_Group','Remarks2','Remarks3']
    pVal = ["Total SaleQty","Total COGS(AED)","Total Amt(AED)","Sale Retail(AED)","Discount Value","GrossMargin Value","Closing Stock","Total Stock Cost(AED)","Total Stock Retail(AED)","LW SaleQty","LW Amt(AED)","LW Discount Value","LW GrossMargin Value"]
    finalPivot = sesDept.group_by(pIdx).agg(pl.sum(pVal))
    finalPivot = finalPivot.fill_null(0)
    finalPivot = finalPivot.fill_nan(0)
    finalPivot = finalPivot.filter(~pl.col('Remarks2').is_in(['All']))
    finalPivot = finalPivot.filter(~pl.col('RefCode') < 0)
    return finalPivot


def okaidiWeeklyBestSellerReport(okCombFile, reportWeek, offerDetailFile, comp):
    inputFileDataType = {"Country":pl.String,"City":pl.String,"Location Code":pl.String,"StoreName":pl.String,"ShortName":pl.String,"Location Type":pl.String,"LFL Status":pl.String,"Comp":pl.String,"Year":pl.String,"Quarter":pl.String,"Month":pl.String,"MerchWeek":pl.String,"Posting Date":pl.String,"Brand Code":pl.String,"Item No_":pl.String,"Style Code":pl.String,"Colour Code":pl.String,"Size":pl.String,"Season Code":pl.String,"Sale_Period":pl.String,"Division":pl.String,"Product Group":pl.String,"Item Category":pl.String,"Item Class":pl.String,"Item Sub Class":pl.String,"Sub Class":pl.String,"Theme":pl.String,"Type":pl.String,"Description":pl.String,"Remarks":pl.String,"Disc_Status":pl.String,"Unit_Cost":pl.Float32,"Unit_Price":pl.Float32,"Unit_CurrentPrice":pl.Float32,"Buyers":pl.Float32,"Visitors":pl.Float32,"Season_Group":pl.String,"Target Amount":pl.Float32,"SaleQty":pl.Float32,"Total Sale Cost(AED)":pl.Float32,"Total Sale Retail(AED)":pl.Float32,"Total Sale Org. Retail(AED)":pl.Float32,"GrossMargin Value":pl.Float32,"Discount Value":pl.Float32,"Closing Stock":pl.Float32,"Total Stock Cost(AED)":pl.Float32,"Total Stock Retail(AED)":pl.Float32,"Total Purchase Qty":pl.Float32,"FC Cost (AED)":pl.Float32,"ST_Qty":pl.Float32,"ST_Cost(AED)":pl.Float32,"ST_Retail(AED)":pl.Float32,"OfferDetail":pl.String}
    df = pl.read_excel(source=ashc.OkaidiMaster,sheet_name="OK_Master",)       # schema_overrides=col_dtype,infer_schema_length=20000,
    df = df.fill_null(0)
    df = df.fill_nan(0)
    remarks = Polars_toDict(df, 'RFF', 'Remarks')
    offerFileData = pl.read_excel(offerDetailFile, sheet_name="Sheet1")
    offer = Polars_toDict(offerFileData, 'Combo', 'Offer')
    df_OKSS01 = pl.read_csv(okCombFile, schema_overrides=inputFileDataType)
    df_OKSS01 = df_OKSS01.fill_null(0)
    df_OKSS01 = df_OKSS01.fill_nan(0)
    df_OKSS01 = df_OKSS01.with_columns((pl.col('Division') + " " + pl.col('Product Group') + " " + pl.col('Item Category')).alias('Departmant'))
    df_OKSS1A = df_OKSS01[['Country','ShortName','Departmant','Division','Product Group','Item Category','Item Class','Comp','Season Code','Season_Group','MerchWeek','Style Code','Colour Code','SaleQty','Total Sale Cost(AED)','Total Sale Retail(AED)','Discount Value','GrossMargin Value','Closing Stock','ST_Qty','ST_Cost(AED)','ST_Retail(AED)']]
    df_OKSS1A = df_OKSS1A.filter(pl.col('Comp') == comp)    # Changes df_OKSS1WEEK to df_OKSS1A
    df_OKSS1WEEK = df_OKSS1A.filter(pl.col('MerchWeek') == reportWeek)
    index = ['Country','ShortName','Departmant','Division','Item Category','Item Class','Style Code','Colour Code','Season Code','Season_Group']
    values = ['SaleQty','Total Sale Cost(AED)','Total Sale Retail(AED)','Discount Value','GrossMargin Value','Closing Stock']
    bsLwk_refcode = df_OKSS1WEEK.group_by(index).agg(pl.sum(values))
    bsLwk_refcode = bsLwk_refcode.fill_null(0)
    bsLwk_refcode = bsLwk_refcode.fill_nan(0)
    bsLwk_refcode = bsLwk_refcode.rename({"SaleQty":"LW SaleQty","Total Sale Cost(AED)":"LW Cost(AED)","Total Sale Retail(AED)":"LW Amt(AED)","Discount Value":"LW Discount Value","GrossMargin Value":"LW GrossMargin Value"})
    index = ['Country','ShortName','Departmant','Division','Item Category','Item Class','Style Code','Colour Code','Season Code','Season_Group']
    values = ['SaleQty','Total Sale Cost(AED)','Total Sale Retail(AED)','Discount Value','GrossMargin Value']
    bsLal_refcode = df_OKSS1A.group_by(index).agg(pl.sum(values))
    bsLal_refcode = bsLal_refcode.fill_null(0)
    bsLal_refcode = bsLal_refcode.fill_nan(0)
    bsLal_refcode = bsLal_refcode.rename({"SaleQty":"Total SaleQty","Total Sale Cost(AED)":"Total COGS(AED)","Total Sale Retail(AED)":"Total Amt(AED)"})
    bestSeller01 = pl.concat([bsLwk_refcode, bsLal_refcode], how = "diagonal")
    index = ['Country','ShortName','Departmant','Division','Item Category','Item Class','Style Code','Colour Code','Season Code','Season_Group']
    values = ["Total SaleQty","Total COGS(AED)","Total Amt(AED)","Discount Value","GrossMargin Value","Closing Stock","LW SaleQty","LW Amt(AED)","LW Discount Value","LW GrossMargin Value"]
    bestSeller02 = bestSeller01.group_by(index).agg(pl.sum(values))
    bestSeller02 = bestSeller02.fill_null(0)
    bestSeller02 = bestSeller02.fill_nan(0)
    bestSeller02 = bestSeller02.with_columns((pl.col('Total SaleQty') + pl.col('Closing Stock') + pl.col('LW SaleQty')).alias('tmp'))
    bestSeller03 = bestSeller02.filter(pl.col('tmp') > 0 )
    bestSeller03 = bestSeller03.drop('tmp')
    bestSeller03 = bestSeller03.filter(pl.col('Style Code').ne('All'))
    bestSeller03 = bestSeller03.with_columns(pl.col('Style Code').cast(pl.Int64))
    bestSeller03 = bestSeller03.with_columns(pl.col('Colour Code').cast(pl.Int64))
    bestSeller03 = bestSeller03.with_columns((pl.col('Style Code').cast(pl.String) + pl.col('Colour Code').cast(pl.String)).alias('RefCode'),)
    bestSeller03 = bestSeller03.with_columns(pl.col('RefCode').str.strip_chars().str.replace('AllAll','0').cast(pl.Int64))
    bestSeller03 = bestSeller03.with_columns(pl.col('RefCode').cast(pl.Int64))
    bestSeller03 = bestSeller03.with_columns(pl.col('RefCode').replace_strict(remarks, default=None).alias('Remarks2'))
    bestSeller03 = bestSeller03.with_columns(pl.col('Remarks2').map_elements(lambda x: "Non Carryover" if (str(x) == "Blocked and Discounted") or (str(x) == "0") or (x == 0) else x, return_dtype=pl.String).alias('Remarks3'),)
    bestSeller03 = bestSeller03.with_columns(pl.col('Division').map_elements(lambda x: x if ((x == "Okaidi") or (x == "Obaibi")) else "Okaidi", return_dtype=pl.String).alias('Division'),)
    bestSeller03 = bestSeller03.with_columns((pl.col('Country') + pl.col('RefCode').cast(pl.String)).alias('CountryRef'),)
    bestSeller03 = bestSeller03.with_columns(pl.col('CountryRef').replace_strict(offer, default=None).alias('SaleItem'))
    return bestSeller03


def okaidiWeeklySellthruReport(okCombFile, reportWeek, comp):       # comp = TY24
    inputFileDataType = {"Country":pl.String,"City":pl.String,"Location Code":pl.String,"StoreName":pl.String,"ShortName":pl.String,"Location Type":pl.String,"LFL Status":pl.String,"Comp":pl.String,"Year":pl.String,"Quarter":pl.String,"Month":pl.String,"MerchWeek":pl.String,"Posting Date":pl.String,"Brand Code":pl.String,"Item No_":pl.String,"Style Code":pl.String,"Colour Code":pl.String,"Size":pl.String,"Season Code":pl.String,"Sale_Period":pl.String,"Division":pl.String,"Product Group":pl.String,"Item Category":pl.String,"Item Class":pl.String,"Item Sub Class":pl.String,"Sub Class":pl.String,"Theme":pl.String,"Type":pl.String,"Description":pl.String,"Remarks":pl.String,"Disc_Status":pl.String,"Unit_Cost":pl.Float32,"Unit_Price":pl.Float32,"Unit_CurrentPrice":pl.Float32,"Buyers":pl.Float32,"Visitors":pl.Float32,"Season_Group":pl.String,"Target Amount":pl.Float32,"SaleQty":pl.Float32,"Total Sale Cost(AED)":pl.Float32,"Total Sale Retail(AED)":pl.Float32,"Total Sale Org. Retail(AED)":pl.Float32,"GrossMargin Value":pl.Float32,"Discount Value":pl.Float32,"Closing Stock":pl.Float32,"Total Stock Cost(AED)":pl.Float32,"Total Stock Retail(AED)":pl.Float32,"Total Purchase Qty":pl.Float32,"FC Cost (AED)":pl.Float32,"ST_Qty":pl.Float32,"ST_Cost(AED)":pl.Float32,"ST_Retail(AED)":pl.Float32,"OfferDetail":pl.String}
    df_OKSS01 = pl.read_csv(okCombFile, schema_overrides=inputFileDataType)
    df_OKSS01 = df_OKSS01.fill_null(0)
    df_OKSS01 = df_OKSS01.fill_nan(0)
    df_OKSS01 = df_OKSS01.filter(pl.col('Style Code').ne('All'))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Style Code').cast(pl.Int64))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Colour Code').cast(pl.Int64))
    df_OKSS01 = df_OKSS01.with_columns((pl.col('Style Code').cast(pl.String) + pl.col('Colour Code').cast(pl.String)).alias('RefCode'),)
    df_OKSS01 = df_OKSS01.with_columns(pl.col('RefCode').str.strip_chars().str.replace('All111','0').cast(pl.Int64))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('RefCode').cast(pl.Int64))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Remarks').map_elements(lambda x: "Non Carryover" if (str(x) == "Blocked and Discounted") or (str(x) == "0") or (x == 0) else x, return_dtype=pl.String).alias('Remarks2'),)
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Division').map_elements(lambda x: x if ((x == "Okaidi") or (x == "Obaibi")) else "Okaidi", return_dtype=pl.String).alias('Division'),)
    df_OKSS01 = df_OKSS01.with_columns((pl.col('Division') + " " + pl.col('Product Group') + " " + pl.col('Item Category')).alias('Departmant'))
    df_OKSS01 = df_OKSS01.with_columns(pl.col('Remarks2').alias('Remarks3'),)
    df_OKSS01 = df_OKSS01.fill_null(0)
    df_OKSS01 = df_OKSS01.fill_nan(0)
    df_OKSS01 = df_OKSS01.filter(pl.col('Comp') == comp)        # Changed df_OKSS02 to df_OKSS01
    df_OKSS02 = df_OKSS01.filter(pl.col('MerchWeek') == reportWeek)
    pIdx = ['Country','ShortName','Departmant','Division','Product Group','Item Category','Season Code','Season_Group','Remarks2','Remarks3']
    pVal = ["SaleQty","Total Sale Cost(AED)","Total Sale Retail(AED)","Discount Value","GrossMargin Value","Closing Stock","Total Stock Cost(AED)","Total Stock Retail(AED)"]
    Lwk_Dpt = df_OKSS02.group_by(pIdx).agg(pl.sum(pVal))
    Lwk_Dpt = Lwk_Dpt.fill_null(0)
    Lwk_Dpt = Lwk_Dpt.fill_nan(0)
    Lwk_Dpt = Lwk_Dpt.rename({"SaleQty":"LW SaleQty","Total Sale Retail(AED)":"LW Amt(AED)","Discount Value":"LW Discount Value","GrossMargin Value":"LW GrossMargin Value"})
    pIdx = ['Country','ShortName','Departmant','Division','Product Group','Item Category','Season Code','Season_Group','Remarks2','Remarks3']
    pVal = ["SaleQty","Total Sale Cost(AED)","Total Sale Retail(AED)","Discount Value","GrossMargin Value"]
    LSes_Dpt = df_OKSS01.group_by(pIdx).agg(pl.sum(pVal))
    LSes_Dpt = LSes_Dpt.fill_null(0)
    LSes_Dpt = LSes_Dpt.fill_nan(0)
    LSes_Dpt = LSes_Dpt.rename({"SaleQty":"Total SaleQty","Total Sale Cost(AED)":"Total COGS(AED)","Total Sale Retail(AED)":"Sale Retail(AED)"})
    LSes_Dpt = LSes_Dpt.with_columns(pl.col('Sale Retail(AED)').alias('Total Amt(AED)'),)
    sesDept = pl.concat([Lwk_Dpt, LSes_Dpt], how="diagonal")
    sesDept = sesDept.fill_null(0)
    sesDept = sesDept.fill_nan(0)
    pIdx = ['Country','ShortName','Departmant','Division','Product Group','Item Category','Season Code','Season_Group','Remarks2','Remarks3']
    pVal = ["Total SaleQty","Total COGS(AED)","Total Amt(AED)","Sale Retail(AED)","Discount Value","GrossMargin Value","Closing Stock","Total Stock Cost(AED)","Total Stock Retail(AED)","LW SaleQty","LW Amt(AED)","LW Discount Value","LW GrossMargin Value"]
    finalPivot = sesDept.group_by(pIdx).agg(pl.sum(pVal))
    finalPivot = finalPivot.fill_null(0)
    finalPivot = finalPivot.fill_nan(0)
    finalPivot = finalPivot.filter(~pl.col('Remarks2').is_in(['All']))
    return finalPivot


def ParfoisColumnRename(df):
    reNameCols = {"Category":"Item Category","Family":"Item Class","Sub Family":"Item Sub Class","Fashion Type":"Product Group","Style_Colour":"RefCode","PA Season":"Season Code"}
    dropCols = ["Cord Sets","Style","Season Code","Cumm Sales"]
    df = df.drop(dropCols)
    df = df.rename(reNameCols)
    finalDF = df.with_columns(pl.col('Item Category').alias('Division'),)
    finalDF = finalDF[["Brand Code","Country","City","Location Code","StoreName","ShortName","StoreSize","Location Type","Status","Division","Product Group","Item Category","Item Class","Item Sub Class","Theme","Type","RefCode","Style Code","First Purchase Date","Last Receive Date","Colour Code","Size","Item No_","Season Code","Unit Price","Current Price","Unit Cost","ExchangeRate(AED)","Cumm. SaleQty","Cumm. CostValue","Cumm. SaleValue","MTD SaleQty","MTD CostValue","MTD SaleValue","WTD SaleQty","WTD CostValue","WTD SaleValue","Closing Stock","StockCost","StockRetail","StockOrgRetail","Purchased","Remarks","Combo2","Offer_Price","EOSS Discount","Disc.P"]]
    return finalDF