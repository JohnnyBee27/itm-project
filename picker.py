import datetime


time_range = range(8,18)

availabilities = dict()
time_list = list()
count_list = list()

def listReset():
    for hour in time_range:
        availabilities.setdefault('{0:02}:00'.format(hour),0)
        availabilities.setdefault('{0:02}:30'.format(hour),0)

    for hour in time_range:
        time_list.append('{0:02}:00'.format(hour))
        time_list.append('{0:02}:30'.format(hour))
        
def updateLists(booking_time):
    for i in booking_time:
        availabilities[i] = availabilities[i] + 1
    
def bestTime():
    list_index = list()
    best_times = list()
    
    count_list = list(availabilities.values())

    for i in range(len(count_list)):
        if count_list[i] == max(count_list):
            list_index.append(i)

    for j in list_index:
        best_times.append(time_list[j])
        
    return ', '.join(best_times)
        

        

    

    
