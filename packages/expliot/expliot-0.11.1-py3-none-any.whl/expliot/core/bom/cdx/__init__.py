"""Support for CycloneDX BOM."""

import json
from datetime import UTC, datetime, timezone
from uuid import uuid4

import jsonschema

from .. import DirEnumerator
from .json14schema import json14schema

# """
# **EXPLIoT CycloneDX Property Taxonomy**
#
# +-------------------+--------------------------------------------------------------+
# |     Property      |                      Description                             |
# +===================+==============================================================+
# | expliot:file:path | The path of the file in the package (software, firmware etc) |
# +-------------------+--------------------------------------------------------------+
# | expliot:file:mode | The file mode string as on a Linux system (rwx)              |
# +-------------------+--------------------------------------------------------------+
# | expliot:file:size | The size of the file in bytes                                |
# +-------------------+--------------------------------------------------------------+
# """
XPROP_PATH = "expliot:file:path"
XPROP_MODE = "expliot:file:mode"
XPROP_SIZE = "expliot:file:size"

VER14 = "1.4"
VERSIONS = {VER14: dict(jsonschema=json14schema)}


class JKeywords:
    """Namespace for JSON keywords defined in CycloneDX JSON BOM format."""

    BOMFMT = "bomFormat"
    SPECVERSION = "specVersion"
    SERIALNUM = "serialNumber"
    VERSION = "version"
    METADATA = "metadata"
    TIMESTAMP = "timestamp"
    TOOLS = "tools"
    EXPLIOT_VENDOR = "EXPLIoT"
    EXPLIOT_TOOL = "EXPLIoT Framework"
    COMPONENTS = "components"

    # Component Valid Properties
    ADVISORIES = "advisories"
    AFFECTS = "affects"
    AGGREGATE = "aggregate"
    ALIASES = "aliases"
    ALG = "alg"
    ALGORITHM = "algorithm"
    ANALYSIS = "analysis"
    ANCESTORS = "ancestors"
    ASSEMBLIES = "assemblies"
    AUTHENTICATED = "authenticated"
    AUTHOR = "author"
    AUTHORS = "authors"
    BOMREF = "bom-ref"
    CERTIFICATEPATH = "certificatePath"
    CHAIN = "chain"
    CLASSIFICATION = "classification"
    COMMENT = "comment"
    COMMITTER = "committer"
    COMMITS = "commits"
    COMPONENT = "component"
    COMPONENTS = "components"
    COMPOSITIONS = "compositions"
    CONTACT = "contact"
    CONTENT = "content"
    CONTENTTYPE = "contentType"
    COPYRIGHT = "copyright"
    CPE = "cpe"
    CREATED = "created"
    CREDITS = "credits"
    CRV = "crv"
    CWES = "cwes"
    DATA = "data"
    DEPENDENCIES = "dependencies"
    DEPENDSON = "dependsOn"
    DESCENDANTS = "descendants"
    DESCRIPTION = "description"
    DETAIL = "detail"
    DIFF = "diff"
    E = "e"
    EMAIL = "email"
    ENCODING = "encoding"
    ENDPOINTS = "endpoints"
    EVIDENCE = "evidence"
    EXCLUDES = "excludes"
    EXPRESSION = "expression"
    EXTERNALREFS = "externalReferences"
    FEATUREDIMAGE = "featuredImage"
    FLOW = "flow"
    GROUP = "group"
    HASHES = "hashes"
    ID = "id"
    INDIVIDUALS = "individuals"
    JUSTIFICATION = "justification"
    KEYID = "keyId"
    KTY = "kty"
    LICENSE = "license"
    LICENSES = "licenses"
    MANUFACTURE = "manufacture"
    MESSAGE = "message"
    METHOD = "method"
    MIME_TYPE = "mime-type"
    N = "n"
    NAME = "name"
    NOTES = "notes"
    ORGANIZATIONS = "organizations"
    PATCH = "patch"
    PATCHES = "patches"
    PEDIGREE = "pedigree"
    PHONE = "phone"
    PROPERTIES = "properties"
    PROVIDER = "provider"
    PUBLICKEY = "publicKey"
    PUBLISHED = "published"
    PUBLISHER = "publisher"
    PURL = "purl"
    RATINGS = "ratings"
    RANGE = "range"
    RECOMMENDATION = "recommendation"
    REF = "ref"
    REFERENCES = "references"
    RELEASENOTES = "releaseNotes"
    RESOLVES = "resolves"
    RESPONSE = "response"
    SCOPE = "scope"
    SCORE = "score"
    SERVICES = "services"
    SEVERITY = "severity"
    SIGNATURE = "signature"
    SIGNERS = "signers"
    SOCIALIMAGE = "socialImage"
    SOURCE = "source"
    STATE = "state"
    STATUS = "status"
    SUPPLIER = "supplier"
    SWID = "swid"
    TAGID = "tagId"
    TAGS = "tags"
    TAGVERSION = "tagVersion"
    TEXT = "text"
    TIMESTAMP = "timestamp"
    TITLE = "title"
    TOOLS = "tools"
    TYPE = "type"
    UID = "uid"
    UPDATED = "updated"
    URL = "url"
    VALUE = "value"
    VARIANTS = "variants"
    VECTOR = "vector"
    VENDOR = "vendor"
    VERSION = "version"
    VERSIONS = "versions"
    VULNERABILITIES = "vulnerabilities"
    X = "x"
    XTRUSTBOUNDARY = "x-trust-boundary"
    Y = "y"

    # Valid Algos as of 1.4
    ALGO_MD5 = "MD5"
    ALGO_SHA1 = "SHA-1"
    ALGO_SHA256 = "SHA-256"
    ALGO_SHA384 = "SHA-384"
    ALGO_SHA512 = "SHA-512"
    ALGO_SHA3_256 = "SHA3-256"
    ALGO_SHA3_384 = "SHA3-384"
    ALGO_SHA3_512 = "SHA3-512"
    ALGO_BLAKE2B_256 = "BLAKE2b-256"
    ALGO_BLAKE2B_384 = "BLAKE2b-384"
    ALGO_BLAKE2B_512 = "BLAKE2b-512"
    ALGO_BLAKE3 = "BLAKE3"

    # types
    APPLICATION = "application"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    CONTAINER = "container"
    OS = "operating-system"
    DEVICE = "device"
    FIRMWARE = "firmware"
    FILE = "file"


