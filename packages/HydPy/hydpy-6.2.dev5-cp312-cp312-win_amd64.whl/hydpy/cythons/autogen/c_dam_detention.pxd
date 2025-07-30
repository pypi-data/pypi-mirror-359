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
cdef public numpy.npy_bool TYPE_CHECKING = False
@cython.final
cdef class Parameters:
    cdef public ControlParameters control
    cdef public DerivedParameters derived
@cython.final
cdef class ControlParameters:
    cdef public double surfacearea
    cdef public double correctionprecipitation
    cdef public double correctionevaporation
    cdef public double weightevaporation
    cdef public double minimumrelease
    cdef public interputils.SimpleInterpolator watervolume2waterlevel
    cdef public double allowedwaterleveldrop
    cdef public double[:] allowedrelease
    cdef public double[:] targetvolume
    cdef public double maximumvolume
    cdef public numpy.int64_t nmbsafereleasemodels
@cython.final
cdef class DerivedParameters:
    cdef public numpy.int64_t[:] toy
    cdef public double seconds
    cdef public double inputfactor
@cython.final
cdef class Sequences:
    cdef public InletSequences inlets
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public StateSequences states
    cdef public LogSequences logs
    cdef public AideSequences aides
    cdef public OutletSequences outlets
    cdef public StateSequences old_states
    cdef public StateSequences new_states
@cython.final
cdef class InletSequences:
    cdef public double[:] q
    cdef public numpy.int64_t _q_ndim
    cdef public numpy.int64_t _q_length
    cdef public numpy.int64_t _q_length_0
    cdef public bint _q_ramflag
    cdef public double[:,:] _q_array
    cdef public bint _q_diskflag_reading
    cdef public bint _q_diskflag_writing
    cdef public double[:] _q_ncarray
    cdef double **_q_pointer
    cdef public numpy.int64_t len_q
    cdef public numpy.int64_t[:] _q_ready
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline alloc_pointer(self, name, numpy.int64_t length)
    cpdef inline dealloc_pointer(self, name)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx)
    cpdef get_pointervalue(self, str name)
    cpdef set_value(self, str name, value)
@cython.final
cdef class FactorSequences:
    cdef public double waterlevel
    cdef public numpy.int64_t _waterlevel_ndim
    cdef public numpy.int64_t _waterlevel_length
    cdef public bint _waterlevel_ramflag
    cdef public double[:] _waterlevel_array
    cdef public bint _waterlevel_diskflag_reading
    cdef public bint _waterlevel_diskflag_writing
    cdef public double[:] _waterlevel_ncarray
    cdef public bint _waterlevel_outputflag
    cdef double *_waterlevel_outputpointer
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value)
    cpdef inline void update_outputs(self) noexcept nogil
