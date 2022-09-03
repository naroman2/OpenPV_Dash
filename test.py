import datetime

# datetime in string format for may 25 1999
input = '2021/05/25'
  
# format
format = '%Y/%m/%d'
  
# convert from string format to datetime format
datetime = datetime.datetime.strptime(input, format)
  
# get the date from the datetime using date() 
# function
print(datetime.date())