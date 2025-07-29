"""
.. module:: NPD
    :platform: Unix, Windows
    :synopsis: Class to construct and de construct NPD Packets

.. moduleauthor:: Diarmuid Collins <dcollins@curtisswright.com>

"""

__author__ = "Diarmuid Collins"
__copyright__ = "Copyright 2018"
__maintainer__ = "Diarmuid Collins"
__email__ = "dcollins@curtisswright.com"
__status__ = "Production"


import struct
from socket import inet_aton, inet_ntoa
import typing


class NPDSegment(object):
    """
    NPD Payloads are split into segments. This class will pack and unpack segments

    """

    NPD_SEGMENT_HDR_FORMAT = ">IHBB"
    NPD_SEGMENT_HDR_LEN = struct.calcsize(NPD_SEGMENT_HDR_FORMAT)

    def __init__(self):
        self.timedelta: int = 0  #: The R-bit in the Flags field of the packet header dictates the format of this field.
        self.segmentlen: int = (
            NPDSegment.NPD_SEGMENT_HDR_LEN
        )  #: The length of the segment header and data in bytes excluding padding.
        self.errorcode: int = 0  #: This field has a zero value if there are no errors
        self.flags: int = 0  #: [2:1] Fragmentation state flag
        self._payload: bytes = bytes()  #: Payload of segment

    @property
    def payload(self) -> bytes:
        """
        Payload of segment
        :return:
        """
        return self._payload

    @payload.setter
    def payload(self, buf: bytes) -> None:
        self._payload = buf
        self.segmentlen = len(self.payload) + NPDSegment.NPD_SEGMENT_HDR_LEN

    def unpack(self, buffer: bytes) -> bytes:
        """
        Unpack a string buffer into an NPD segment. Return the remaining buffer so that the next segment can iteratively
        be unpacked
        """
        (self.timedelta, self.segmentlen, self.errorcode, self.flags) = struct.unpack_from(
            NPDSegment.NPD_SEGMENT_HDR_FORMAT, buffer
        )
        self.payload = buffer[NPDSegment.NPD_SEGMENT_HDR_LEN : self.segmentlen]
        if self.segmentlen % 4 == 0:
            pad_len = 0
        else:
            pad_len = 4 - (self.segmentlen % 4)

        return buffer[(self.segmentlen + pad_len) :]

    def pack(self) -> bytes:
        """
        Pack the NPD object into a binary buffer

        :rtype: str
        """
        if len(self.payload) % 4 == 0:
            pad = b""
        else:
            pad_len = 4 - len(self.payload) % 4
            pad = struct.pack(">B", 0xFF) * pad_len

        hdr_pack = struct.pack(
            NPDSegment.NPD_SEGMENT_HDR_FORMAT, self.timedelta, self.segmentlen, self.errorcode, self.flags
        )

        return hdr_pack + self.payload + pad

    def __eq__(self, other):
        if not isinstance(other, NPDSegment):
            return False
        for attr in ["timedelta", "segmentlen", "errorcode", "flags", "payload"]:
            if getattr(other, attr) != getattr(self, attr):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "NPD Segment. TimeDelta={} Segment Len={} ErrorCode={} Flags={:#0X}".format(
            self.timedelta, self.segmentlen, self.errorcode, self.flags
        )


class ACQSegment(NPDSegment):
    """
    ACQ MPCM segments. Defined as 0xA1 in the NPD specification
    """

    def __init__(self):
        NPDSegment.__init__(self)
        self.sfid: int = 0
        self.cal: int = 0
        self.words: typing.List[int] = []

    def unpack(self, buffer):
        remaining = NPDSegment.unpack(self, buffer)
        (self.sfid, _cal, reserved) = struct.unpack_from(">BBH", self.payload)
        self.cal = _cal >> 7
        len_words = int((len(self.payload) - 4) / 2)
        self.words = list(struct.unpack_from(">{}H".format(len_words), self.payload, 4))
        return remaining

    def __repr__(self):
        return (
            "PCM NPD Segment. TimeDelta={} Segment Len={} ErrorCode={:#0X} Flags={:#0X} sfid={:#0X} "
            "WordCnt={}"
            "".format(self.timedelta, self.segmentlen, self.errorcode, self.flags, self.sfid, len(self.words))
        )


class PCMPacketizer(NPDSegment):
    """
    PCM Packetizer Segments for the ADAU PCM module
    """

    def __repr__(self):
        return "PCM Packetizer NPD Segment. TimeDelta={} Segment Len={} ErrorCode={:#0X} Flags={:#0X}" "".format(
            self.timedelta, self.segmentlen, self.errorcode, self.flags
        )


class A429Segment(NPDSegment):
    pass


