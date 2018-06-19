import subprocess

def is_aria2c_installed():
    try:
        subprocess.check_output(['aria2c', '-h'], stderr=subprocess.STDOUT)        
    except Exception as ex:
        print 'ERROR: some of dependencies are not installed: aria2c: '+str(ex)
        return False

    return True

def is_ffmpeg_installed():
    try:
        subprocess.check_output(['ffmpeg', '-h'], stderr=subprocess.STDOUT)        
    except Exception as ex:
        print 'ERROR: some of dependencies are not installed: aria2c: '+str(ex)
        return False

    return True


if __name__ == "__main__":
    if is_ffmpeg_installed():
        print "ok"
    else:
        print "not installed"