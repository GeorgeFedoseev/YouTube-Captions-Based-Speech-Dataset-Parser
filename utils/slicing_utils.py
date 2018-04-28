import re
import wave
import webrtcvad

def is_bad_piece(audio_duration, transcript):   

    MAX_SECS = 20
    MIN_SECS = 3    
    
    MIN_SEC_PER_SYMBOL = 0.04375

    # remove audios that are shorter than 0.5s and longer than 20s.
    # remove audios that are too short for transcript.
    if audio_duration > MIN_SECS and audio_duration < MAX_SECS and transcript!="" and audio_duration/len(transcript) > MIN_SEC_PER_SYMBOL:
        return True
    return False

def is_bad_subs(subs_text):
    bad = False

    if subs_text.strip() == "":
        bad = True

    if len(re.findall(r'[0-9]+', subs_text)) > 0:
        bad = True
    if len(re.findall(r'[A-Za-z]+', subs_text)) > 0:
        bad = True

    return bad


def slice_audio_by_silence(wave_obj, min_audio_length=5, max_audio_length=10, vad_silence_volume_param=1):
    SPEECH_FRAME_SEC = 0.01
    SILENCE_DETECT_FRAMES_COUNT = 1
    SPEECH_DETECT_FRAMES_COUNT = 1

    vad = webrtcvad.Vad(vad_silence_volume_param)

    samples_per_second = wave_obj.getframerate()    
    samples_per_frame = int(SPEECH_FRAME_SEC*samples_per_second)
    total_samples = wave_obj.getnframes()    
    
    wave_obj.setpos(0)

    out_pieces = []


    current_piece_start_sec = 0    
    current_piece_length_sec = 0

    current_piece_samples = ""

    total_length = 0

    searching_for_speech = False
    searching_for_silence = True
    have_current_piece = False

    is_speech_frame_count = 0
    is_silence_frame_count = 0

    silence_start_sec = 0
    speech_start_sec = 0

    
    while wave_obj.tell() < total_samples:        
        wav_samples = wave_obj.readframes(samples_per_frame)
        current_frame_length_sec = float(samples_per_frame)/samples_per_second
        
        try:
            is_speech = vad.is_speech(wav_samples, samples_per_second)
        except Exception as ex:
            #print("VAD Exception: %s" % str(ex))
            continue

        # update frame count buffers
        if is_speech:
            is_silence_frame_count = 0
            is_speech_frame_count += 1
            if is_speech_frame_count == 1:
                speech_start_sec = float(wave_obj.tell())/samples_per_second
        else:
            is_silence_frame_count += 1
            is_speech_frame_count = 0
            if is_silence_frame_count == 1:
                silence_start_sec = float(wave_obj.tell())/samples_per_second


        # when searching for piece start
        if not have_current_piece:
            # searching for silence to start piece
            if searching_for_silence:
                if is_silence_frame_count >= SILENCE_DETECT_FRAMES_COUNT:
                    # found silence, now start searching for speech start
                    have_current_piece = False
                    searching_for_silence = False
                    searching_for_speech = True
                    current_piece_start_sec = silence_start_sec
                    

            # searching for speech after silence
            elif searching_for_speech:
                if is_speech_frame_count >= SPEECH_DETECT_FRAMES_COUNT:
                    # start piece here
                    
                    current_piece_length_sec = 0
                    current_piece_samples = ""

                    # and start recoding piece
                    have_current_piece = True
                    searching_for_silence = False
                    searching_for_speech = False

        else:
            # recoding piece

            # update current piece data
            current_piece_length_sec += current_frame_length_sec
            current_piece_samples += wav_samples

            # when searching for piece end
            if (current_piece_length_sec > min_audio_length):
                if current_piece_length_sec < max_audio_length:
                    # check for silence
                    if is_silence_frame_count >= SILENCE_DETECT_FRAMES_COUNT:
                        # stop piece here
                        out_pieces.append({
                            "start": current_piece_start_sec,
                            "end": current_piece_start_sec+current_piece_length_sec,
                            "samples": current_piece_samples
                            })
                        total_length += current_piece_length_sec
                        # and reset current piece
                        current_piece_samples = ""
                        current_piece_start_sec = 0
                        current_piece_length_sec = 0

                        # begin searching for next piece start
                        have_current_piece = False
                        searching_for_speech = False
                        searching_for_silence = True

                # reached max length - reset searching
                else:
                    print("WARNING: reached max length of piece - reset searching for piece start from %f" % (current_piece_start_sec+1))

                    # reset to time of current piece start + 1 sec and start searching for piece beginning
                    wave_obj.setpos(int((current_piece_start_sec+1)*samples_per_second))
                    have_current_piece = False
                    searching_for_speech = False
                    searching_for_silence = True



    return out_pieces, total_length/len(out_pieces)