class RS232Segment(NPDSegment):
    """The RS-232 segment header encapsulates data captured by the MBIM-232N-1 acquisition module."""

    BSL_CH0 = 0x0
    BSL_CH1 = 0x8000
    BSL_PAR_ERR = 0x4000
    BSL_TWO_STOP_BITS = 0x2000
    BSL_EVEN_PAR = 0x1000
    BSL_PARN_EN = 0x800
    BSL_8BIT = 0x0
    BSL_7BIT = 0x200
    BSL_6BIT = 0x400
    BSL_5BIT = 0x600
    BSL_PKT_SYNC_FIXED = 0x0
    BSL_PKT_SYNC_VAR = 0x80
    BSL_PKT_GAP = 0x100
    BSL_PKT_THROUGHPUT = 0x180
    BSL_422 = 0x40
    BSL_PAD_EN = 0x20
    BSL_ENDIAN_BIG = 0x0
    BSL_ENDIAN_LITTLE = 0x10
    BSL_REL_PKT_CNT = 0x8

    BSL_SYNC_COUNT_MASK = 0x7

    def __init__(self):
        NPDSegment.__init__(self)
        self.block_status: int = 0
        self.sync_bytes: typing.List[int] = []
        self.data: bytes = bytes()

    def unpack(self, buffer: bytes):
        """
        Unpack a string buffer into an RS232 segment. Return the remaining buffer so that the next segment can iteratively
        be unpacked

        :param buffer: A string buffer representing an RS232 segment
        :type buffer: str

        :rtype: str
        """
        remaining = NPDSegment.unpack(self, buffer)
        (self.block_status,) = struct.unpack_from(">H", self.payload)
        sync_word_cnt = self.block_status & RS232Segment.BSL_SYNC_COUNT_MASK
        if sync_word_cnt > 0:
            self.sync_bytes = list(struct.unpack_from(">{}B".format(sync_word_cnt), self.payload[2:]))
            self.data = self.payload[2 + sync_word_cnt :]
        else:
            self.data = self.payload[2:]
        return remaining

    def pack(self) -> bytes:
        """
        Pack the RS232 Segment object into a binary buffer

        """
        if self.block_status is None:
            raise Exception("block_status attribute should be defined")
        # Build the status word by calculating the sync bytes and adding to the rest of the header
        self.block_status = (self.block_status & 0xFFF8) + len(self.sync_bytes)
        self.payload = struct.pack(">H", self.block_status)
        # Add the sync words
        for sync_byte in self.sync_bytes:
            self.payload += struct.pack(">B", sync_byte)
        self.payload += self.data
        return NPDSegment.pack(self)

    def __eq__(self, other):
        if not isinstance(other, RS232Segment):
            return False
        for attr in ["timedelta", "segmentlen", "errorcode", "flags", "block_status", "sync_bytes", "data"]:
            if getattr(other, attr) != getattr(self, attr):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return (
            "RS232 NPD Segment. TimeDelta={} Segment Len={} ErrorCode={:#0X} Flags={:#0X} Block_Status={:#0X} "
            "DataLen={}"
            "".format(self.timedelta, self.segmentlen, self.errorcode, self.flags, self.block_status, len(self.data))
        )


class MIL1553Segment(NPDSegment):
    """The MIL-STD-1553 segment encapsulates MIL-STD-1553 messages"""

    def __init__(self):
        NPDSegment.__init__(self)
        self.blockstatus: int = 0
        self.gap1: int = 0
        self.gap2: int = 0
        self.data: bytes = bytes()

    def unpack(self, buffer: bytes) -> bytes:
        """Unpack the buffer into the MIL1553Segment object. Return the remaining bytes after unpacking"""
        remaining = NPDSegment.unpack(self, buffer)
        (self.blockstatus, self.gap2, self.gap2) = struct.unpack_from(">HBB", self.payload)
        self.data = self.payload[4:]
        return remaining

    def __repr__(self):
        return (
            "MIL-STD-1553 Segment. TimeDelta={} Segment Len={} ErrorCode={:#0X} Flags={:#0X} BlockStatus={:#0X} "
            "Gap1={} Gap2={}"
            "".format(
                self.timedelta, self.segmentlen, self.errorcode, self.flags, self.blockstatus, self.gap1, self.gap2
            )
        )


