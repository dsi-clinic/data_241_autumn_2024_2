import pandas as pd
import zipfile

def mergedaily(zippath):
  """
  Input:
  Zippath: path to zip file

  Process:
  1. Unzips file in Zip file object
  2. Gets a list of csv files within the zip file
  3. Makes the DF using the first csv as the template
  4. Loops through the csv files and appends to the template
  5. Appends either NASDAQ or NYSE at the end


  Output:
  Merged dataframe containing merged CSV data from zip file
  """

  zf = zipfile.ZipFile(zippath)
  zflist = zf.namelist()
  zfdf = pd.read_csv(zf.open(zflist[0]))
  for csv in zf.namelist()[1:]:
    mergedf = pd.read_csv(zf.open(csv))
    zfdf = pd.concat([zfdf, mergedf],
                          ignore_index = True,
                          sort = False)
  if 'NASDAQ' in zippath:
    zfdf['market'] = 'NASDAQ'
  elif 'NYSE' in zippath:
    zfdf['market'] = 'NYSE'
  else:
    zfdf['market'] = 'Not NYSE or NASDAQ'

  return zfdf



def __main__():
  """
  Input:
  None

  Process:
  1. Creates seperate DF for nasdaq and nysedf based on specified zip file path
  using the mergedaily function above
  2. Combines both DF
  3. Creates BRK.A only DF
  answers*
  4. Filters BRK.A only DF for open max and indexes the date
  5. Finds rows for individual and combined


  Output:
  Returns combinded rows, nasdaq rows, nyse rows, and BRK.A date
  """

  pathone = './data/raw_data/NASDAQ_2019.zip'
  pathtwo = './data/raw_data/NYSE_2019.zip'

  nasdaqdf = mergedaily(pathone)
  nysedf = mergedaily(pathtwo)
  combindeddf = pd.concat([nasdaqdf, nysedf],
                          ignore_index = True,
                          sort = False)

  brka = combindeddf[combindeddf['Symbol']=='BRK.A']


  brkadate = brka[brka['Open']==max( brka['Open'])]['Date'].iloc[0]
  combindedrows = combindeddf.shape[0]
  nasdaqrows = nasdaqdf.shape[0]
  nyserows = nysedf.shape[0]

  return f"Total Rows: {combindedrows}", f"Nasdaq Rows: {nasdaqrows}", f"NYSE Rows: {nyserows}", brkadate

if __name__ == "__main__":
    results = __main__()
    for result in results:
        print(result)