import os
import csv

import const

import sys



def check_paths(remove_if_nf=False):
    curr_dir_path = os.getcwd()
    export_csvs_dir = os.path.join(curr_dir_path, "export-sets/")

    for item in os.listdir(export_csvs_dir):
        csv_path = os.path.join(export_csvs_dir, item)

        #print 'process '+csv_path
        #print csv_path.split(".")[-1]
        if csv_path.split(".")[-1] != "csv":
            continue        


        

        f = open(csv_path, "r")
        parts = list(csv.reader(f))
        f.close()

        f = open(csv_path, "w")
        writer = csv.writer(f)
        for i, row in enumerate(parts):
            
            write = True
            if i > 0 and not os.path.exists(row[0]):
                print 'doesnt exist: '+row[0]
                if remove_if_nf:
                    write = False

            if write:
                writer.writerow(row)
            
        f.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-rm':
            check_paths(True)
        else:
            check_paths()
    else:
        check_paths()
        