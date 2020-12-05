import shelve

with shelve.open('test_shelve.db') as db:
    print("current value " + str(db['test_key']))
    db['test_key'] = db['test_key'] + 1
    print("next value" + str(db['test_key']))