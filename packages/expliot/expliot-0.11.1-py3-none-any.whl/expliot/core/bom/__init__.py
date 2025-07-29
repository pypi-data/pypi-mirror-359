"""Support for BOM functionality."""

import os
import stat
from hashlib import sha1, sha256

import magic


class DirEnumerator:
    """Enumerate a directory and get info on all the files and dirs recursively."""

    def __init__(self):
        """Initialize the enumeration."""
        self.root = ""
        self.files = {}
        self.count = {"files": 0, "dirs": 0, "hiddenfiles": 0,
                      "hiddendirs": 0, "symlinks": 0}

    def enumerate(self, directory, callback):
        """Enumerate a ditrctory.

        1. Enumerate the specified root dir recursively
        2. Get metadata of each file
        3. Call the callback method for each file and pass the metadata

        Args:
            directory (str): The directory to enumerate
            callback (method): The callback method to be called for each file.
                The format is callback(rootdir, currentdir, filedata)
                    - rootdir(str): Root directory path being enumerated
                    - currentdir(str): The current directory i.e. parent of the file
                    - filedata (dict): File metadata
                        name = File name(str)
                        abspath = Absolute path of the file (str)
                        relpath = Relative path of the file (from the root directory)
                        mode = File mode (str)
                        size = File size in bytes
                        symlink = Yes - True, No - False (bool)
                        mime = Mime-Type (str),
                        descr = Description from libmagic (str),
                        sha1 = SHA1 Hash (str),
                        sha256 = SHA256 Hash (str)

        Returns:
            Nothing
        Raises:
            ValueError - if the dir argument is not a valid directory i.e. doesn't exist

        """
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            raise ValueError(f"Couldn't find ({directory})")

        self.root = directory

        for curdir, subdirs, files in os.walk(self.root):
            # Update the counts
            updatedfiles = files
            self.count["dirs"] += len(subdirs)
            for sdir in subdirs:
                if sdir.startswith("."):
                    self.count["hiddendirs"] += 1
                if os.path.islink(f"{curdir}/{sdir}"):
                    # Treat symlink as file
                    updatedfiles.append(sdir)
                    self.count["dirs"] -= 1

            # Treat symlink to dir as a file too for the count
            self.count["files"] += len(updatedfiles)
            for file in updatedfiles:
                mode = size = mime = descr = sha_1 = sha_256 = None
                slink = False
                abspath = curdir + "/" + file
                relpath = abspath.replace(self.root, "")
                if not relpath.startswith("/"):
                    relpath = f"/{relpath}"
                if file.startswith("."):
                    self.count["hiddenfiles"] += 1
                if os.path.islink(abspath):
                    slink = True
                    actualpath = os.readlink(abspath)
                    self.count["symlinks"] += 1
                    # In case of broken symlink i.e. actual file does not exist
                    # magic raise FileNotFoundError.
                    # Check if the actual link inside the firmware directory
                    # exists, if not mention it as broken in description
                    mime = "inode/symlink"
                    descr = f"symbolic link to {actualpath.replace(self.root, '')}"
                    if actualpath.startswith("/"):
                        # Symlink to absolute path starting from root
                        actualpath = f"{self.root}/{actualpath}"
                    else:
                        # Symlink to relative path within the file system
                        actualpath = os.path.realpath(abspath)
                    if not os.path.exists(actualpath):
                        descr = f"broken {descr}"
                else:
                    # If not a symlink i.e. normal file then get below details
                    stats = os.stat(abspath)
                    mode = stat.filemode(stats.st_mode)
                    size = str(stats.st_size)
                    # Convert mime to lower case as the CycloneDX JSON 1.4 schema
                    # invalidates mime with Capital letters
                    # Check json14schema.py - "pattern": "^[-+a-z0-9.]+/[-+a-z0-9.]+$"
                    # mime, content-type as per rfcs (1341, 2045, 2046, 1049 etc.)
                    # is not case-sensitive
                    mime = f"{magic.from_file(abspath, mime=True)}".lower()
                    descr = magic.from_file(abspath)
                    msg1 = sha1()
                    msg2 = sha256()
                    fdesc = os.open(abspath, os.O_RDONLY)
                    fdata = os.read(fdesc, stats.st_size)
                    os.close(fdesc)
                    msg1.update(fdata)
                    msg2.update(fdata)
                    sha_1 = msg1.hexdigest()
                    sha_256 = msg2.hexdigest()

                self.files[relpath] = {
                    "name": file,
                    "abspath": abspath,
                    "relpath": relpath,
                    "mode": mode,
                    "size": size,
                    "symlink": slink,
                    "mime": mime,
                    "descr": descr,
                    "sha1": sha_1,
                    "sha256": sha_256,
                }

                callback(self.root, curdir, self.files[relpath])