class CycloneDXBOM:
    """CycloneDX BOM Object.

    It implements a callback for DirEnumerator for creating
    the SBOM.

    **EXPLIoT CycloneDX Property Taxonomy**

    +-------------------+--------------------------------------------------------------+
    |     Property      |                      Description                             |
    +===================+==============================================================+
    | expliot:file:path | The path of the file in the paxkage (software, firmware etc) |
    +-------------------+--------------------------------------------------------------+
    | expliot:file:mode | The file mode string as on a Linux system (rwx)              |
    +-------------------+--------------------------------------------------------------+
    | expliot:file:size | The size of the file in bytes                                |
    +-------------------+--------------------------------------------------------------+
    """

    def __init__(self):
        """Initialize the JSON format."""
        self.bom = None
        self.version = None
        self.count = {"files": -1, "dirs": -1, "hiddenfiles": -1,
                      "hiddendirs": -1, "symlinks": -1}

    def initbom(self, specversion, rootdir=None):
        """Create a new BOM Object and fill it with all file data.

        Only if rootdir is specified.

        Args:
            specversion (str): The CycloneDX Specification Version
        Returns:
             Nothing
        Raises:
            ValueError - if specversion is not supported

        """
        if specversion not in VERSIONS:
            raise ValueError(f"Unsupported CycloneDX version ({specversion})")

        self.version = specversion if specversion else "1.4"

        self.bom = {
            "bomFormat": "CycloneDX",
            "specVersion": self.version,
            "serialNumber": uuid4().urn,
            "version": 1,
            "metadata": {
                "timestamp": str(datetime.now(UTC).timestamp()),
                "tools": [dict(vendor="EXPLIoT", name="EXPLIoT Framework")],
            },
            "components": [],
        }
        if rootdir:
            self.generate_from_dir(rootdir)

    def enumcb(self, rootdir, currentdir, filedata):
        """Callback for DirEnumerator.enumerate().

        Return the component data about the file
        """
        component = Component(JKeywords.FILE, **filedata)
        self.bom[JKeywords.COMPONENTS].append(component.getdict())

    def generate_from_dir(self, rootdir):
        """Generate CycloneDX BOM from the contents of a directory.

        Args:
            rootdir (str): The root directory to start enumerating
                        and generating the BOM data
        Returns:
             Nothing

        """
        itr = DirEnumerator()
        itr.enumerate(rootdir, self.enumcb)
        self.count = itr.count

    def validate(self):
        """Validate the format with the json schema of the initialized spec version.

        Returns:
            Nothing

        Raises:
            ValidationError
            (https://python-jsonschema.readthedocs.io/en/stable/validate/)

        """
        jsonschema.validate(self.bom, VERSIONS[self.version]["jsonschema"])

    def getbom(self, validate=True, jsonfmt=False):
        """Returns the CycloneDX BOM in Dict or JSON format.

        Args:
            validate(bool): Validate the format with the schema. Default is True
            jsonfmt(bool): Return BOM in JSON format or Dict object. Default is False

        Returns:
            BOM in JSON string

        """
        bom = None
        if validate is True:
            self.validate()
        if jsonfmt is True:
            bom = json.dumps(self.bom)
        else:
            bom = self.bom
        return bom

    def writebom(self, file, validate=True, indent=4):
        """Write BOM in JSON format to a file.

        Args:
            file(str): File path to write the JSON to
            validate(bool): Validate the format with the schema. Default is True
            indent(int): Indentation limit to improve readability. Default is 4

        Returns:
            Nothing

        """
        if validate is True:
            self.validate()
        with open(file, mode="w", encoding="utf-8") as write_file:
            json.dump(self.bom, write_file, indent=indent)

    def total_files(self):
        """Returns the total number of files in the root dir.

        Args:
            Nothing

        Returns:
            (int) Total number of files or -1 if BOM not generated

        """
        return self.count["files"]

    def total_dirs(self):
        """Returns the total number of dirs in the root dir.

        Args:
            Nothing

        Returns:
            (int) Total number of dirs or -1 if BOM not generated

        """
        return self.count["dirs"]

    def total_hiddenfiles(self):
        """Returns the total number of hidden files in the root dir.

        Args:
            Nothing

        Returns:
            (int) Total number of hidden files or -1 if BOM not generated

        """
        return self.count["hiddenfiles"]

    def total_hiddendirs(self):
        """Returns the total number of hidden dirs in the root dir.

        Args:
            Nothing

        Returns:
            (int) Total number of hidden dirs or -1 if BOM not generated

        """
        return self.count["hiddendirs"]

    def total_symlinks(self):
        """Returns the total number of symlinks in the dir.

        Args:
            Nothing

        Returns:
            (int) Total number of symlinks or -1 if BOM not generated

        """
        return self.count["symlinks"]


