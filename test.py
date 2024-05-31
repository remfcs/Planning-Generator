import sqlite3
import function_database

Data = 'data/test.sqlite3'
promo_pair = [['1A','2A']]

def make_association(Data, promo_pair):
    conn = sqlite3.connect(Data)
    for promo_list in promo_pair:
        slot_count = function_database.get_lv_slot_count(Data, promo_list)
        