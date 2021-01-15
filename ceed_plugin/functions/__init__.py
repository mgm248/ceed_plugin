from ceed.function.plugin import ConstFunc
from ceed.function import CeedFunc
from kivy.properties import NumericProperty, StringProperty
from random import shuffle


class StackDelayFunc(ConstFunc):
    """Defines a function which returns a constant value.

    The function is defined as ``y(t) = a``.
    """
    delays = None

    offset_step = NumericProperty(.01)

    stim_duration = NumericProperty(1.)

    offset_name = StringProperty('Stack0')

    named_delay_count = {'Stack0': 0, 'Stack1': 1, 'Stack2': 2}

    def __init__(self, name='StackDelay', description='y(t) = a', **kwargs):
        super().__init__(
            name=name, description=description, **kwargs)

    def __call__(self, t):
        super().__call__(t)
        t = t - self.t_start + self.t_offset
        offset = self.delays[self.loop_count]
        count = self.named_delay_count[self.offset_name]

        if t < offset * count or t >= offset * (3 - count - 1):
            return 0
        return self.a

    def get_state(self, *largs, **kwargs):
        d = super().get_state(*largs, **kwargs)
        d['offset_step'] = self.offset_step
        d['stim_duration'] = self.stim_duration
        d['offset_name'] = self.offset_name
        return d

    def get_gui_props(self):
        d = super().get_gui_props()
        d['offset_step'] = None
        d['stim_duration'] = None
        d['offset_name'] = None
        return d

    def init_func(self, t_start):
        self.compute_delays()

        super().init_func(t_start)
        self.duration = self.delays[0] * 2 + self.stim_duration

    def init_loop_iteration(self, t_start):
        super().init_loop_iteration(t_start)
        self.duration = self.delays[self.loop_count] * 2 + self.stim_duration

    def compute_delays(self):
        if StackDelayFunc.delays is not None:
            return

        offset = self.offset_step
        loops = self.loop
        delays = [i * offset for i in range(loops)]
        shuffle(delays)
        StackDelayFunc.delays = delays


class RandomDelayFunc(CeedFunc):

    delay_unit = NumericProperty(.01)

    num_repeats = NumericProperty(0)

    sampled_units = []

    current_sampled_units = []

    def __init__(self, name='RandomDelay', description='y(t) = 0', **kwargs):
        super().__init__(
            name=name, description=description, **kwargs)

    def __call__(self, t):
        super().__call__(t)
        return 0

    def get_state(self, *largs, **kwargs):
        d = super().get_state(*largs, **kwargs)
        d['delay_unit'] = self.delay_unit
        d['num_repeats'] = self.num_repeats
        d['sampled_units'] = self.sampled_units
        return d

    def get_gui_props(self):
        d = super().get_gui_props()
        d['delay_unit'] = None
        d['num_repeats'] = None
        return d

    def resample_parameters(self, is_forked=False):
        if not is_forked:
            self.sampled_units = [
                i * self.delay_unit for i in range(self.num_repeats)]
            shuffle(self.sampled_units)
        else:
            self.current_sampled_units = self.sampled_units[:]

        super().resample_parameters(is_forked)

    def init_func(self, t_start):
        super().init_func(t_start)
        self.duration = self.current_sampled_units.pop(0)


def get_ceed_functions():
    return StackDelayFunc, RandomDelayFunc
