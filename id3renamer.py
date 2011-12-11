#!/usr/bin/python

import os
import sys
import argparse
import id3reader
import unicodedata
 
# id3renamer, by jamesob
# based on loosely on original work by systems_glitch (systems.glitch@gmail.com)
# found here: http://bit.ly/tgxRyG
# 
# Use the ID3 tag of an mp3 file to rename all of the files in a specified
# directory.
# 
# The ID3 library used automatically chooses the appropriate version of ID3.
# You'll need a copy of Ned Batchelder's id3reader:
# 
# http://nedbatchelder.com/code/modules/id3reader.html
                
_desc = """Walk a directory recursively and rename each MP3 found according to
its ID3 tags."""

def buildParser():
    parser = argparse.ArgumentParser(description=_desc)
 
    parser.add_argument('path', 
                        action='store', 
                        type=str, 
                        help='Which directory to walk for MP3s.')
                          
    parser.add_argument('-d', '--dry-run',
                        action='store_const', 
                        const=True,
                        default=False,
                        dest='dry',
                        help='Do a dry run verbosely.')
                          
    parser.add_argument('-v', '--verbose',
                        action='store_const', 
                        const=True,
                        default=False,
                        dest='verbose',
                        help='Emit debugging information.')
                                          
    return parser
 

class ID3Renamer(object):

    def __init__(self, path, v=False, dry=False):
        self.path = path
        self.verbose = v
        self.dry = dry

    def _log(self, msg, v_only=False):
        """Log a message.

        :Parameters:
          - `v_only`: log only if in verbose mode.
        """

        if (not v_only) or (v_only and self.verbose):
            print(msg)
 
    def to_ascii(self, st):
        """Return an ascii representation of `st`."""

        if type(st) is unicode:
            return unicodedata.normalize('NFKD', st).encode('ascii', 'ignore')
        else:
            return st
                         
    def _getID3Name(self, old_name):
        id3r = id3reader.Reader(old_name)

        track_number = id3r.getValue('track') or "0"
        track_number = track_number.split("/")[0]
        title = id3r.getValue('title') or "No title"
        title = title.strip()

        return self.to_ascii("%s %s.mp3" % (track_number.zfill(2), title))

    def rename_file(self, name, root):
        if name.lower().endswith(".mp3"):
            old_name = os.path.join(root, name)
            new_name = os.path.join(root, self._getID3Name(old_name))

            if old_name != new_name:
                self._log("Renaming '%s'\n    with '%s'" \
                          % (old_name, new_name), v_only=True)

                if not self.dry:
                    try:
                        os.rename(old_name, new_name)
                    except OSError:
                        self._log("Couldn't rewrite '%s'." % old_name)
         
    def walk_dir(self):
        """Walk a directory recursively, renaming its contents based on ID3
        tags."""
     
        for root, dir_name, names in os.walk(self.path):
            for name in names:
                self.rename_file(name, root)
                
if __name__ == '__main__':
    args = buildParser().parse_args()
    renamer = ID3Renamer(args.path, 
                         args.verbose or args.dry, 
                         args.dry)
    renamer.walk_dir()
                
