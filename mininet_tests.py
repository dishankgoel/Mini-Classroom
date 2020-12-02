#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import TCLink
from mininet.cli import CLI
import api
import subprocess
import time

class TreeTopo( Topo ):
    "Topology for a tree network with a given depth and fanout."

    def build( self, depth=1, fanout=2 ):
        # Numbering:  h1..N, s1..M
        self.hostNum = 1
        self.switchNum = 1
        self.custom_switches = []
        # Build topology
        self.addTree( depth, fanout )
        hosts_added = 2**depth
        for i in range(1, 5):
            added_host = self.addHost('h{}'.format(hosts_added + i))
            self.addLink(added_host, self.custom_switches[i])
        database = self.addHost('h37')
        self.addLink(database, self.custom_switches[0])

    def addTree( self, depth, fanout ):
        """Add a subtree starting with node n.
           returns: last node added"""
        isSwitch = depth > 0
        if isSwitch:
            node = self.addSwitch( 's%s' % self.switchNum )
            if(self.switchNum in [1, 3,10,18,25]):
                self.custom_switches.append(node)
            self.switchNum += 1
            for _ in range( fanout ):
                child = self.addTree( depth - 1, fanout )
                self.addLink( node, child )
        else:
            node = self.addHost( 'h%s' % self.hostNum )
            self.hostNum += 1
        return node

def for_each_client():
    pass

def perform_tests():

    topo = TreeTopo(depth = 5)
    net = Mininet(topo, link = TCLink)
    net.start()
    # print ("Dumping host connections")
    # dumpNodeConnections(net.hosts)
    # Create the database
    # database = net.get('h37')
    app_servers = ['h33', 'h34', 'h35', 'h36']
    for app_server in app_servers:
        s = net.get(app_server)
        s.popen('./start_app.sh', stdout = subprocess.PIPE)

    CLI(net)
    net.stop()


if __name__ == "__main__":

    setLogLevel("info")
    perform_tests()

