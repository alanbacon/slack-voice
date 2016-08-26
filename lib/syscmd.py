import sys, subprocess, shlex

# define a function to remove any newline characters from the end of a string
def stripNewLine(string):
    # if the last character is the newline character
    if (string[-1] == '\n'):
        # then return everything except the last character
        return string[0:-1]
    else:
        # else return the unmodified string
        return string


# define a system call function to abstract python's subproccess object
def syscall(cmd, stdin='', **kwargs):
    # see if it has been requested to strip off new lines
    if 'strip' in kwargs:
        strip = kwargs['strip']
    else:
        strip = False

    # systems text encoding scheme    
    encoding = sys.getdefaultencoding()

    # use shlex to split command into individual arguments
    # define that any ouput or error message to be piped back into the proc object

    proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # the second output argument could be an error message (if one was given)
    out, errmsg = proc.communicate(input=stdin.encode('utf-8'))
    exitcode = proc.returncode
    if (exitcode == 0):
        if (type(out) != str):
            outstr = out.decode(encoding)
        else:
            outstr = out
        if strip:
            outstr = stripNewLine(outstr)
        return outstr
    else:
        #raise Exception('system call had a non-zero return code')
        if (type(errmsg) != str):
            errmsg = errmsg.decode(encoding)
        raise Exception('syscall error:\n' + errmsg)

