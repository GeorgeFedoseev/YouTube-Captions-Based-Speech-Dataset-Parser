from python_speech_features import mfcc
import numpy as np
import scipy.io.wavfile as wav
import sys
import os
import csv

def audioToInputVector(audio, fs, numcep, numcontext):       

        # Get mfcc coefficients
        features = mfcc(audio, samplerate=fs, numcep=numcep)

        # We only keep every second feature (BiRNN stride = 2)
        features = features[::2]

        # One stride per time step in the input
        num_strides = len(features)

        # Add empty initial and final contexts
        empty_context = np.zeros((numcontext, numcep), dtype=features.dtype)
        features = np.concatenate((empty_context, features, empty_context))

        # Create a view into the array with overlapping strides of size
        # numcontext (past) + 1 (present) + numcontext (future)
        window_size = 2*numcontext+1
        train_inputs = np.lib.stride_tricks.as_strided(
            features,
            (num_strides, window_size, numcep),
            (features.strides[0], features.strides[0], features.strides[1]),
            writeable=False)

        # Flatten the second and third dimensions
        train_inputs = np.reshape(train_inputs, [num_strides, -1])

        # Whiten inputs (TODO: Should we whiten?)
        # Copy the strided array so that we can write to it safely
        train_inputs = np.copy(train_inputs)
        train_inputs = (train_inputs - np.mean(train_inputs))/np.std(train_inputs)

        # Return results
        return train_inputs

def audiofile_to_input_vector(audio_filename, numcep, numcontext):
    r"""
    Given a WAV audio file at ``audio_filename``, calculates ``numcep`` MFCC features
    at every 0.01s time step with a window length of 0.025s. Appends ``numcontext``
    context frames to the left and right of each time step, and returns this data
    in a numpy array.
    """
    # Load wav files
    fs, audio = wav.read(audio_filename)

    return audioToInputVector(audio, fs, numcep, numcontext)

def source_lower_than_target_bad_condition(wav_file, transcript):
    source = audiofile_to_input_vector(wav_file, 26, 9)
    source_len = len(source)
    #print 'transcript for '+wav_file+': '+transcript            
    target_len = len(transcript)

    return source_len < target_len

def remove_source_lower_than_target():
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    videos_data_dir = os.path.join(curr_dir_path, "data/")

    total_scanned = 0
    bad = 0

    for item in os.listdir(videos_data_dir):
        item_path = os.path.join(videos_data_dir, item)

        if not os.path.isdir(item_path):
            continue        

        parts_path = os.path.join(item_path, "parts.csv")

        if not os.path.exists(parts_path):
            continue

        f = open(parts_path, "r")
        parts = list(csv.reader(f))
        f.close()

        f = open(parts_path, "w")
        writer = csv.writer(f)

        
        for row in parts:
            if len(row) < 3:
                continue

            total_scanned+=1

            wav_file = row[0]
            transcript = row[2]
            
            
            if source_lower_than_target_bad_condition(wav_file, transcript):
                bad+=1
                print "source_len < target_len "+str(float(bad)/total_scanned*100)+'% (of '+str(total_scanned)+')'
            else:
                writer.writerow(row)
        f.close()

remove_source_lower_than_target()