"""
Please write you name here: Sharon Mazor
"""

def getBreakTimes(breaknotes, start_time): # additional function added for cleaner code
    """

    :param breaknotes: One line's break notes as supplied in work_shift.csv
    :type string:
    :param start_time: One line's start time as supplied in work_shift.csv
    :type string:
    :return: A list of the start and end times of the break as floats (where the 2 numbers after the decimal point are equal to minutes after the hour)
    For example, it should be something like :
    [13,15.3] for a 1PM-3:30PM break
    :rtype list:
    """
    # removing whitespace
    breakstarttime = breaknotes[0].strip()
    breakendtime = breaknotes[1].strip()
    
    # converting from PM to the numerical equivalent without letters
    if breakstarttime.find("PM") != -1:
        breakstarttime=float(breakstarttime[:-2])+12

    if breakendtime.find("PM") != -1:
        breakendtime=float(breakendtime[:-2])+12
   
    # if the numerical value of the breaks are currently less than the start hour then 12 hours are added 
    # (e.g. converting 4 to 16 with the assumption PM was missed)
    startHour = float(start_time[:-3])
        
    if(float(breakstarttime)<startHour):
        breakstarttime = float(breakstarttime) + 12
            
    if(float(breakendtime)<startHour):
        breakendtime = float(breakendtime) + 12

    return [float(breakstarttime),float(breakendtime)]

def process_shifts(path_to_csv):
    """

    :param path_to_csv: The path to the work_shift.csv
    :type string:
    :return: A dictionary with time as key (string) with format %H:%M
        (e.g. "18:00") and cost as value (Number)
    For example, it should be something like :
    {
        "17:00": 50,
        "22:00: 40,
    }
    In other words, for the hour beginning at 17:00, labour cost was
    50 pounds
    :rtype dict:
    """
    theShiftsFile = open(path_to_csv)
    theShiftsFileContent = theShiftsFile.read()
    theShiftsData = theShiftsFileContent.splitlines()

    shiftDicto = {} # all the shift data in a consistent format
    startTimes= []
    endTimes=[]

    # get all the shift data in the same consistent format
    for x in range(1, len(theShiftsData)):
    
        dictdata = theShiftsData[x].split(",")
        breaknotes = dictdata[0].split("-")
        end_time = dictdata[1]
        pay_rate = float(dictdata[2])
        start_time = dictdata[3]
        
        breaknotes = getBreakTimes(breaknotes, start_time)
        breakstarttime = breaknotes[0]
        breakendtime = breaknotes[1]           

        shiftDicto['shift'+str(x)]=[start_time, end_time, pay_rate, breakstarttime,breakendtime]
        startTimes.append(start_time)
        endTimes.append(end_time)

    mini = int(min(startTimes)[:-3]) # get earliest time mentioned in the data 
    maxi = int(max(endTimes)[:-3]) # get the latest time mentioned in the data

    labourCostDicto = {} # the dictionary that will be returned
    
    # assign all the hours that labour cost will be calculated for in the dictionary
    for i in range(mini,maxi):
        if (i>9):
            timeKey = str(i)+":00"
        else: 
            timeKey = "0"+str(i)+":00"
        labourCostDicto[timeKey]=0

    # calculate and assign all labour cost by shift
    for x in range(1, len(theShiftsData)):
       [start_time, end_time, pay_rate, breakstarttime,breakendtime] = shiftDicto['shift'+str(x)] 
      
       partsST = start_time.split(":")
       numStartT = float(partsST[0]+"."+partsST[1]) # numerical start time
       partsET = end_time.split(":")
       numEndT = float(partsET[0]+"."+partsET[1]) # numerical end time

       start_time = start_time[:-2]+"00" # setting start time as HH:00

       if breakstarttime>=(int(numStartT)+1): # if there was no break during this hour
            afterTheHour = (numStartT-int(numStartT))*100 # how many minutes after the hour they actually started (0 if they started at HH:00)
            minutesworked = 60-afterTheHour
         
       elif breakendtime>=(int(numStartT)+1):# if there was a break during this hour and it lasted from the start of the break to at least the end of the hour
            minutesworked = (breakstarttime-numStartT)*100 
            
       else: #if the break started and ended during the hour
            minutesworked = (breakstarttime-numStartT + int(numStartT)+1 - breakendtime)* 100
   
   
       labourCostDicto[start_time]=labourCostDicto[start_time]+(pay_rate* (minutesworked/60))       
       
       currentTime = int(numStartT)+1
       endHour = currentTime+1 # time the hour ends
       while currentTime<numEndT:
        
        partsCT = str(currentTime).split(".")
        if (int(partsCT[0])<=9):
            partsCT[0]="0"+partsCT[0]
       
        timeKey = partsCT[0]+":00"
        
        minutesWorked = 0.6 # will be multiplied by a hundred later to make 60 if not changed (assumes entire hour was worked)
        
        
        if (currentTime>= breakstarttime) and (endHour<= breakendtime): # the entire hour was spent on break
           
           minutesWorked = 0
            
        else: # not all the hour was spent on break

           if (breakstarttime>=currentTime) and (breakstarttime<endHour): # break started after or as the hour begins but before the hour is up

                minutesWorked = breakstarttime - currentTime # worked from the start of the hour to when the break began

                if (breakendtime<endHour): # break ended before the hour did
                
                    minutesWorked = minutesWorked+(currentTime+0.6-breakendtime) # also worked from the end of the break to the end of the hour

              
           elif (breakstarttime<currentTime) and (breakendtime>currentTime) and (breakendtime<endHour): # break started before the hour began but ends during the hour
           
                minutesWorked=currentTime+0.6-breakendtime

           if(numEndT<endHour): #if shift ends during the hour remove the minutes added when they should not have been
                minutesWorked = minutesWorked - (currentTime+0.6-numEndT)
                
        minutesWorked=minutesWorked*100
        labourCostDicto[timeKey] = labourCostDicto[timeKey]+pay_rate*(minutesWorked/60)
        currentTime=currentTime+1
        endHour = endHour+1 

    return labourCostDicto

