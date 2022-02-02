import pickle
import pysic
import datetime as dt
test = pysic.core.core.Core('test', dt.date.today())

with open('/home/megavolts/Desktop/test.pkl', 'wb') as f:
    pickle.dump(test, f)

birthday = pysic.core.profile.Profile()

with open('/home/megavolts/Desktop/test2.pkl', 'wb') as f:
    pickle.dump(birthday, f)