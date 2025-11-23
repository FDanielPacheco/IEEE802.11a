import numpy as np
from gnuradio import gr
import pmt

S_SEARCH = 0
S_COPY   = 1

MIN_GAP = 480
MAX_SAMPLES = 540 * 80  # maximum samples to forward

class sync_short_py(gr.sync_block):
    """
    Python implementation of the GNU Radio sync_short block.
    Detects short preamble plateaus, applies coarse CFO correction, and forwards samples.
    """

    def __init__(self, threshold=0.7, min_plateau=20, log=False):
        gr.sync_block.__init__(
            self,
            name='sync_short_py',
            in_sig=[np.complex64, np.complex64, np.float32],  # [signal, delayed conjugate, correlation]
            out_sig=[np.complex64]
        )

        self.threshold = threshold
        self.min_plateau = min_plateau
        self.log = log

        # State machine
        self.state = S_SEARCH
        self.plateau_count = 0
        self.copied_count = 0
        self.freq_offset = 0.0

    def insert_tag(self, item, freq_offset, input_item):
        key = pmt.string_to_symbol("wifi_start")
        value = pmt.from_double(freq_offset)
        srcid = pmt.string_to_symbol(self.name())
        self.add_item_tag(0, item, key, value, srcid)
        if self.log:
            print(f"[sync_short_py] Tag inserted at out index {item}, freq_offset={freq_offset}, input index={input_item}")

    def work(self, input_items, output_items):
        xin   = input_items[0]
        xdel  = input_items[1]
        corr  = input_items[2]
        out   = output_items[0]

        ninput = min(len(xin), len(xdel), len(corr))
        nout = 0
        i = 0

        while i < ninput:
            if self.state == S_SEARCH:
                if corr[i] > self.threshold:
                    self.plateau_count += 1
                    if self.plateau_count >= self.min_plateau:
                        # Transition to COPY
                        self.state = S_COPY
                        self.copied_count = 0
                        self.freq_offset = np.angle(xdel[i]) / 16.0
                        self.plateau_count = 0
                        self.insert_tag(nout, self.freq_offset, i)
                        if self.log:
                            print(f"[sync_short_py] SHORT Frame detected at input index {i}")
                        continue
                else:
                    self.plateau_count = 0
                i += 1

            elif self.state == S_COPY:
                if self.copied_count >= MAX_SAMPLES:
                    self.state = S_SEARCH
                    self.copied_count = 0
                    if self.log:
                        print(f"[sync_short_py] Reached MAX_SAMPLES, returning to SEARCH")
                    break

                # Coarse CFO correction
                rotation = np.exp(-1j * self.freq_offset * self.copied_count)
                out[nout] = xin[i] * rotation

                nout += 1
                self.copied_count += 1
                i += 1

        self.consume_each(i)
        return nout
