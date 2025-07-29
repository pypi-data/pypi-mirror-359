# Store the version here so:
# 1) we don't load dependencies by storing it in __init__.py
# 2) we can import it in setup.py for the same reason
# 3) we can import it into your module module
# 0.7.4 - Correct class declaration to include object
# 0.7.5 - Added an alias for streamid to IEAN
# 0.7.6 - Added repr function to SimpleEthernet
# 0.8.0 - Lots of updates and documentation updates
# 0.8.1 - Added IENA-N and IENA-D packets
# 0.9.0 - Added NDP
# 0.9.2 - Added Ch10
# 0.9.4 - Previous chapter 10 was the UDP wrapper. Correct Chapter10 packet now added
# 0.9.5 - Added ARINC data packet
# 0.10.0 - Added iNET
# 0.10.1 - Added info to exception
# 0.10.2 - Fixed IP checksum bug
# 0.11.0 - Chapter10 endianness changes
# 0.11.1 - IENA-N and IENA-D throw exception if there are not integer number of D and N parameters in the payload
# 0.11.2 - ParserAligned throws exception if the number of quadbytes is illegal
# 0.12.0 - Added IENA-M and IENA-Q
# 0.12.1 - Changed pcap to an iterator model
# 0.12.2 - Fixed iNET byte order
# 0.12.3 - Fixed iNET byte order
# 0.12.4 - Changed INET to separate seconds and nanoseconds
# 0.13.0 - Added UART Payload for Chapter 10
# 0.13.1 - Bug fixes on UART for Chapter 10
# 0.13.2 - Added NPD Segments for RS232
# 0.13.3 - Parser aligned printout
# 0.14.0 - Made compatiable with python3
# 0.15.0 - Added ch7 and updated all unit test to pass in both py3 py2
# 0.15.1 - Added unpack to ParserAligned
# 0.15.2 - Fixd the ascii example
# 0.15.3 - Minor updates to Ch7 and unittest
# 0.15.4 - Pcap comment removal
# 0.15.5 - Handled padding for UART data words in chapter 10
# 0.15.6 - Optimisations on Golay encoding
# 0.15.7 - Minor updates
# 0.15.8 - Traffic generator update
# 0.15.10 - Traffic generator update
# 0.15.11 - Added FCS Support to ethernet packets
# 0.15.12 - Indentation bugfix
# 0.15.13 - Renamed PDFR to PTFR
# 0.15.14 - Massive perf improvements with Golay handling
# 0.15.15 - Added summary to the recorder
# 0.15.16 - Added summary to validation script
# 0.15.17 - Added IGMPv2 simplified packet generation
# 0.15.18 - Updated validate and pkt generation script
# 0.15.19 - Fixed divide by error in validate_pcap script
# 0.15.20 - Updated tx script to be much more accurate with timing
# 0.15.21 - Added configparsed file for contol
# 0.15.22 - Added timestamp to packets in validation script
# 0.15.23 - Fixed compatibility with python2 and reduced size of test input
# 0.15.24 - Added rec time check on validate script
# 0.15.25 - Fixed unpacking of vlan. Expanded SimpleEthernet to handle VLAN more completely
# 0.15.26 - Validate script update
# 0.15.27 - Added simple IENA packet generation script
# 0.15.28 - Fixed line endings
# 0.16.0  - Refactored Chapter10 module
# 0.16.1  - Initialized attributes
# 0.16.2  - Lots of chapter10 updates.
# 0.16.3  - Added support for PCM throughput mode
# 0.16.4  - Added custom NPD segment for PCM Packetizer (0x60)
# 0.16.5  - NDP clean up.
# 0.16.6  - NDP clean up #2
# 0.16.7  - Minor clean up
# 0.16.8  - Added pcap to ch10 conversion script
# 0.16.9  - Made script executable
# 0.16.10 - Fixed wrapping of TMATs
# 0.16.11 - Added attribute to ch10 to indicate presence of secondary header
# 0.16.12 - Added timeid argument to the adau script
# 0.16.13 - Fixed sequence number rollover in adau_to_ch10 conversion. Makde optimisations to the PCM sync word length
# 0.16.14 - use pinksheet RTC time conversion. Add verification to endianness swap. Swap endianness on ARINC payloads
# 0.16.15 - fixed bug on ARINC conversion
# 0.16.16 - fixed bug in PTP -> RTC conversion
# 0.16.17 - fixed python3.11 only code in adau conversion script
# 0.16.18 - added source distribution
# 0.16.19 - Fixed timestamp bug in adau conversion script
# 0.16.20 - Changed RTC conversion to use Decimal as integer resolution was not sufficient to convert the timestamp
# 0.16.21 - adau conversion script accepts a folder input
# 0.17.0  - significant change to the MPEGTS block. Added classes for the adaption fields
# 0.17.1  - Added Video to the chapter10
# 0.17.2  - Major update to the MPEGTS section. Split out code into multiple modules. Added support for PAT packets
# 0.17.3  - Added support for PES + STANAG4609 packets
# 0.17.4  - Option to mpeg ts pack to not stuff
# 0.17.5  - Check chapter10 data length field and throw exception if not correct
# 0.17.6  - Reverted last change
# 0.17.7  - Allowed ch10 UART packet to be little endian
# 0.17.8  - Fixed ch10 secondary header checksum calculation
# 0.17.9  - Downgraded the offset error in ch7 to a warning. Added type hintint to ch7
# 0.17.10 - Added support for ARP in SimpleEthernet
# 0.17.11 - Added the SamDec class to support capturing live data from a SamDec
# 0.17.13 - Added chapter 10 recorder script.
# 0.17.14 - Fixed the PMT packet in MPEGTS
# 0.17.15 - Added support for reading SamDec pcap files
# 0.17.16 - Added documentation details
# 0.17.17 - Docstring updates
# 1.0.0   - First 1.0 release. No functional change from 0.17.17
# 1.1.0   - Moved all Chapter10 stuff into IRIG106 and then into the module according to the spec. Existing code will work but with a Deprecation warning
# 1.1.1   - Version tag not updates
# 1.1.2   - Fixed the ch10 examples
# 1.1.4   - Updates to the MPEGTS packets to build and decom a PTS / DTS packet
# 1.1.5   - Missing ut file added
# 1.1.6   - No chnage but tagging as 1.1.6
# 1.1.7   - Added logging error for incorrect IP checksum
# 1.1.8   - No change but tagging as 1.1.8
# 1.1.9   - Fixed ARINC ch10 intra packet header
# 1.2.0   - Moved Chapter 7 into the IRIG106 folder. Removed old Chapter10 directory
# 1.2.1   - Fixed logging in IP error message
# 1.2.2   - Fixed chapter 7 packet generation
# 1.2.3   - Last release was nto successful
# 1.2.4   - Removed exit in the ch7
# 1.2.5   - Added C implementation of Golay. Also improved the existing python impl
# 1.2.6   - Further optimisation of the C Golay implementation
# 1.2.7   - Changed setup so as not to break if extension cannot be compiled
# 1.2.8   (FJP 2025-07-01)
#         - Added Context Manager support to Pcap.py
#         - Allow Golay.decode() to accept bytearray or other bytes-like object instead of only bytes (if not int)
#         - simplified Golay.py; removed some redundant checks
__version__ = "1.2.8"
