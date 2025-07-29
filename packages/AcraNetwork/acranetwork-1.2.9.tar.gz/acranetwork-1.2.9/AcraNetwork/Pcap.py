"""
.. module:: pcap
    :platform: Unix, Windows
    :synopsis: Class to pack and unpack pcap files

.. moduleauthor:: Diarmuid Collins <dcollins@curtisswright.com>

"""

__author__ = "Diarmuid Collins"
__copyright__ = "Copyright 2018"
__maintainer__ = "Diarmuid Collins"
__email__ = "dcollins@curtisswright.com"
__status__ = "Production"


import struct
import os
import time
import warnings


class PcapRecord(object):
    """
    Class that can be used to store one pcap record. A Pcap file contains one or more PcapRecords

    :type sec: int
    :type usec: int
    :type incl_len: int
    :type orig_len: int
    :type _packet: str
    """

    def __init__(self, now=False):
        """
        :param now: if True, record time is set to the current time.
        :type  now: bool
        """
        self.sec: int = 0  #: Second timestamp of the record. Epoch time
        self.usec: int = 0  #: Microsecond timestamp of the record
        self.incl_len: int = 0  #: The number of bytes captured and saved in the file
        self.orig_len: int = 0  #: The number of bytes as appeared on the network when captured
        self._payload: bytes = bytes()
        if now:
            self.set_current_time()

    # Use a property on packet so that the length is triggered on it changing
    @property
    def packet(self):
        """
        The payload within the pcap record. Payload is more accurate

        :rtype: bytes
        """
        return self._payload

    @packet.setter
    def packet(self, p: bytes) -> None:
        self._payload = p
        self.incl_len = len(p)
        self.orig_len = self.incl_len

    @property
    def payload(self):
        """
        The payload within the pcap record.

        :rtype: bytes
        """
        return self._payload

    @payload.setter
    def payload(self, p: bytes) -> None:
        self._payload = p
        self.incl_len = len(p)
        self.orig_len = self.incl_len

    def unpack(self, buf: bytes) -> None:
        """
        Unpack the pcap header. Pass in a buffer containing the header

        :type buf: bytes
        """

        if struct.calcsize(Pcap.RECORD_HEADER_FORMAT) != len(buf):
            raise ValueError("Header buffer is not the correct size to be a Pcap record header")
        (self.sec, self.usec, self.incl_len, self.orig_len) = struct.unpack(Pcap.RECORD_HEADER_FORMAT, buf)

    def pack(self) -> bytes:
        """
        Pack a PcapRecord into a buffer

        :rtype: bytes

        """
        if (
            self.sec is None
            or self.usec is None
            or self.incl_len is None
            or self.orig_len is None
            or self.packet is None
        ):
            raise ValueError("Cannot build record with undefined fields in the payload")

        return struct.pack(Pcap.RECORD_HEADER_FORMAT, self.sec, self.usec, self.incl_len, self.orig_len) + self.packet

    def setCurrentTime(self) -> bool:
        return self.set_current_time()

    def set_current_time(self):
        """
        Convienece method to set the time of the PCAP record

        :rtype: bool
        """
        currenttime = time.time()
        self.usec = int((currenttime % 1) * 1e6)
        self.sec = int(currenttime)
        return True

    def __repr__(self):
        return "LEN:{} SEC:{} USEC:{}".format(self.orig_len, self.sec, self.usec)

    def __len__(self):
        return len(self._payload)


