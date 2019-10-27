import json
import matplotlib.pyplot as plt
import datetime
from datetime import datetime, date, timedelta
import mplcursors
import pandas as pd


with open('data.json') as json_data:
    mock = json.load(json_data)

def stay(stay_id):
    """"
    stay_id(str): name of person who booked event
    """
    time  = []
    guests = []
    urls = []
    tot_guests = []
    tot_guest = int(json.dumps(mock['Airbnb'][stay_id]['Tot_Guests']))

    sdate = json.dumps(mock['Airbnb'][stay_id]['Start_Time'], indent=2).replace("_", " ").replace('"', "")
    if sdate == "present":
        return
    else:
        sdate = datetime.strptime(sdate, '%Y-%m-%d %H:%M')

    edate = json.dumps(mock['Airbnb'][stay_id]['End_Time'], indent=2).replace("_", " ").replace('"', "")
    if edate == 'present':
        edate = datetime.now()
        edate = datetime.strftime(edate, '%Y-%m-%d %H:%M')
    else:
        edate = datetime.strptime(edate, '%Y-%m-%d %H:%M')



    entries = json.dumps(mock['Airbnb'][stay_id]['Entries'], indent=2).replace(" ", "").replace("[", "").\
        replace("]", "").replace("}", "").replace("[", "").replace("{", "").replace("\n", "").split(",")
    for i in range(len(entries)):
        entry = entries[i].replace('"', "").replace("_", " ").split(":", 1)
        if entry[0] == 'TimeStamp':
            time.append(datetime.strptime(entry[1], '%Y-%m-%d %H:%M'))
            tot_guests.append(tot_guest)
        elif entry[0] == 'NumGuests':
            guests.append(int(entry[1]))
        else:
            urls.append(entry[1])

    too_many = [] #value of guests (when exceeding max)
    too_many_time = [] #date where value of guests exceeds max
    days = [] #all days at airbnb

    fig, ax = plt.subplots()

    delta = edate.date() - sdate.date()  # as timedelta
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        days.append(day.date())

    ax.plot(time, guests, 'bo')
    ax.plot_date(time, tot_guests, 'r--', label="Max capacity")
    ax.plot_date(time, guests, 'k', label="Current capacity")

    # find dates where number of guests exceeded expected capacity
    for i in range(len(time)):
        if guests[i] > tot_guest:
            too_many.append(guests[i])
            too_many_time.append(time[i])

    ax.plot(too_many_time, too_many, 'ro')

    plt.ylabel('Number of guests')
    plt.xlabel('Time')
    plt.title('Number of Guests during Airbnb stay')
    plt.legend("Num_Guests", "Max_Guests")
    plt.xticks(days, rotation=30)

    #fig.canvas.mpl_connect('button_press_event', on_click)

    mplcursors.cursor(ax).connect(
        "add", lambda sel: sel.annotation.set_text(urls[int(round(sel.target.index, 0))]))
    ax.legend()
    plt.show()

    data = {'Time': time, 'Guests': guests, 'Urls': urls}
    df = pd.DataFrame(data)
    print(df)

stay("Kevin3")



