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
cdef class Parameters:
    pass
@cython.final
cdef class ControlParameters:
    pass
@cython.final
cdef class Sequences:
    pass
@cython.final
cdef class ObserverSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._x_diskflag_reading:
            k = 0
            for jdx0 in range(self._x_length_0):
                self.x[jdx0] = self._x_ncarray[k]
                k += 1
        elif self._x_ramflag:
            for jdx0 in range(self._x_length_0):
                self.x[jdx0] = self._x_array[idx, jdx0]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._x_diskflag_writing:
            k = 0
            for jdx0 in range(self._x_length_0):
                self._x_ncarray[k] = self.x[jdx0]
                k += 1
        if self._x_ramflag:
            for jdx0 in range(self._x_length_0):
                self._x_array[idx, jdx0] = self.x[jdx0]
    cpdef inline alloc_pointer(self, name, numpy.int64_t length):
        if name == "x":
            self._x_length_0 = length
            self._x_ready = numpy.full(length, 0, dtype=numpy.int64)
            self._x_pointer = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc_pointer(self, name):
        if name == "x":
            PyMem_Free(self._x_pointer)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "x":
            self._x_pointer[idx] = pointer.p_value
            self._x_ready[idx] = 1
    cpdef get_pointervalue(self, str name):
        cdef numpy.int64_t idx
        if name == "x":
            values = numpy.empty(self.len_x)
            for idx in range(self.len_x):
                pointerutils.check0(self._x_length_0)
                if self._x_ready[idx] == 0:
                    pointerutils.check1(self._x_length_0, idx)
                    pointerutils.check2(self._x_ready, idx)
                values[idx] = self._x_pointer[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "x":
            for idx in range(self.len_x):
                pointerutils.check0(self._x_length_0)
                if self._x_ready[idx] == 0:
                    pointerutils.check1(self._x_length_0, idx)
                    pointerutils.check2(self._x_ready, idx)
                self._x_pointer[idx][0] = value[idx]
@cython.final
cdef class FactorSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._x_diskflag_reading:
            self.x = self._x_ncarray[0]
        elif self._x_ramflag:
            self.x = self._x_array[idx]
        if self._y_diskflag_reading:
            self.y = self._y_ncarray[0]
        elif self._y_ramflag:
            self.y = self._y_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._x_diskflag_writing:
            self._x_ncarray[0] = self.x
        if self._x_ramflag:
            self._x_array[idx] = self.x
        if self._y_diskflag_writing:
            self._y_ncarray[0] = self.y
        if self._y_ramflag:
            self._y_array[idx] = self.y
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "x":
            self._x_outputpointer = value.p_value
        if name == "y":
            self._y_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._x_outputflag:
            self._x_outputpointer[0] = self.x
        if self._y_outputflag:
            self._y_outputpointer[0] = self.y
@cython.final
cdef class SenderSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._y_diskflag_reading:
            k = 0
            for jdx0 in range(self._y_length_0):
                self.y[jdx0] = self._y_ncarray[k]
                k += 1
        elif self._y_ramflag:
            for jdx0 in range(self._y_length_0):
                self.y[jdx0] = self._y_array[idx, jdx0]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._y_diskflag_writing:
            k = 0
            for jdx0 in range(self._y_length_0):
                self._y_ncarray[k] = self.y[jdx0]
                k += 1
        if self._y_ramflag:
            for jdx0 in range(self._y_length_0):
                self._y_array[idx, jdx0] = self.y[jdx0]
    cpdef inline alloc_pointer(self, name, numpy.int64_t length):
        if name == "y":
            self._y_length_0 = length
            self._y_ready = numpy.full(length, 0, dtype=numpy.int64)
            self._y_pointer = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc_pointer(self, name):
        if name == "y":
            PyMem_Free(self._y_pointer)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "y":
            self._y_pointer[idx] = pointer.p_value
            self._y_ready[idx] = 1
    cpdef get_pointervalue(self, str name):
        cdef numpy.int64_t idx
        if name == "y":
            values = numpy.empty(self.len_y)
            for idx in range(self.len_y):
                pointerutils.check0(self._y_length_0)
                if self._y_ready[idx] == 0:
                    pointerutils.check1(self._y_length_0, idx)
                    pointerutils.check2(self._y_ready, idx)
                values[idx] = self._y_pointer[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "y":
            for idx in range(self.len_y):
                pointerutils.check0(self._y_length_0)
                if self._y_ready[idx] == 0:
                    pointerutils.check1(self._y_length_0, idx)
                    pointerutils.check2(self._y_ready, idx)
                self._y_pointer[idx][0] = value[idx]
@cython.final
cdef class Model(masterinterface.MasterInterface):
    cpdef inline void simulate(self, numpy.int64_t idx)  noexcept nogil:
        self.idx_sim = idx
        self.load_data(idx)
        self.update_observers()
        self.run()
        self.update_outputs()
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
        self.sequences.observers.load_data(idx)
    cpdef void save_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.observers.save_data(idx)
        self.sequences.factors.save_data(idx)
        self.sequences.senders.save_data(idx)
    cpdef inline void run(self) noexcept nogil:
        self.calc_y_v1()
    cpdef void update_inlets(self) noexcept nogil:
        cdef numpy.int64_t i
        pass
    cpdef void update_outlets(self) noexcept nogil:
        pass
        cdef numpy.int64_t i
    cpdef void update_observers(self) noexcept nogil:
        cdef numpy.int64_t i
        if not self.threading:
            for i in range(self.sequences.observers._x_length_0):
                if self.sequences.observers._x_ready[i]:
                    self.sequences.observers.x[i] = self.sequences.observers._x_pointer[i][0]
                else:
                    self.sequences.observers.x[i] = nan
        self.pick_x_v1()
    cpdef void update_receivers(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        cdef numpy.int64_t i
        pass
    cpdef void update_senders(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.pass_y_v1()
        cdef numpy.int64_t i
        if not self.threading:
            for i in range(self.sequences.senders._y_length_0):
                if self.sequences.senders._y_ready[i]:
                    self.sequences.senders._y_pointer[i][0] = self.sequences.senders._y_pointer[i][0] + self.sequences.senders.y[i]
    cpdef void update_outputs(self) noexcept nogil:
        if not self.threading:
            self.sequences.factors.update_outputs()
    cpdef inline void pick_x_v1(self) noexcept nogil:
        cdef numpy.int64_t i
        self.sequences.factors.x = 0.0
        for i in range(self.parameters.control.observernodes):
            self.sequences.factors.x = self.sequences.factors.x + (self.sequences.observers.x[i])
    cpdef inline void calc_y_v1(self) noexcept nogil:
        self.parameters.control.x2y.inputs[0] = self.sequences.factors.x
        self.parameters.control.x2y.calculate_values()
        self.sequences.factors.y = self.parameters.control.x2y.outputs[0]
    cpdef inline void pass_y_v1(self) noexcept nogil:
        cdef numpy.int64_t i
        for i in range(self.sequences.senders.len_y):
            self.sequences.senders.y[i] = self.sequences.factors.y
    cpdef double get_y_v1(self) noexcept nogil:
        return self.sequences.factors.y
    cpdef inline void pick_x(self) noexcept nogil:
        cdef numpy.int64_t i
        self.sequences.factors.x = 0.0
        for i in range(self.parameters.control.observernodes):
            self.sequences.factors.x = self.sequences.factors.x + (self.sequences.observers.x[i])
    cpdef inline void calc_y(self) noexcept nogil:
        self.parameters.control.x2y.inputs[0] = self.sequences.factors.x
        self.parameters.control.x2y.calculate_values()
        self.sequences.factors.y = self.parameters.control.x2y.outputs[0]
    cpdef inline void pass_y(self) noexcept nogil:
        cdef numpy.int64_t i
        for i in range(self.sequences.senders.len_y):
            self.sequences.senders.y[i] = self.sequences.factors.y
    cpdef double get_y(self) noexcept nogil:
        return self.sequences.factors.y
    cpdef void determine_y_v1(self) noexcept nogil:
        self.pick_x_v1()
        self.calc_y_v1()
    cpdef void determine_y(self) noexcept nogil:
        self.pick_x_v1()
        self.calc_y_v1()
