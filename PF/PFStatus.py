"""Class representing the internal Packet Filter statistics and counters.

PFStatus objects contain a series of runtime statistical information describing
the current status of the Packet Filter.
"""

import time
from socket import ntohl

from PF._PFStruct import pf_status
from PF.PFConstants import *
from PF.PFUtils import PFObject


__all__ = ['PFStatus']


# PFStatus class ###############################################################
class PFStatus(PFObject):
    """Class representing the internal Packet Filter statistics and counters."""

    _struct_type = pf_status

    def __init__(self, status):
        """Check argument and initialize class attributes."""
        super(PFStatus, self).__init__(status)

    def _from_struct(self, s):
        """Initialize class attributes from a pf_status structure."""
        self.ifname    = s.ifname
        self.running   = bool(s.running)
        self.since     = s.since
        self.states    = s.states
        self.src_nodes = s.src_nodes
        self.debug     = s.debug
        self.hostid    = ntohl(s.hostid) & 0xffffffff
        self.reass     = s.reass
        self.pf_chksum = "0x" + "".join(["%02x" % b for b in s.pf_chksum])

        self.cnt       = {'match':                    s.counters[0],
                          'bad-offset':               s.counters[1],
                          'fragment':                 s.counters[2],
                          'short':                    s.counters[3],
                          'normalize':                s.counters[4],
                          'memory':                   s.counters[5],
                          'bad-timestamp':            s.counters[6],
                          'congestion':               s.counters[7],
                          'ip-option':                s.counters[8],
                          'proto-cksum':              s.counters[9],
                          'state-mismatch':           s.counters[10],
                          'state-insert':             s.counters[11],
                          'state-limit':              s.counters[12],
                          'src-limit':                s.counters[13],
                          'synproxy':                 s.counters[14]}

        self.lcnt      = {'max states per rule':      s.lcounters[0],
                          'max-src-states':           s.lcounters[1],
                          'max-src-nodes':            s.lcounters[2],
                          'max-src-conn':             s.lcounters[3],
                          'max-src-conn-rate':        s.lcounters[4],
                          'overload table insertion': s.lcounters[5],
                          'overload flush states':    s.lcounters[6]}

        self.fcnt      = {'searches':                 s.fcounters[0],
                          'inserts':                  s.fcounters[1],
                          'removals':                 s.fcounters[2]}

        self.scnt      = {'searches':                 s.scounters[0],
                          'inserts':                  s.scounters[1],
                          'removals':                 s.scounters[2]}

        self.bytes     = {'in':   (s.bcounters[0][0], s.bcounters[1][0]),
                          'out':  (s.bcounters[0][1], s.bcounters[1][1])}

        self.packets   = {'in':  ((s.pcounters[0][0][PF_PASS],
                                   s.pcounters[1][0][PF_PASS]),
                                  (s.pcounters[0][0][PF_DROP],
                                   s.pcounters[1][0][PF_DROP])),
                          'out': ((s.pcounters[0][1][PF_PASS],
                                   s.pcounters[1][1][PF_PASS]),
                                  (s.pcounters[0][1][PF_DROP],
                                   s.pcounters[1][1][PF_DROP]))}

    def _to_string(self):
        """Return a string containing the statistics."""
        s = "Status: " + ('Enabled' if self.running else 'Disabled')

        if self.since:
            runtime = time.time() - self.since
            day, sec = divmod(runtime, 60)
            day, min = divmod(day, 60)
            day, hrs = divmod(day, 24)
            s += " for %i days %02i:%02i:%02i" % (day, hrs, min, sec)

        dbg = ('none', 'urgent', 'misc', 'loud')[self.debug]
        s = "%-44s%15s\n\n" % (s, "Debug: " + dbg)
        s += "Hostid:   0x%08x\n" % self.hostid
        s += "Checksum: %s\n\n" % self.pf_chksum

        if self.ifname:
            fmt = "  %-25s %14u %16u\n"
            s += "Interface Stats for %-16s %5s %16s\n" % (self.ifname,
                                                           "IPv4", "IPv6")
            s += fmt % (("Bytes In",)  + self.bytes["in"])
            s += fmt % (("Bytes Out",) + self.bytes["out"])
            s += "  Packets In\n"
            s += fmt % (("  Passed",)  + self.packets["in"][PF_PASS])
            s += fmt % (("  Blocked",) + self.packets["in"][PF_DROP])
            s += "  Packets Out\n"
            s += fmt % (("  Passed",)  + self.packets["out"][PF_PASS])
            s += fmt % (("  Blocked",) + self.packets["out"][PF_DROP])
            s += "\n"

        s += "%-27s %14s %16s\n" % ("State Table", "Total", "Rate")
        s += "  %-25s %14u" % ("current entries", self.states)
        for k, v in self.fcnt.iteritems():
            s += "\n  %-25s %14u " % (k, v)
            if self.since:
                s += "%14.1f/s" % (v/runtime)

        s += "\nSource Tracking Table"
        s += "\n  %-25s %14u" % ("current entries", self.src_nodes)
        for k, v in self.scnt.iteritems():
            s += "\n  %-25s %14u " % (k, v)
            if self.since:
                s += "%14.1f/s" % (v/runtime)

        s += "\nCounters"
        for k, v in self.cnt.iteritems():
            s += "\n  %-25s %14u " % (k, v)
            if self.since:
                s += "%14.1f/s" % (v/runtime)

        s += "\nLimit Counters"
        for k, v in self.lcnt.iteritems():
            s += "\n  %-25s %14u " % (k, v)
            if self.since:
                s += "%14.1f/s" % (v/runtime)

        return s

