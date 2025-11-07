import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block):
  def __init__(self):
    gr.sync_block.__init__(
      self,
      name="Stream Tagger",
      in_sig=[np.complex64, np.float32, np.uint8],
      out_sig=[np.complex64],
    )

  def work(self, input_items, output_items):
    x_in, cfo_in, trig_in = input_items
    x_out = output_items[0]
    x_out[:] = x_in

    for i in range(len(trig_in)):
      if trig_in[i] == 1:  # plateau pulse
        key = pmt.string_to_symbol("frame_start")
        val = pmt.from_double(float(cfo_in[i]))
        src = pmt.string_to_symbol("frame_start_tagger")
        self.add_item_tag(0, self.nitems_written(0) + i, key, val, src)

    return len(x_out)
