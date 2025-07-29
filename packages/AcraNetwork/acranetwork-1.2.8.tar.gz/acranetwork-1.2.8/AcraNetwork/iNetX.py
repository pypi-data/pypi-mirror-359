"""
.. module:: iNetX
    :platform: Unix, Windows
    :synopsis: Class to construct and de construct iNetx Packets

.. moduleauthor:: Diarmuid Collins <dcollins@curtisswright.com>

"""

__author__ = "Diarmuid Collins"
__copyright__ = "Copyright 2018"
__maintainer__ = "Diarmuid Collins"
__email__ = "dcollins@curtisswright.com"
__status__ = "Production"


import struct


class iNetX(object):
    """
    Class to pack and unpack iNetX payloads. iNet-X is an open payload format for use
    in FTI networks. It is usually transmitted in a UDP packet containing parameter data
    acquired from sensors and buses

    Capture a UDP packet and unpack the payload as an iNetX packet

    Here's an example where you take some bytes, decode it as an iNetX packet, then build the same
    packet from scratch and compare the two


    >>> from base64 import b64decode
    >>> data = b64decode('EQAAAAAAANwAAAABAAAAHgAAAAEAAAABAAAAAAUA')
    >>> pkt = iNetX()
    >>> pkt.unpack(data)
    True
    >>> print(f"{pkt.streamid:#0X}")
    0XDC
    >>> i = iNetX()
    >>> i.sequence = 1
    >>> i.pif = 0
    >>> i.streamid = 0xDC
    >>> i.setPacketTime(1, 1)
    True
    >>> i.payload = struct.pack("H", 0x5)
    >>> i == pkt
    True

    """

    DEF_CONTROL_WORD = 0x11000000  #: (Object Constant) The default iNetX control word.
    INETX_HEADER_FORMAT = ">LLLLLLL"
    INETX_HEADER_LENGTH = struct.calcsize(INETX_HEADER_FORMAT)
    REQ_ATTR = ("inetxcontrol", "streamid", "sequence", "ptptimeseconds", "ptptimenanoseconds", "pif", "payload")

    def __init__(self, buf: bytes = None):
        """Creator method for an iNetX class

        Args:
            buf (bytes, optional): Optionally unpack the byte buffer into an iNetX object. Defaults to None.
        """
        self.inetxcontrol: int = iNetX.DEF_CONTROL_WORD  #: Control Word Defaults to 0x11000000
        self.streamid: int = 0  #: Stream ID. Typically to identify a unique packet in an FTI network. 4 bytes in size
        self.sequence: int = 0  #: Unique rollover counter per stream ID.Rolls over at 2^64
        self.packetlen: int = 0  #: Packet Length in bytes
        self.ptptimeseconds: int = 0  #: Timestamp of first parameter in the packet. EPOCH time
        self.ptptimenanoseconds: int = 0  #: Nanaosecond timestamp
        self.pif: int = 0  #: Payload Information Field
        self.payload: bytes = bytes()  #: Payload

        self._packetStrut = struct.Struct(iNetX.INETX_HEADER_FORMAT)
        if buf is not None:
            self.unpack(buf)

    def pack(self) -> bytes:
        """
        Pack the packet into a binary format and return as a string

        :rtype: bytes
        """

        for attr in iNetX.REQ_ATTR:
            if getattr(self, attr) is None:
                raise ValueError("Require {} is not defined".format(attr))

        self.packetlen = len(self.payload) + iNetX.INETX_HEADER_LENGTH
        packetvalues = (
            self.inetxcontrol,
            self.streamid,
            self.sequence,
            self.packetlen,
            self.ptptimeseconds,
            self.ptptimenanoseconds,
            self.pif,
        )
        packet = self._packetStrut.pack(*packetvalues) + self.payload
        return packet

    def unpack(self, buf: bytes) -> bool:
        """
        Unpack a raw byte stream to an iNetX object
        Accepts a buffer to unpack as the required argument

        :param buf: The string buffer to unpack
        :type buf: bytes
        :rtype: bool
        """

        if len(buf) < iNetX.INETX_HEADER_LENGTH:
            raise ValueError("Buffer is too short to be an iNetX packet")

        (
            self.inetxcontrol,
            self.streamid,
            self.sequence,
            self.packetlen,
            self.ptptimeseconds,
            self.ptptimenanoseconds,
            self.pif,
        ) = self._packetStrut.unpack_from(buf)

        if self.packetlen != len(buf):
            raise ValueError(
                "Length of buffer 0x{:X} does not match length field 0x{:X}".format(len(buf), self.packetlen)
            )

        self.payload = buf[iNetX.INETX_HEADER_LENGTH :]

        return True

    def setPacketTime(self, utctimestamp, nanoseconds=0):
        """
        Set the packet timestamp

        :param timestamp: The timestamp in seconds since 1 Jan 1970
        :type timestamp: int
        :type nanoseconds: Nanoseconds past the current time
        :type nanoseconds: int
        """

        self.ptptimeseconds = utctimestamp
        self.ptptimenanoseconds = nanoseconds

        return True

    def __repr__(self):
        return "STREAMID={:#0X} SEQ={} LEN={} PTPS={} PTPNS={}".format(
            self.streamid, self.sequence, self.packetlen, self.ptptimeseconds, self.ptptimenanoseconds
        )

    def __eq__(self, other):
        if not isinstance(other, iNetX):
            return False

        for attr in iNetX.REQ_ATTR:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def __len__(self):
        return len(self.pack())
