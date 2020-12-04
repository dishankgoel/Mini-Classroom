#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import TCLink
from mininet.cli import CLI
import subprocess
import time

class TreeTopo( Topo ):
    "Topology for a tree network with a given depth and fanout."

    def build( self, depth=1, fanout=2 ):
        # Numbering:  h1..N, s1..M
        self.hostNum = 1
        self.switchNum = 1
        # Build topology
        self.addTree( depth, fanout )

    def addTree( self, depth, fanout ):
        """Add a subtree starting with node n.
           returns: last node added"""
        isSwitch = depth > 0
        if isSwitch:
            node = self.addSwitch( 's%s' % self.switchNum )
            self.switchNum += 1
            for _ in range( fanout ):
                child = self.addTree( depth - 1, fanout )
                self.addLink( node, child )
        else:
            node = self.addHost( 'h%s' % self.hostNum )
            self.hostNum += 1
        return node


def perform_tests():

    topo = TreeTopo(depth = 3)
    net = Mininet(topo, link = TCLink)
    net.addNAT().configDefault()
    net.start()
    # print ("Dumping host connections")
    # dumpNodeConnections(net.hosts)
    # datbase_ip = net.get('nat0').IP()
    # app_servers = ['h33', 'h34']
    # for app_server in app_servers:
    #     s = net.get(app_server)
    #     p = s.popen('./start_app.sh', s.IP(), datbase_ip, stdout = subprocess.PIPE)
    # time.sleep(2)
    # instructor = net.get('h1')
    # print("[*] Creating Instructor")
    # p = instructor.popen("python3", "instructor.py", net.get('h33').IP(), stdout = subprocess.PIPE)
    # output, error = p.communicate()
    # p.wait()
    # print(output, error)
    # students = [net.get('h2'), net.get('h3'), net.get('h4')]
    # for i in range(len(students)):
    #     print("[*] Creating student no: {}".format(i+1))
    #     student_no = i+1
    #     p = students[i].popen("python3", "student.py", net.get('h33').IP(), str(student_no))
    #     output, error = p.communicate()
    #     print(error)
    #     p.wait()
    CLI(net)
    net.stop()


if __name__ == "__main__":

    setLogLevel("info")
    perform_tests()