class Component:
    """Class that represents a CycloneDX component."""

    def __init__(self, comptype, **kwargs):
        """Create a Component dict object.

        Args:
            comptype (str): Component type as per the spec.
            kwargs: type specific attributes as per the spec
        Returns:
            Nothing
        Raises:
            ValueError - If type is not supported

        """
        self.data = {}

        if comptype == JKeywords.FILE:
            self.create_file(**kwargs)
        else:
            # As of now we only support file component creation
            raise ValueError(f"Unsupported Component type ({comptype})")

    def create_file(self, **kwargs):
        """Create a file component from the passed arguments.

        Args:
            kwargs: file component specific attributes as per the spec
        Returns:
            bool - True if component was created successfully, False otherwise

        """
        self.data[JKeywords.TYPE] = JKeywords.FILE
        self.data[JKeywords.NAME] = kwargs["name"]
        self.data[JKeywords.MIME_TYPE] = kwargs["mime"]
        self.data[JKeywords.DESCRIPTION] = kwargs["descr"]
        if kwargs["sha1"]:
            self.data[JKeywords.HASHES] = [
                {"alg": JKeywords.ALGO_SHA1, "content": kwargs["sha1"]}
            ]
        if kwargs["sha256"]:
            self.data[JKeywords.HASHES].append(
                {"alg": JKeywords.ALGO_SHA256, "content": kwargs["sha256"]}
            )
        self.data[JKeywords.PROPERTIES] = [
            {"name": XPROP_PATH, "value": kwargs["relpath"]}
        ]
        if kwargs["mode"]:
            self.data[JKeywords.PROPERTIES].append(
                {"name": XPROP_MODE, "value": kwargs["mode"]}
            )
        if kwargs["size"]:
            self.data[JKeywords.PROPERTIES].append(
                {"name": XPROP_SIZE, "value": kwargs["size"]}
            )

    def getdict(self):
        """Returns the dict member self.data.

        Returns:
            dict - the dict member self.data

        """
        return self.data