class NPD(object):
    """
    Class to pack and unpack NPD payloads. The segments will be unpacked for specific defined segements

    For unknown data types, the class :class:`NPDSegment` will be used

    >>> from base64 import b64decode
    >>> import AcraNetwork.iNetX as inetx
    >>> data = b64decode('NVAADAMEAAoAAAAB6wAAAQAAAAUAAAADAA0AAQhAAAAA////AAAAAwAMAAEIQQEA')
    >>> n = NPD()
    >>> n.unpack(data)
    True
    >>> print(f"{n.datatype:#0X}")
    0X50
    >>> for segment in n.segments:
    ...    print(f"{segment}")
    RS232 NPD Segment. TimeDelta=3 Segment Len=13 ErrorCode=0X0 Flags=0X1 Block_Status=0X840 DataLen=3
    RS232 NPD Segment. TimeDelta=3 Segment Len=12 ErrorCode=0X0 Flags=0X1 Block_Status=0X841 DataLen=1
    """

    NPD_HEADER_FORMAT = ">BBHBBHIII"
    NPD_HEADER_LENGTH = struct.calcsize(NPD_HEADER_FORMAT)
    NPD_VERSION = 3

    NPD_DT = {0x50: RS232Segment, 0x38: A429Segment, 0xA1: ACQSegment, 0xD0: MIL1553Segment, 0x60: PCMPacketizer}

    def __init__(self):
        """Creator method for a UDP class"""
        self.version: int = NPD.NPD_VERSION  #: Version
        self.hdrlen: int = NPD.NPD_HEADER_LENGTH // 4  #: Header Length
        self.datatype: typing.Optional[int] = None  #: A unique identifier for the type of data collected in the packet
        self.packetlen: int = (
            0  #: The number of 32-bit words in the data packet including the NPD header and data segments.
        )
        self.cfgcnt: int = (
            0  #: Stores an 8-bit number that is incremented (mod 256) each time the network device is configured.
        )
        self.flags: int = 0  #: Flags [0]-Unlocked timestamp [1]-Packet fragmentation [2]-Relative Time Count Present
        self.sequence: int = 0  #: Sequence number
        self.datasrcid: int = 0  #: A unique data source identifier for each data source.
        self.mcastaddr: str = ""  #: The 32-bit IP multicast address used as the destination address of the packet.
        self.timestamp = None  #: The content of this field is based upon the R bit in the flags field of the NPD Packet Protocol header.
        self.segments: typing.List[NPDSegment | ACQSegment | PCMPacketizer | RS232Segment | MIL1553Segment] = (
            []
        )  #: List of all the data segments

    def unpack(self, buffer: bytes) -> bool:
        """
        Unpack a string buffer into an NPD object

        :param buffer: A string buffer representing an NPD packet
        :type buffer: bytes
        :rtype: None
        """
        (
            _ver_hdr,
            self.datatype,
            self.packetlen,
            self.cfgcnt,
            self.flags,
            self.sequence,
            self.datasrcid,
            _mcast,
            self.timestamp,
        ) = struct.unpack_from(NPD.NPD_HEADER_FORMAT, buffer)
        self.version = _ver_hdr >> 4
        self.hdrlen = _ver_hdr & 0xF
        self.mcastaddr = inet_ntoa(struct.pack(">I", _mcast))

        _payload = buffer[self.hdrlen * 4 :]

        if self.packetlen * 4 != len(buffer):
            raise Exception("The self reported packet length does not match the length of the buffer supplied")

        remain_buf = _payload
        while remain_buf != b"":
            if self.datatype in NPD.NPD_DT:
                segment = NPD.NPD_DT[self.datatype]()
            else:
                segment = NPDSegment()
            try:
                remain_buf = segment.unpack(remain_buf)
            except Exception as e:
                raise Exception(e)
            else:
                self.segments.append(segment)

        return True

    def pack(self) -> bytes:
        """
        Pack the NPD object into a binary buffer
        """
        _ver_hdr = (self.version << 4) + self.hdrlen
        (_mc,) = struct.unpack(">I", inet_aton(self.mcastaddr))

        _payload = b""
        for segment in self.segments:
            _payload += segment.pack()
        self.packetlen = (NPD.NPD_HEADER_LENGTH + len(_payload)) // 4
        hdr_buf = struct.pack(
            NPD.NPD_HEADER_FORMAT,
            _ver_hdr,
            self.datatype,
            self.packetlen,
            self.cfgcnt,
            self.flags,
            self.sequence,
            self.datasrcid,
            _mc,
            self.timestamp,
        )

        return hdr_buf + _payload

    def __repr__(self) -> str:
        det = "NPD: DataType={:#0X} Seq={} DataSrcID={:#0X} MCastAddr={}".format(
            self.datatype, self.sequence, self.datasrcid, self.mcastaddr
        )
        for seg in self.segments:
            det += "\n\t{}".format(repr(seg))

        return det

    def __eq__(self, other):
        if not isinstance(other, NPD):
            return False
        for attr in [
            "version",
            "hdrlen",
            "datatype",
            "packetlen",
            "cfgcnt",
            "flags",
            "sequence",
            "datasrcid",
            "mcastaddr",
            "timestamp",
            "segments",
        ]:
            if getattr(other, attr) != getattr(self, attr):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        self._index = 0
        return self

    def next(self) -> NPDSegment:
        if self._index < len(self.segments):
            _dw = self.segments[self._index]
            self._index += 1
            return _dw
        else:
            raise StopIteration

    __next__ = next

    def __len__(self) -> int:
        return len(self.segments)

    def __getitem__(self, key: int) -> NPDSegment:
        return self.segments[key]
