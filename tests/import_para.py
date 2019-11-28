# import sys
# workPath = '/home/jovyan/workspace'
# if not workPath in sys.path:
#     sys.path.append(workPath)

from everest import disk
from everest import mpi
import os
import time

import random
import string

scriptText = 'my_var = "Hello world!"'

tempfilename = disk.tempname(extension = 'py')
print(tempfilename)
disk.write_file(tempfilename, scriptText, 'w')
time.sleep(1)
tempmodname = os.path.splitext(os.path.basename(tempfilename))[0]
exec('import ' + tempmodname)
imported = locals()[tempmodname]
print(imported.my_var)
disk.remove_file(tempfilename)

# tempfilename = 'testmodule.py'
# tempfilename = disk.tempname(extension = 'py')
# print(tempfilename)
# disk.write_file(tempfilename, scriptText, 'w')
# imported = disk.local_import(tempfilename)
# print(imported.my_var)
# disk.remove_file(tempfilename)

# with disk.TempFile(
#             scriptText,
#             extension = 'py',
#             mode = 'w'
#             ) \
#         as tempfile:
#     print(tempfile)
#     mpi.comm.barrier()
#     # imported = disk.local_import(tempfile)
#     # print(imported.my_var)
