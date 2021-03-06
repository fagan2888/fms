#!/usr/bin/env python
"""
Synchronous random with replace engine
"""

import random
import logging

from fms.engines import Engine

logger = logging.getLogger('fms.engines.synchronousrandwreplace')

class SynchronousRandWReplace(Engine):
    """
    Synchronous engine, random sampling of agents,
    with replacement.
    After given number of periods, calls Market clearing.
    """

    def __init__(self, parameters=None, offset=0):
        """
        Constructor. Takes parameters from config.
        Seeds ramdom engine from parameter.randomseed, if any.
        """
        Engine.__init__(self, parameters, offset)
        self.params = parameters
        self.rank = offset
        if parameters:
            random.seed(parameters['randomseed'])

    def run(self, world, agents, market):
        """
        Sample agents (with replacement) and let them speak on market.   
        As market is synchronous, do_clearing is called after 
        self.days*self.daylength periods.
        """
        market.sellbook = world.state()['sellbook']
        logger.debug("Starting with sellbook %s" % market.sellbook)
        market.buybook = world.state()['buybook']
        logger.debug("Starting with buybook %s" % market.buybook)
        for day in range(self.days):
            for time in range(self.daylength):
                agt = random.randint(0, len(agents)-1)
                order = market.sanitize_order(agents[agt].speak())
                if market.is_valid(agents[agt], order):
                    if self.params.orderslogfile:
                        self.output_order(order)
                    market.record_order(order, world.tick,
                            self.unique_by_agent)
                    if self.showbooks:
                        market.output_books(world.tick)
                    world.lastmarketinfo.update(
                            {'sellbook':market.sellbook, 'buybook':market.buybook})
                world.tick +=1
                if self.params['timer']:
                    world.show_time(day, time, self.days*self.daylength)
            market.do_clearing(world.tick)
            if self.clearbooksateod:
                market.clear_books()
        logger.debug("Ending with sellbook %s" % market.sellbook)
        logger.debug("Ending with buybook %s" % market.buybook)

if __name__ == '__main__':
    print SynchronousRandWReplace()
