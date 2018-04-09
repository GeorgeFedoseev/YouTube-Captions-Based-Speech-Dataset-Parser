import os
import sys

import time
import datetime

import csv

from Queue import *

import threading

import const



# CSV MEM ABSTRACTION with syncing with filesystem every n seconds
# {filename: {rows: [], queue: } }
csv_files_dict = {}

csv_files_dict_rlock = threading.RLock()

csv_worker_thread = None





    #print('csv utils setup 2')

    #print('csv utils setup - end')




# init from files
def init_csv_from_file(csv_path):    

    # lazy init
    maybe_start_csv_queue_worker_thread()

    with csv_files_dict_rlock:

        if csv_path in csv_files_dict:
            return # already inited

        #print("init csv %s" % csv_path)

        # create csv file if not exists
        if not os.path.exists(csv_path):
            open(csv_path, 'a').close()



        f = open(csv_path, "r+")
        csv_reader = csv.reader(f)

        #print("init_csv_from_file - 1")
        rows = list(csv_reader)
        rows = [r for r in rows if len(r) > 0 and r[0].strip() != ""]
        #print("init_csv_from_file - 2")



        
        csv_files_dict[csv_path] = {
            "rows": rows,
            "queue": Queue(),
            "lock": threading.RLock()
        }

        f.close()

def update_from_file(csv_path):
    # in case if first time
    init_csv_from_file(csv_path)

    f = open(csv_path, "r+")
    csv_reader = csv.reader(f)

    #print("init_csv_from_file - 1")
    rows = list(csv_reader)
    rows = [r for r in rows if len(r) > 0 and r[0].strip() != ""]
    with csv_files_dict[csv_path]["lock"]:
        csv_files_dict[csv_path]["rows"] = rows




def sync_csv_to_file(csv_path):
    if not (csv_path in csv_files_dict):
        return # cant write - dont have data

    #print('sync_csv_to_file - start')

    lines = []
    for row in csv_files_dict[csv_path]["rows"]:
        lines.append(','.join(row))


    f = open(csv_path, "w")
    f.write('\n'.join(lines)+'\n')
    f.close()
    
    #print('sync_csv_to_file - end')

# writer worker
def csv_queue_worker():
    while 1:
        
        

        #print("perform queue operations - wait for lock")
        with csv_files_dict_rlock:
            update_from_file(const.KWDS_TO_SEARCH)

            #print("perform queue operations")
            for csv_path, item in csv_files_dict.iteritems():

                performed_count = 0

                # perform all operaions in queue
                while 1:
                    q = item["queue"]
                    if q.empty():
                        break

                    f, args = q.get()
                    csv_files_dict[csv_path]["rows"] = f(*([csv_files_dict[csv_path]["rows"]]+args))
                    performed_count += 1
                    q.task_done()   

                # sync changes to file
                if performed_count > 0:
                    sync_csv_to_file(csv_path)

             # finished queue
            # check if main thread is still alive
            is_main_thread_active = lambda : any((i.name == "MainThread") and i.is_alive() for i in threading.enumerate())
            #print("is_main_thread_active: %s" % str(is_main_thread_active()))
            if not is_main_thread_active():
                print ("main thread is not alive - exit")
                sys.exit()

        #print ("performed %i queue operations" % performed_count)



        time.sleep(0.1) 
        

def maybe_start_csv_queue_worker_thread():
    global csv_worker_thread

    if csv_worker_thread == None:
        print 'start_csv_queue_worker_thread'
        csv_worker_thread = threading.Thread(target=csv_queue_worker)
        csv_worker_thread.daemon = False
        csv_worker_thread.start()

    return csv_worker_thread

# CSV OPERATIONS


