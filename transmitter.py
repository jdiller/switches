import time
import pigpio

class Transmitter(object):
   """
   A class to transmit the wireless codes sent by 433 MHz
   wireless fobs.
   """
   def __init__(self, pi, gpio, repeats=6, bits=24, gap=5800, t0=180, t1=560):
      """
      Instantiate with the Pi and the GPIO connected to the wireless
      transmitter.

      """
      self.pi = pi
      self.gpio = gpio
      self.repeats = repeats
      self.bits = bits
      self.gap = gap
      self.t0 = t0
      self.t1 = t1

      self._make_waves()

      pi.set_mode(gpio, pigpio.OUTPUT)

   def _make_waves(self):
      """
      Generates the basic waveforms needed to transmit codes.
      """
      wf = []
      wf.append(pigpio.pulse(1<<self.gpio, 0, self.t0))
      wf.append(pigpio.pulse(0, 1<<self.gpio, self.gap))
      self.pi.wave_add_generic(wf)
      self._amble = self.pi.wave_create()

      wf = []
      wf.append(pigpio.pulse(1<<self.gpio, 0, self.t0))
      wf.append(pigpio.pulse(0, 1<<self.gpio, self.t1))
      self.pi.wave_add_generic(wf)
      self._wid0 = self.pi.wave_create()

      wf = []
      wf.append(pigpio.pulse(1<<self.gpio, 0, self.t1))
      wf.append(pigpio.pulse(0, 1<<self.gpio, self.t0))
      self.pi.wave_add_generic(wf)
      self._wid1 = self.pi.wave_create()

   def set_repeats(self, repeats):
      """
      Set the number of code repeats.
      """
      if 1 < repeats < 100:
         self.repeats = repeats

   def set_bits(self, bits):
      """
      Set the number of code bits.
      """
      if 5 < bits < 65:
         self.bits = bits

   def set_timings(self, gap, t0, t1):
      """
      Sets the code gap, short pulse, and long pulse length in us.
      """
      self.gap = gap
      self.t0 = t0
      self.t1 = t1

      self.pi.wave_delete(self._amble)
      self.pi.wave_delete(self._wid0)
      self.pi.wave_delete(self._wid1)

      self._make_waves()

   def send(self, code):
      """
      Transmits the code (using the current settings of repeats,
      bits, gap, short, and long pulse length).
      """
      chain = [self._amble, 255, 0]

      bit = (1<<(self.bits-1))
      for i in range(self.bits):
         if code & bit:
            chain += [self._wid1]
         else:
            chain += [self._wid0]
         bit = bit >> 1

      chain += [self._amble, 255, 1, self.repeats, 0]

      self.pi.wave_chain(chain)

      while self.pi.wave_tx_busy():
         time.sleep(0.1)

   def cancel(self):
      """
      Cancels the wireless code transmitter.
      """
      self.pi.wave_delete(self._amble)
      self.pi.wave_delete(self._wid0)
      self.pi.wave_delete(self._wid1)

