# Autor: Fábio D. Pacheco
# Date: 21/11

import numpy as np
from gnuradio import gr

S_IDLE    = 0
S_PACKET  = 1

class basic_block(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__( self, power_thres=0.01, window_size=80 ):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Power Threshold Filter',   # will show up in GRC
            in_sig=[np.complex64, np.float32],   
            out_sig=[np.complex64, np.float32]   

        )
        self.power_thres  = power_thres
        self.window_size  = window_size

        self.state        = S_IDLE
        self.sample_count = 0
        
    def work(self, input_items, output_items):
        xin   = input_items[0]   # complex signal
        xmag2 = input_items[1]   # power (or magnitude^2)
        nin   = len(xin)

        output_items[0][:] = 0
        output_items[1][:] = 0

        nout = 0

        for i in range( nin ): 
            mag = xmag2[i]

            if( S_IDLE == self.state ):
                if mag > self.power_thres:
                    self.sample_count = 0
                    self.state = S_PACKET
                else:
                    continue

            if( S_PACKET == self.state ):
                output_items[0][i] = xin[i]
                output_items[1][i] = mag
                nout += 1
                                
                if mag < self.power_thres:
                    self.sample_count += 1
                    if self.sample_count > self.window_size:
                        self.state = S_IDLE
                else:
                    self.sample_count = 0

        self.consume_each(nin)

        return nout