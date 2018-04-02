import os

def folder_video_ids():
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    
    output = ""

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue        

        stats_path = os.path.join(item_path, "stats.csv")
        
        
        if os.path.exists(stats_path):
            output += item+"\n"
        

    print output   
    


if __name__ == '__main__':
    folder_video_ids()