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
ctypedef void (*CallbackType) (Model)  noexcept nogil
cdef class CallbackWrapper:
    cdef CallbackType callback
@cython.final
cdef class Parameters:
    cdef public ControlParameters control
@cython.final
cdef class ControlParameters:
    cdef public numpy.int64_t observernodes
    cdef public interputils.SimpleInterpolator x2y
@cython.final
cdef class Sequences:
    cdef public ObserverSequences observers
    cdef public FactorSequences factors
    cdef public SenderSequences senders
@cython.final
cdef class ObserverSequences:
    cdef public double[:] x
    cdef public numpy.int64_t _x_ndim
    cdef public numpy.int64_t _x_length
    cdef public numpy.int64_t _x_length_0
    cdef public bint _x_ramflag
    cdef public double[:,:] _x_array
    cdef public bint _x_diskflag_reading
    cdef public bint _x_diskflag_writing
    cdef public double[:] _x_ncarray
    cdef double **_x_pointer
    cdef public numpy.int64_t len_x
    cdef public numpy.int64_t[:] _x_ready
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline alloc_pointer(self, name, numpy.int64_t length)
    cpdef inline dealloc_pointer(self, name)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx)
    cpdef get_pointervalue(self, str name)
    cpdef set_value(self, str name, value)
@cython.final
cdef class FactorSequences:
    cdef public double x
    cdef public numpy.int64_t _x_ndim
    cdef public numpy.int64_t _x_length
    cdef public bint _x_ramflag
    cdef public double[:] _x_array
    cdef public bint _x_diskflag_reading
    cdef public bint _x_diskflag_writing
    cdef public double[:] _x_ncarray
    cdef public bint _x_outputflag
    cdef double *_x_outputpointer
    cdef public double y
    cdef public numpy.int64_t _y_ndim
    cdef public numpy.int64_t _y_length
    cdef public bint _y_ramflag
    cdef public double[:] _y_array
    cdef public bint _y_diskflag_reading
    cdef public bint _y_diskflag_writing
    cdef public double[:] _y_ncarray
    cdef public bint _y_outputflag
    cdef double *_y_outputpointer
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value)
    cpdef inline void update_outputs(self) noexcept nogil
@cython.final
cdef class SenderSequences:
    cdef public double[:] y
    cdef public numpy.int64_t _y_ndim
    cdef public numpy.int64_t _y_length
    cdef public numpy.int64_t _y_length_0
    cdef public bint _y_ramflag
    cdef public double[:,:] _y_array
    cdef public bint _y_diskflag_reading
    cdef public bint _y_diskflag_writing
    cdef public double[:] _y_ncarray
    cdef double **_y_pointer
    cdef public numpy.int64_t len_y
    cdef public numpy.int64_t[:] _y_ready
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline alloc_pointer(self, name, numpy.int64_t length)
    cpdef inline dealloc_pointer(self, name)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx)
    cpdef get_pointervalue(self, str name)
    cpdef set_value(self, str name, value)
@cython.final
cdef class Model(masterinterface.MasterInterface):
    cdef public numpy.npy_bool threading
    cdef public Parameters parameters
    cdef public Sequences sequences
    cpdef inline void simulate(self, numpy.int64_t idx)  noexcept nogil
    cpdef void simulate_period(self, numpy.int64_t i0, numpy.int64_t i1)  noexcept nogil
    cpdef void reset_reuseflags(self) noexcept nogil
    cpdef void load_data(self, numpy.int64_t idx) noexcept nogil
    cpdef void save_data(self, numpy.int64_t idx) noexcept nogil
    cpdef inline void run(self) noexcept nogil
    cpdef void update_inlets(self) noexcept nogil
    cpdef void update_outlets(self) noexcept nogil
    cpdef void update_observers(self) noexcept nogil
    cpdef void update_receivers(self, numpy.int64_t idx) noexcept nogil
    cpdef void update_senders(self, numpy.int64_t idx) noexcept nogil
    cpdef void update_outputs(self) noexcept nogil
    cpdef inline void pick_x_v1(self) noexcept nogil
    cpdef inline void calc_y_v1(self) noexcept nogil
    cpdef inline void pass_y_v1(self) noexcept nogil
    cpdef double get_y_v1(self) noexcept nogil
    cpdef inline void pick_x(self) noexcept nogil
    cpdef inline void calc_y(self) noexcept nogil
    cpdef inline void pass_y(self) noexcept nogil
    cpdef double get_y(self) noexcept nogil
    cpdef void determine_y_v1(self) noexcept nogil
    cpdef void determine_y(self) noexcept nogil