@cython.final
cdef class FluxSequences:
    cdef public double precipitation
    cdef public numpy.int64_t _precipitation_ndim
    cdef public numpy.int64_t _precipitation_length
    cdef public bint _precipitation_ramflag
    cdef public double[:] _precipitation_array
    cdef public bint _precipitation_diskflag_reading
    cdef public bint _precipitation_diskflag_writing
    cdef public double[:] _precipitation_ncarray
    cdef public bint _precipitation_outputflag
    cdef double *_precipitation_outputpointer
    cdef public double adjustedprecipitation
    cdef public numpy.int64_t _adjustedprecipitation_ndim
    cdef public numpy.int64_t _adjustedprecipitation_length
    cdef public bint _adjustedprecipitation_ramflag
    cdef public double[:] _adjustedprecipitation_array
    cdef public bint _adjustedprecipitation_diskflag_reading
    cdef public bint _adjustedprecipitation_diskflag_writing
    cdef public double[:] _adjustedprecipitation_ncarray
    cdef public bint _adjustedprecipitation_outputflag
    cdef double *_adjustedprecipitation_outputpointer
    cdef public double potentialevaporation
    cdef public numpy.int64_t _potentialevaporation_ndim
    cdef public numpy.int64_t _potentialevaporation_length
    cdef public bint _potentialevaporation_ramflag
    cdef public double[:] _potentialevaporation_array
    cdef public bint _potentialevaporation_diskflag_reading
    cdef public bint _potentialevaporation_diskflag_writing
    cdef public double[:] _potentialevaporation_ncarray
    cdef public bint _potentialevaporation_outputflag
    cdef double *_potentialevaporation_outputpointer
    cdef public double adjustedevaporation
    cdef public numpy.int64_t _adjustedevaporation_ndim
    cdef public numpy.int64_t _adjustedevaporation_length
    cdef public bint _adjustedevaporation_ramflag
    cdef public double[:] _adjustedevaporation_array
    cdef public bint _adjustedevaporation_diskflag_reading
    cdef public bint _adjustedevaporation_diskflag_writing
    cdef public double[:] _adjustedevaporation_ncarray
    cdef public bint _adjustedevaporation_outputflag
    cdef double *_adjustedevaporation_outputpointer
    cdef public double actualevaporation
    cdef public numpy.int64_t _actualevaporation_ndim
    cdef public numpy.int64_t _actualevaporation_length
    cdef public bint _actualevaporation_ramflag
    cdef public double[:] _actualevaporation_array
    cdef public bint _actualevaporation_diskflag_reading
    cdef public bint _actualevaporation_diskflag_writing
    cdef public double[:] _actualevaporation_ncarray
    cdef public bint _actualevaporation_outputflag
    cdef double *_actualevaporation_outputpointer
    cdef public double inflow
    cdef public numpy.int64_t _inflow_ndim
    cdef public numpy.int64_t _inflow_length
    cdef public bint _inflow_ramflag
    cdef public double[:] _inflow_array
    cdef public bint _inflow_diskflag_reading
    cdef public bint _inflow_diskflag_writing
    cdef public double[:] _inflow_ncarray
    cdef public bint _inflow_outputflag
    cdef double *_inflow_outputpointer
    cdef public double saferelease
    cdef public numpy.int64_t _saferelease_ndim
    cdef public numpy.int64_t _saferelease_length
    cdef public bint _saferelease_ramflag
    cdef public double[:] _saferelease_array
    cdef public bint _saferelease_diskflag_reading
    cdef public bint _saferelease_diskflag_writing
    cdef public double[:] _saferelease_ncarray
    cdef public bint _saferelease_outputflag
    cdef double *_saferelease_outputpointer
    cdef public double aimedrelease
    cdef public numpy.int64_t _aimedrelease_ndim
    cdef public numpy.int64_t _aimedrelease_length
    cdef public bint _aimedrelease_ramflag
    cdef public double[:] _aimedrelease_array
    cdef public bint _aimedrelease_diskflag_reading
    cdef public bint _aimedrelease_diskflag_writing
    cdef public double[:] _aimedrelease_ncarray
    cdef public bint _aimedrelease_outputflag
    cdef double *_aimedrelease_outputpointer
    cdef public double unavoidablerelease
    cdef public numpy.int64_t _unavoidablerelease_ndim
    cdef public numpy.int64_t _unavoidablerelease_length
    cdef public bint _unavoidablerelease_ramflag
    cdef public double[:] _unavoidablerelease_array
    cdef public bint _unavoidablerelease_diskflag_reading
    cdef public bint _unavoidablerelease_diskflag_writing
    cdef public double[:] _unavoidablerelease_ncarray
    cdef public bint _unavoidablerelease_outputflag
    cdef double *_unavoidablerelease_outputpointer
    cdef public double outflow
    cdef public numpy.int64_t _outflow_ndim
    cdef public numpy.int64_t _outflow_length
    cdef public bint _outflow_ramflag
    cdef public double[:] _outflow_array
    cdef public bint _outflow_diskflag_reading
    cdef public bint _outflow_diskflag_writing
    cdef public double[:] _outflow_ncarray
    cdef public bint _outflow_outputflag
    cdef double *_outflow_outputpointer
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value)
    cpdef inline void update_outputs(self) noexcept nogil
@cython.final
cdef class StateSequences:
    cdef public double watervolume
    cdef public numpy.int64_t _watervolume_ndim
    cdef public numpy.int64_t _watervolume_length
    cdef public bint _watervolume_ramflag
    cdef public double[:] _watervolume_array
    cdef public bint _watervolume_diskflag_reading
    cdef public bint _watervolume_diskflag_writing
    cdef public double[:] _watervolume_ncarray
    cdef public bint _watervolume_outputflag
    cdef double *_watervolume_outputpointer
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value)
    cpdef inline void update_outputs(self) noexcept nogil
@cython.final
cdef class LogSequences:
    cdef public double[:] loggedadjustedevaporation
    cdef public numpy.int64_t _loggedadjustedevaporation_ndim
    cdef public numpy.int64_t _loggedadjustedevaporation_length
    cdef public numpy.int64_t _loggedadjustedevaporation_length_0
@cython.final
cdef class AideSequences:
    cdef public double alloweddischarge
    cdef public numpy.int64_t _alloweddischarge_ndim
    cdef public numpy.int64_t _alloweddischarge_length
    cdef public double allowedwaterlevel
    cdef public numpy.int64_t _allowedwaterlevel_ndim
    cdef public numpy.int64_t _allowedwaterlevel_length
