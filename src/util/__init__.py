
import json
import os
import shutil



def ensure_folder_exists(inPath, wipe = False):
    path = os.path.expanduser(inPath)
    exists = os.path.exists(path)
    if wipe and exists:
        wipe_path(path)
        exists = False
    if not exists:
        os.makedirs(path)
    return path

def wipe_path(path = None, paths = None):
    def onerror(func, path, exc_info):
        # this is for windows, who doesn't like removing RO files
        os.chmod(path, 0o644)
        func(path)
    paths = paths or [ path ]
    for path in paths:
        assert(path not in [ None, '.', '/', '~', './', '..' ])
        if os.path.exists(path):
            shutil.rmtree(path, onerror=onerror)

def json_at_path(path, emptyIfMissing = False):
    if emptyIfMissing  and  not os.path.exists(path):
        return {}
    return json.loads(path_to_str(path))

def write_json_to_path(dictionary, path, pretty = False, skipIfNoDiff = False, overwriteReadonly = False):
    unserializable = None
    try:
        data = json.dumps(dictionary, sort_keys = pretty, indent = 4 if pretty else None, separators = (',', ': ') if pretty else None)
    except Exception as e:
        if str(e).endswith('JSON serializable'):
            unserializable = e
        else:
            raise
    if unserializable:
        raise Exception("unserializable object in dictionary: {}".format(str(unserializable)))
    return write_path(data,
                      path,
                      skipIfNoDiff = skipIfNoDiff,
                      overwriteReadonly = overwriteReadonly)

def write_path(inData, path, skipIfNoDiff = False, overwriteReadonly = False, writeReadonly = False):
    if isinstance(inData, str):
        data = inData.encode()
    else:
        data = inData
    if os.path.exists(path):
        if skipIfNoDiff:
            try:
                existing = path_to_data(path)
                if existing == data:
                    return False
            except:
                pass
        if overwriteReadonly:
            os.chmod(path, 0o644) # for windoze
            os.remove(path)
    with open(path, 'wb') as f:
        f.write(data)
    if writeReadonly:
        os.chmod(path, 0o444)
    return True

def path_to_data(path):
    with open(path, 'rb') as f:
        return f.read()

def path_to_str(path, emptyIfMissing = False):
    if emptyIfMissing and (not os.path.exists(path)):
        return ""
    with open(path, 'r') as f:
        return f.read()