def process_sales(path_to_csv):
    """

    :param path_to_csv: The path to the transactions.csv
    :type string:
    :return: A dictionary with time (string) with format %H:%M as key and
    sales as value (string),
    and corresponding value with format %H:%M (e.g. "18:00"),
    and type float)
    For example, it should be something like :
    {
        "17:00": 250,
        "22:00": 0,
    },
    This means, for the hour beginning at 17:00, the sales were 250 dollars
    and for the hour beginning at 22:00, the sales were 0.

    :rtype dict:
    """
    theSalesFile = open(path_to_csv)
    theSalesFileContent = theSalesFile.read()
    theSalesData = theSalesFileContent.splitlines() # a list of each line of data in the transactions.csv file

    salesDict = {} # the dictionary that will be returned
    
    for x in range(1, len(theSalesData)):
        transactionData = theSalesData[x].split(",") # first value is the dollar amount the transaction was worth, the second is the transaction time
        cost = transactionData[0]
        htime = transactionData[1] 
        htime = htime[:-2]+"00" # getting the start time of the hour the transaction occured in  e.g 10:00 if transaction happened at 10:53
       
        if (htime in salesDict): # if a sale had already occured in the same hour, increment total sales by current cost, otherwise set total sales as the new cost.
            salesDict[htime] = str(float(salesDict[htime])+ float(transactionData[0]))
        else:
            salesDict[htime] = transactionData[0]
    
    return salesDict

def compute_percentage(shifts, sales):
    """

    :param shifts:
    :type shifts: dict
    :param sales:
    :type sales: dict
    :return: A dictionary with time as key (string) with format %H:%M and
    percentage of labour cost per sales as value (float),
    If the sales are null, then return -cost instead of percentage
    For example, it should be something like :
    {
        "17:00": 20,
        "22:00": -40,
    }
    :rtype: dict
    """
  
    shiftTimes = shifts.keys()
    saleTimes = sales.keys()

    mini = min (shiftTimes)
    maxi = max (shiftTimes)
    mini = int(mini[:-3])
    maxi = int(maxi[:-3])

    percentagesDicto = {}
    
    for i in range(mini,maxi+1):
        if (i>9):
            key = str(i)+":00"
        else:
            key = "0"+str(i)+":00"
    
        labourcost = shifts[key]
        if key in saleTimes: # percentage of labour cost per sales as value (float)
            percentagesDicto[key]= float((labourcost/float(sales[key]))*100)
        else: # the sales are null, return -cost instead of percentage
            percentagesDicto[key]= float(labourcost)*-1

    return percentagesDicto

def best_and_worst_hour(percentages):
    """

    Args:
    percentages: output of compute_percentage
    Return: list of strings, the first element should be the best hour,
    the second (and last) element should be the worst hour. Hour are
    represented by string with format %H:%M
    e.g. ["18:00", "20:00"]

    """

    keys = list(percentages.keys())
    worstSoFar = percentages[keys[0]]
    worstHour = keys[0] # most loss made 
    # (e.g. most negative value as labour costs were high and no sales were made or if sales are always made than highest percentage of labour)
    bestSoFar = percentages[keys[0]]
    bestHour = keys[0] # lowest percentage (e.g. smallest positive value as labour costs were low but sales were high or if sales are never made then lowest labour cost) 
    
    for x in range(1,len(keys)):
        current = percentages[keys[x]]
        
        if ((current<worstSoFar and (current<0)) # current is a more negative value
        or ((current>worstSoFar) and (worstSoFar>0))): # current is a higher percentage of labour as no negative number has been found yet
            worstSoFar = current
            worstHour = keys[x]
            
        if ((current<bestSoFar and current>0) # current is a lower labour/sales percentage 
        or (current>bestSoFar and bestSoFar<0)): # best so far is no sales so current is either lower labour cost or increased sales
            bestSoFar = current
            bestHour = keys[x]
    
    return [bestHour, worstHour]

def main(path_to_shifts, path_to_sales):
    """
    Do not touch this function, but you can look at it, to have an idea of
    how your data should interact with each other
    """

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "C:\\Users\\ukmsh\\Downloads\\Tenzo Coding Test\\Tenzo Coding Test\\transactions.csv"
    path_to_shifts = "C:\\Users\\ukmsh\\Downloads\\Tenzo Coding Test\\Tenzo Coding Test\\work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)


# Please write you name here: Sharon Mazor