class Pcap(object):
    """
    Create a new Pcap object with the specified filename.
    Set the mode to define read, write or append

    :param filename: The PCAP filename
    :type filename: str


    :Keyword Arguments:
        * *mode* -- r: read w: write a: append


    Pcap files look like::

        -------------- --------------- ---------------- --------------- ---------------- -------
        Global Header | Record Header | Record payload | Record Header | Record payload | .....
        -------------- --------------- ---------------- --------------- ---------------- -------

    So after opening the file, iterate through the object to read the records

    A PCAP file can be opened for reading or writing by specifying mode "r"
    or "w", or for append by specifying "a".
    
    When a PCAP file is open for writing or appending, PcapRecord objects can 
    be written to it.
    
    # Write 10 UDP records to a file
    # For simplicity use the same MAC, IP and UDP headers in all records
    >>> headers = (bytes((0x77,0x88,0x99,0xAA,0xBB,0xCC,0x66,0x55,0x44,0x33,0x22,0x11,
    ...                   0x08,0x00))
    ...           +bytes((0x45,0x00,0x00,0x36,0x77,0x77,0x40,0x00,0xff,0x11,0x8a,0xa4,
    ...                   0x12,0x34,0x56,0x78,0x99,0x88,0x77,0x66))
    ...           +bytes((0x12,0x34,0x56,0x78,0x00,0x22,0x00,0x00))
    ...           )
    >>> with Pcap("_dummy.pcap", mode='w') as p:
    ...     r = PcapRecord()
    ...     for i in range(10):
    ...         start_ch = ord('A') + i
    ...         r.payload = headers + bytes((x for x in range(start_ch,start_ch+26)))
    ...         p.write(r)
    
    When a PCAP file is open for reading, iterate through the records.
    >>> with Pcap("_dummy.pcap", mode='r') as p2:
    ...     print(f"{p2.filename} contains {p2.filesize} bytes and is open with mode '{p2.mode}'")
    ...     print(f"Network type ID {p2.network}{' (Ethernet)' if p2.network==1 else ''}")
    ...     for ix, record in enumerate(p2):
    ...         print(f"{ix} {record.orig_len} bytes: {record.payload}")
    ...
    _dummy.pcap contains 864 bytes and is open with mode 'r'
    Network type ID 1 (Ethernet)
    0 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    1 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00BCDEFGHIJKLMNOPQRSTUVWXYZ['
    2 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00CDEFGHIJKLMNOPQRSTUVWXYZ[\\'
    3 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00DEFGHIJKLMNOPQRSTUVWXYZ[\\]'
    4 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00EFGHIJKLMNOPQRSTUVWXYZ[\\]^'
    5 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00FGHIJKLMNOPQRSTUVWXYZ[\\]^_'
    6 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00GHIJKLMNOPQRSTUVWXYZ[\\]^_`'
    7 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00HIJKLMNOPQRSTUVWXYZ[\\]^_`a'
    8 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00IJKLMNOPQRSTUVWXYZ[\\]^_`ab'
    9 68 bytes: b'w\x88\x99\xaa\xbb\xccfUD3"\x11\x08\x00E\x00\x006ww@\x00\xff\x11\x8a\xa4\x124Vx\x99\x88wf\x124Vx\x00"\x00\x00JKLMNOPQRSTUVWXYZ[\\]^_`abc'


    The pcap can also be treated a list to select the relevant object.


    >>> # Create a pcap file
    >>> p = Pcap("_dummy.pcap", mode='w')
    >>> r = PcapRecord()
    >>> r.payload = bytes(1)
    >>> p.write(r)
    >>> p.close()
    >>> # Now open and read it
    >>> p2 = Pcap(os.path.join("_dummy.pcap"))
    >>> print(p2.network)
    1
    >>> import struct
    >>> for mypcaprecord in p2:
    ...    (firstbyte,) = struct.unpack(">B", mypcaprecord.payload)
    ...    print(firstbyte)
    0



    """

    GLOBAL_HEADER_FORMAT = "<IhhiIII"
    RECORD_HEADER_FORMAT = "<IIII"
    RECORD_HEADER_SIZE = struct.calcsize(RECORD_HEADER_FORMAT)
    GLOBAL_HEADER_SIZE = struct.calcsize(GLOBAL_HEADER_FORMAT)

    def __init__(self, filename: str, **kwargs):
        self.filename: str = filename  #: The filename of the PCAP file
        self.mode: str = kwargs.get("mode", "r")  #: The file reading mode
        self._bufferring: int = kwargs.get("buffering ", -1)  #: The file reading mode
        # Global header fields
        self.magic: int = 0xA1B2C3D4  #: The magic_number which defines the file format. Leave as is.
        self.versionmaj: int = 2  #: File format major version. Currently 2
        self.versionmin: int = 4  #: File format minor version. Currently 4
        self.zone: int = 0  #: The timezone correction in seconds. 0 = GMT
        self.sigfigs: int = 0  #: Set to 0
        self.snaplen: int = 65535  #: snapshot length. Typically unchanged
        self.network: int = 1  #: Link-layer header type. http://www.tcpdump.org/linktypes.html
        self.filesize = 0

        # rec_no is convenient if the file is not being read in a simple loop,
        # so "for ix, record in enumerate(p)" cannot easily be used. It is the 
        # number of the last record read or written. Wireshark numbers records 
        # starting at 1, so after the first record is read or written, rec_no 
        # will be 1
        self.rec_no = 0

        self.fopen = None # make deterministic if the file open fails
        try:
            self.fopen = open(filename, f"{self.mode}b", self._bufferring)
        except Exception as e:
            raise IOError(f"Failed to open {self.filename}. err={e}")

        # mode can be anything that open() will accept with 'b' added. So it
        # could be "a". But for "r" or "w", then the header must be handled.
        if self.mode == "r":
            self._read_global_header()
        elif self.mode == "w":
            self._write_global_header()

        try:
            self.filesize = os.path.getsize(filename)
        except Exception as e:
            self.filesize = 0

    # Define __enter__() and __exit__() so "with Pcap(...) as x" can be used
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def flush(self):
        return self.fopen.flush()

    def _read_global_header(self) -> bool:
        """
        This method will read the pcap global header and unpack it and propogate the relevant attributes
        This should be the first method to call on reading a pcap] file

        :rtype: bool
        """

        header = self.fopen.read(Pcap.GLOBAL_HEADER_SIZE)
        (
            self.magic,
            self.versionmaj,
            self.versionmin,
            self.zone,
            self.sigfigs,
            self.snaplen,
            self.network,
        ) = struct.unpack(Pcap.GLOBAL_HEADER_FORMAT, header)

        return True

    def _write_global_header(self):
        """
        Write the global header to a new pcap file

        :rtype: None
        """
        header = struct.pack(
            Pcap.GLOBAL_HEADER_FORMAT,
            self.magic,
            self.versionmaj,
            self.versionmin,
            self.zone,
            self.sigfigs,
            self.snaplen,
            self.network,
        )
        self.fopen.write(header)
        self.filesize += len(header)
        return True

    def write(self, pcaprecord: PcapRecord):
        """
        Write the supplied pcaprecord to the pcap file

        :param pcaprecord: The Pcap Record to write
        :type pcaprecord: PcapRecord
        """

        _pkt = pcaprecord.pack()
        self.fopen.write(_pkt)
        self.rec_no += 1
        self.filesize += len(_pkt)

    def close(self):
        """
        Close the current pcap file

        :rtype: None
        """
        self.fopen.close()

    def __iter__(self):
        return self

    def next(self):
        # read the pcap header to a new object
        pcaprecord = PcapRecord()
        try:
            pcaprecord.unpack(self.fopen.read(Pcap.RECORD_HEADER_SIZE))
        except:
            raise StopIteration

        try:
            pcaprecord.packet = self.fopen.read(pcaprecord.incl_len)
        except:
            raise StopIteration
        else:
            self.rec_no += 1
            return pcaprecord

    __next__ = next

    def __getitem__(self, item):
        self.fopen.seek(Pcap.GLOBAL_HEADER_SIZE)
        for idx, rec in enumerate(self):
            if idx == item:
                return rec
