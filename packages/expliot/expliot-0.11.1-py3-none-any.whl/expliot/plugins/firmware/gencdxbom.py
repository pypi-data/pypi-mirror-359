"""Sample test/plugin as demo."""

from expliot.core.bom.cdx import VER14, CycloneDXBOM
from expliot.core.tests.test import (
    LOGNO,
    LOGPRETTY,
    TCategory,
    Test,
    TLog,
    TTarget,
)

DEFAULT_PORT = 80


class GenCDXBom(Test):
    """Test class for the sample.

    Output Format:
    [
        {
            "files": 7,               # Total number of files (including normal, hidden and symlinks)
            "dirs": 4,                # Total number of directories
            "hiddenfiles": 2,         # Total number of hidden files
            "hiddentdirs": 1,         # Total number of hidden directories
            "symlinks": 1             # Total number of symlinks
        },
        # Below is the JSON format as per CycloneDX JSON Specification
        {
            "bomFormat": "CycloneDX",
            ...
            ...
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="gencdxbom",
            summary="Generate CycloneDX BOM from the firmware file-system",
            descr="This plugin generates a CycloneDX bom v1.4 JSON format from "
            "the provided file-system root directory of a firmware. ",
            author="Aseem Jakhar",
            email="aseem@expliot.io",
            ref=["https://cyclonedx.org/docs/1.4/json/"],
            category=TCategory(TCategory.FW, TCategory.SW, TCategory.COMPLIANCE),
            target=TTarget(TTarget.LINUX, TTarget.GENERIC, TTarget.LINUX),
        )

        self.argparser.add_argument(
            "-r",
            "--rootdir",
            required=True,
            help="The root directory of the file system.",
        )
        self.argparser.add_argument(
            "-f",
            "--file",
            help="File path to write the SBOM JSON to. If the file doesn't exist, it will "
            "it will create it. If it exists, it will be overwritten.",
        )
        self.argparser.add_argument(
            "-v", "--verbose", action="store_true", help="Show the SBOM data."
        )

    def execute(self):
        """Execute the test."""
        logargs = LOGNO
        TLog.generic(f"Generating CycloneDX bom of directory ({self.args.rootdir})")
        try:
            cdx = CycloneDXBOM()
            cdx.initbom(VER14, self.args.rootdir)
        except ValueError as err:
            self.result.setstatus(passed=False, reason=str(err))
        bom = cdx.getbom()

        self.output_handler(
            msg="Total count:",
            files=cdx.total_files(),
            dirs=cdx.total_dirs(),
            hiddenfiles=cdx.total_hiddenfiles(),
            hiddentdirs=cdx.total_hiddendirs(),
            symlinks=cdx.total_symlinks(),
        )
        if self.args.verbose:
            logargs = LOGPRETTY
        self.output_handler(logkwargs=logargs, **bom)
        if self.args.file:
            TLog.trydo(f"Writing SBOM JSON to file ({self.args.file})")
            cdx.writebom(self.args.file)
