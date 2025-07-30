#!python
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# cython: language_level=3
# cython: cpow=True
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True
from typing import Optional
import numpy
cimport numpy
from libc.math cimport exp, fabs, log, sin, cos, tan, tanh, asin, acos, atan, isnan, isinf
from libc.math cimport NAN as nan
from libc.math cimport INFINITY as inf
import cython
from cpython.mem cimport PyMem_Malloc
from cpython.mem cimport PyMem_Realloc
from cpython.mem cimport PyMem_Free
from hydpy.cythons.autogen cimport configutils
from hydpy.cythons.autogen cimport interfaceutils
from hydpy.cythons.autogen cimport interputils
from hydpy.cythons.autogen import pointerutils
from hydpy.cythons.autogen cimport pointerutils
from hydpy.cythons.autogen cimport quadutils
from hydpy.cythons.autogen cimport rootutils
from hydpy.cythons.autogen cimport smoothutils
from hydpy.cythons.autogen cimport masterinterface


cdef void do_nothing(Model model)  noexcept nogil:
    pass

cpdef get_wrapper():
    cdef CallbackWrapper wrapper = CallbackWrapper()
    wrapper.callback = do_nothing
    return wrapper

@cython.final
cdef class Sequences:
    pass
@cython.final
cdef class ReceiverSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._waterlevel_diskflag_reading:
            self.waterlevel = self._waterlevel_ncarray[0]
        elif self._waterlevel_ramflag:
            self.waterlevel = self._waterlevel_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._waterlevel_diskflag_writing:
            self._waterlevel_ncarray[0] = self.waterlevel
        if self._waterlevel_ramflag:
            self._waterlevel_array[idx] = self.waterlevel
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "waterlevel":
            self._waterlevel_pointer = pointer.p_value
    cpdef get_pointervalue(self, str name):
        cdef numpy.int64_t idx
        if name == "waterlevel":
            return self._waterlevel_pointer[0]
    cpdef set_value(self, str name, value):
        if name == "waterlevel":
            self._waterlevel_pointer[0] = value
@cython.final
cdef class LogSequences:
    pass
@cython.final
cdef class Model(masterinterface.MasterInterface):
    cpdef inline void simulate(self, numpy.int64_t idx)  noexcept nogil:
        self.idx_sim = idx
        self.load_data(idx)
        self.run()
    cpdef void simulate_period(self, numpy.int64_t i0, numpy.int64_t i1)  noexcept nogil:
        cdef numpy.int64_t i
        with nogil:
            for i in range(i0, i1):
                self.simulate(i)
                self.update_senders(i)
                self.update_receivers(i)
                self.save_data(i)
    cpdef void reset_reuseflags(self) noexcept nogil:
        pass
    cpdef void load_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.receivers.load_data(idx)
    cpdef void save_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.receivers.save_data(idx)
    cpdef inline void run(self) noexcept nogil:
        pass
    cpdef void update_inlets(self) noexcept nogil:
        cdef numpy.int64_t i
        pass
    cpdef void update_outlets(self) noexcept nogil:
        pass
        cdef numpy.int64_t i
    cpdef void update_observers(self) noexcept nogil:
        cdef numpy.int64_t i
        pass
    cpdef void update_receivers(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        cdef numpy.int64_t i
        if not self.threading:
            self.sequences.receivers.waterlevel = self.sequences.receivers._waterlevel_pointer[0]
        self.pick_loggedwaterlevel_v1()
    cpdef void update_senders(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        pass
        cdef numpy.int64_t i
    cpdef void update_outputs(self) noexcept nogil:
        pass
    cpdef inline void pick_loggedwaterlevel_v1(self) noexcept nogil:
        self.sequences.logs.loggedwaterlevel[0] = self.sequences.receivers.waterlevel
    cpdef double get_waterlevel_v1(self) noexcept nogil:
        return self.sequences.logs.loggedwaterlevel[0]
    cpdef inline void pick_loggedwaterlevel(self) noexcept nogil:
        self.sequences.logs.loggedwaterlevel[0] = self.sequences.receivers.waterlevel
    cpdef double get_waterlevel(self) noexcept nogil:
        return self.sequences.logs.loggedwaterlevel[0]