# read operations
def read_all(csv_path):
    #print("read_all")

    # lazy init
    init_csv_from_file(csv_path)

    #print("read_all2")

    # wait untill all queued operations will finish
    with csv_files_dict[csv_path]["lock"]:
        #print("read_all3 - wait for queue ops: %i" % csv_files_dict[csv_path]["queue"].qsize())
        csv_files_dict[csv_path]["queue"].join()
        #print("read_all4")
        # now read latest data
        return csv_files_dict[csv_path]["rows"]


def get_column_csv(csv_path, column_index):
    data = read_all(csv_path)

    column = []

    for row in data:
        if len(row) > column_index:
            column.append(row[column_index])
    return column

def get_row_in_csv(csv_path, row_first_cell_val):
    data = read_all(csv_path)

    for row in data:
        if len(row) > 0 and row[0] == row_first_cell_val:
            return row
    return None

def is_item_in_csv(csv_path, item):
    get_row_in_csv(csv_path, item) != None

# modify operations
def clear_csv(csv_path):
    # lazy init
    init_csv_from_file(csv_path)

    def _clear_op(lst):
        return []

    with csv_files_dict[csv_path]["lock"]:
        csv_files_dict[csv_path]["queue"].put((_clear_op, []))



def prepend_rows_to_csv(csv_path, rows):  
    #print("append_rows_to_csv: %s %i" % (csv_path, len(rows)))

    # lazy init
    init_csv_from_file(csv_path)

    def _append_op(lst, rows):
        return rows+lst

    #print("append_rows_to_csv - wait lock")
    with csv_files_dict[csv_path]["lock"]:
        #print("append_rows_to_csv - got lock")
        csv_files_dict[csv_path]["queue"].put((_append_op, [rows]))    

def append_rows_to_csv(csv_path, rows):  
    #print("append_rows_to_csv: %s %i" % (csv_path, len(rows)))

    # lazy init
    init_csv_from_file(csv_path)

    def _append_op(lst, rows):
        return lst + rows

    #print("append_rows_to_csv - wait lock")
    with csv_files_dict[csv_path]["lock"]:
        #print("append_rows_to_csv - got lock")
        csv_files_dict[csv_path]["queue"].put((_append_op, [rows]))    

def write_rows_to_csv(csv_path, rows):
    #print("write_rows_to_csv: %s %i" % (csv_path, len(rows)))

    # lazy init
    init_csv_from_file(csv_path)

    def _write_op(lst, rows):
        return rows

    #print("write_rows_to_csv - wait lock")
    with csv_files_dict[csv_path]["lock"]:
        #print("write_rows_to_csv - got lock")
        csv_files_dict[csv_path]["queue"].put((_write_op, [rows]))   


def prepend_column_to_csv(csv_path, column):
    #print("append_column_to_csv")
    rows = []
    for val in column:
        rows.append([val])
    prepend_rows_to_csv(csv_path, rows)

def append_column_to_csv(csv_path, column):
    #print("append_column_to_csv")
    rows = []
    for val in column:
        rows.append([val])
    append_rows_to_csv(csv_path, rows)

def write_column_to_csv(csv_path, column):
    #print("write_column_to_csv")
    rows = []
    for val in column:
        rows.append([val])
    write_rows_to_csv(csv_path, rows)


def add_row_to_csv(csv_path, row):
    append_rows_to_csv(csv_path, [row])


def pop_first_row_in_csv(csv_path):    
    first_row = None    

    data = read_all(csv_path)

    if len(data) == 0:
        return None

    #print("pop_first_row_in_csv - get: %i" % len(data))

    first_row = data.pop(0)
    remove_row_by_first_val(csv_path, first_row[0])

    return first_row    

def remove_row_by_first_val(csv_path, val):

    # lazy init
    init_csv_from_file(csv_path)

    def _remove_row_op(lst, val):        
        new_data = []
        for row in lst:
            if not (len(row) > 0 and row[0] == val):
                new_data.append(row)

        return new_data

    with csv_files_dict[csv_path]["lock"]:        
        csv_files_dict[csv_path]["queue"].put((_remove_row_op, [val]))     
    
    



