#!/usr/bin/env python3
import os, shutil
removed = []
for root, dirs, files in os.walk('.', topdown=False):
    if '__pycache__' in dirs:
        path = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(path)
            removed.append(path)
        except Exception as e:
            print('ERR REMOVING', path, e)
    for f in files:
        if f.endswith('.pyc') or f.endswith('.pyo'):
            path = os.path.join(root, f)
            try:
                os.remove(path)
                removed.append(path)
            except Exception as e:
                print('ERR REMOVING', path, e)
print('Removed count:', len(removed))
for p in removed[:200]:
    print(p)
