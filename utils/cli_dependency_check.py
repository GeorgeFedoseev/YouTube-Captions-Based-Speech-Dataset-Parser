import subprocess

class CLI_DependencyException(Exception):
    '''raise this when there's CLI dependency missing'''

def is_aria2c_installed():
    try:
        subprocess.check_output(['aria2c', '-h'], stderr=subprocess.STDOUT)        
    except Exception as ex:
        raise CLI_DependencyException('dependency is not installed: aria2c: '+str(ex))
        return False

    return True

def is_ffmpeg_installed():
    try:
        subprocess.check_output(['ffmpeg', '-h'], stderr=subprocess.STDOUT)        
    except Exception as ex:
        raise CLI_DependencyException('dependency is not installed: ffmpeg: '+str(ex))
        return False

    return True

def is_ytdownloader_installed():
    try:
        subprocess.check_output(['youtube-dl', '-h'], stderr=subprocess.STDOUT)        
    except Exception as ex:
        raise CLI_DependencyException('dependency is not installed: youtube-dl: '+str(ex))
        return False

    return True


if __name__ == "__main__":
    if is_ytdownloader_installed():
        print "ok"
    else:
        print "not installed"