@cython.final
cdef class OutletSequences:
    cdef public double q
    cdef public numpy.int64_t _q_ndim
    cdef public numpy.int64_t _q_length
    cdef public bint _q_ramflag
    cdef public double[:] _q_array
    cdef public bint _q_diskflag_reading
    cdef public bint _q_diskflag_writing
    cdef public double[:] _q_ncarray
    cdef double *_q_pointer
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value)
    cpdef get_pointervalue(self, str name)
    cpdef set_value(self, str name, value)
@cython.final
cdef class PegasusWaterVolume(rootutils.PegasusBase):
    cdef public Model model
    cpdef double apply_method0(self, double x)  noexcept nogil
@cython.final
cdef class Model(masterinterface.MasterInterface):
    cdef public numpy.npy_bool threading
    cdef public Parameters parameters
    cdef public Sequences sequences
    cdef public masterinterface.MasterInterface pemodel
    cdef public numpy.npy_bool pemodel_is_mainmodel
    cdef public numpy.int64_t pemodel_typeid
    cdef public masterinterface.MasterInterface precipmodel
    cdef public numpy.npy_bool precipmodel_is_mainmodel
    cdef public numpy.int64_t precipmodel_typeid
    cdef public interfaceutils.SubmodelsProperty safereleasemodels
    cdef public PegasusWaterVolume pegasuswatervolume
    cpdef inline void simulate(self, numpy.int64_t idx)  noexcept nogil
    cpdef void simulate_period(self, numpy.int64_t i0, numpy.int64_t i1)  noexcept nogil
    cpdef void reset_reuseflags(self) noexcept nogil
    cpdef void load_data(self, numpy.int64_t idx) noexcept nogil
    cpdef void save_data(self, numpy.int64_t idx) noexcept nogil
    cpdef void new2old(self) noexcept nogil
    cpdef inline void run(self) noexcept nogil
    cpdef void update_inlets(self) noexcept nogil
    cpdef void update_outlets(self) noexcept nogil
    cpdef void update_observers(self) noexcept nogil
    cpdef void update_receivers(self, numpy.int64_t idx) noexcept nogil
    cpdef void update_senders(self, numpy.int64_t idx) noexcept nogil
    cpdef void update_outputs(self) noexcept nogil
    cpdef inline void pick_inflow_v1(self) noexcept nogil
    cpdef inline void calc_precipitation_v1(self) noexcept nogil
    cpdef inline void calc_adjustedprecipitation_v1(self) noexcept nogil
    cpdef inline void calc_potentialevaporation_v1(self) noexcept nogil
    cpdef inline void calc_adjustedevaporation_v1(self) noexcept nogil
    cpdef inline void calc_allowedwaterlevel_v1(self) noexcept nogil
    cpdef inline void calc_alloweddischarge_v3(self) noexcept nogil
    cpdef inline void update_watervolume_v5(self) noexcept nogil
    cpdef inline void calc_actualevaporation_watervolume_v1(self) noexcept nogil
    cpdef inline void calc_saferelease_v1(self) noexcept nogil
    cpdef inline void calc_aimedrelease_watervolume_v1(self) noexcept nogil
    cpdef inline void calc_unavoidablerelease_watervolume_v1(self) noexcept nogil
    cpdef inline void calc_waterlevel_v1(self) noexcept nogil
    cpdef inline void calc_outflow_v6(self) noexcept nogil
    cpdef inline double return_waterlevelerror_v1(self, double watervolume) noexcept nogil
    cpdef inline void pass_outflow_v1(self) noexcept nogil
    cpdef inline void pick_inflow(self) noexcept nogil
    cpdef inline void calc_precipitation(self) noexcept nogil
    cpdef inline void calc_adjustedprecipitation(self) noexcept nogil
    cpdef inline void calc_potentialevaporation(self) noexcept nogil
    cpdef inline void calc_adjustedevaporation(self) noexcept nogil
    cpdef inline void calc_allowedwaterlevel(self) noexcept nogil
    cpdef inline void calc_alloweddischarge(self) noexcept nogil
    cpdef inline void update_watervolume(self) noexcept nogil
    cpdef inline void calc_actualevaporation_watervolume(self) noexcept nogil
    cpdef inline void calc_saferelease(self) noexcept nogil
    cpdef inline void calc_aimedrelease_watervolume(self) noexcept nogil
    cpdef inline void calc_unavoidablerelease_watervolume(self) noexcept nogil
    cpdef inline void calc_waterlevel(self) noexcept nogil
    cpdef inline void calc_outflow(self) noexcept nogil
    cpdef inline double return_waterlevelerror(self, double watervolume) noexcept nogil
    cpdef inline void pass_outflow(self) noexcept nogil
