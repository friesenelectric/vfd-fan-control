#!/usr/bin/env python

# vfd-fan-control 
#
# Copyright (c) 2018, Friesen Electric.
#
# vfd-fan-control is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.  See the LICENSE file

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.resource import NoResource
from cpppo.server.enip import client
from cpppo.server.enip.getattr import attribute_operations
import json
class fanPage(Resource):
    def render_GET(self, request):
        try:
            IP = request.args['IP'][0]
            cmd = request.args['cmd'][0]
            id = cmd
            if cmd == 'getspeed':
                TAGS = ['@15/61/1','INT']  # getspeed
            if cmd.isdigit():
                TAGS = ["@15/61/1=(INT)%s" % cmd] # setspeed
                id='setspeed'
            if cmd == 'getstate':
                TAGS = ['@15/65/1','INT'] # getstate
            if cmd == 'off':
                TAGS = ["@15/65/1=(INT)0"] # setstateoff
            if cmd == 'on':
                TAGS = ["@15/65/1=(INT)97"] # setstateon 
            vfdcon1 = client.connector(host=IP)
            resp = ''
            with vfdcon1:
                for index, descr, op, reply, status, value in vfdcon1.synchronous(operations=attribute_operations(TAGS, route_path=[], send_path='' )):
                    if value:
                        print value
                        if isinstance(value, list):
                            resp = value[1] * 256 + value[0]
                            print cmd, resp, type(resp)
                            if cmd == 'getstate' and resp == 0:
                                resp = 'OFF'
                            if cmd == 'getstate' and resp == 97:
                                resp = 'ON'
                            if cmd == 'getspeed' and isinstance(resp, int):
                                resp = resp/10.0
                        if isinstance(value, bool):
                            resp = value
        except:
            return json.dumps({'response': 'ERROR'})
        else:
            return json.dumps({'cmd': id, 'response': str(resp)})
root = Resource()
root.putChild('', fanPage())
factory = Site(root)
reactor.listenTCP(8880, factory)
print 'server started'
reactor.run()
