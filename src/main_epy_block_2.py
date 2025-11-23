import numpy as np
from gnuradio import gr

class basic_block(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__( self ):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Coarse CFO Correction',   # will show up in GRC
            in_sig=[np.complex64, np.complex64 ],
            out_sig=[np.complex64 ]
        )

    def work(self, input_items, output_items):
        xin   = input_items[0]   # complex signal
        xprod = input_items[1]   # complex product between the signal and the signal delayed

        rotation = np.exp(-1j * np.angle(xprod) / 16).astype(np.complex64)
        output_items[0][:] = xin * rotation

        return len(xin)