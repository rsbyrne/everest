###############################################################################
###############################################################################

import os
import subprocess
from subprocess import PIPE
import shutil
import glob

import numpy as np

from everest import disk

def frame_iterate(frames):
    frames = iter(frames)
    first = next(frames)
    if isinstance(first, tuple):
        initframe, prevtime = first
        yield initframe, 0.
        for frame, timestamp in frames:
            yield frame, timestamp - prevtime
            prevtime = timestamp
    else:
        yield first, 0.
        for frame in frames:
            yield frame, 1.

def process_durations(rawdurations, duration):
    rawdurations = np.array(rawdurations)
    weights = rawdurations / rawdurations.max()
    weights[0] = 1.
    return weights * duration / len(weights)   

def get_ffconcat(filedir, items, durations):
    randname = disk.tempname(_mpiignore_ = True)
    infile = os.path.join(filedir, randname + '.ffconcat')
    with open(infile, mode = 'w') as file:
        file.write('ffconcat version 1.0' + '\n')
        for item, duration in zip(items, durations):
            file.write('file ' + item + '\n')
            file.write('duration ' + str(duration) + '\n')
    return infile

def get_length(filename):
    # SingleNegationElimination@StackOverflow
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filename
        ]
    result = subprocess.run(cmd, stdout = PIPE, stderr = PIPE)
    return float(result.stdout)

def get_tempDir(outputPath):
    tempDir = os.path.join(outputPath, disk.tempname(_mpiignore_ = True))
    cleanup = lambda: shutil.rmtree(tempDir, ignore_errors = True)
    cleanup()
    os.makedirs(tempDir)
    return tempDir

def process_args(source, duration, outputPath):
    if isinstance(source, str):
        if os.path.isdir(source):
            mode = 'dir'
        else:
            mode = 'mov'
    else:
        mode = 'sav'
    if mode == 'mov':
        infile = source
        pts = duration / get_length(infile)
        cleanup = lambda: None
    else:
        pts = 1
        if mode == 'dir':
            loadDir = source
            rawdurations = None
        else:
            loadDir = get_tempDir(outputPath)
            frames, rawdurations = frame_iterate(source)
            for i, frame in enumerate(frames):
                frame.save(name, path = tempDir, add = i)
        searchpath = glob.glob(os.path.join(loadDir, '*.png'))
        items = sorted(os.path.basename(path) for path in searchpath)
        if rawdurations is None:
            rawdurations = [0., *[1. for _ in items]]
        durations = process_durations(rawdurations, duration)
        assert abs(sum(durations) - duration) < 1e-6
        infile = get_ffconcat(loadDir, items, durations)
        if mode == 'dir':
            cleanup = lambda: os.remove(infile)
    return infile, pts, cleanup

def animate(
        source,
        duration,
        name = None,
        outputPath = '.',
        overwrite = False,
        ):

    if name is None:
        name = disk.tempname(_mpiignore_ = True)

    outputPath = os.path.abspath(outputPath)
    outputFilename = os.path.join(outputPath, name + '.mp4')
    if not overwrite:
        if os.path.exists(outputFilename):
            raise Exception("Output file already exists!")

    try:
        cleanup = lambda: None
        infile, pts, cleanup = process_args(source, duration, outputPath)
        filters = ','.join([
            '"scale=trunc(iw/2)*2:trunc(ih/2)*2"',
            '"setpts=' + str(pts) + '*PTS"'
            ])
        cmd = ' '.join([
            'ffmpeg',
            '-y',
            '-i', infile,
            '-filter', filters,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-an',
            '"' + outputFilename + '"'
            ])
        completed = subprocess.run(
            cmd,
            stdout = PIPE, stderr = PIPE, shell = True, check = True,
            )

    finally:
        cleanup()

    return outputFilename

###############################################################################
###############################################################################
