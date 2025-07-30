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

cdef public numpy.npy_bool TYPE_CHECKING = False
@cython.final
cdef class Parameters:
    pass
@cython.final
cdef class ControlParameters:
    pass
@cython.final
cdef class DerivedParameters:
    pass
@cython.final
cdef class Sequences:
    pass
@cython.final
cdef class InletSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._q_diskflag_reading:
            k = 0
            for jdx0 in range(self._q_length_0):
                self.q[jdx0] = self._q_ncarray[k]
                k += 1
        elif self._q_ramflag:
            for jdx0 in range(self._q_length_0):
                self.q[jdx0] = self._q_array[idx, jdx0]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._q_diskflag_writing:
            k = 0
            for jdx0 in range(self._q_length_0):
                self._q_ncarray[k] = self.q[jdx0]
                k += 1
        if self._q_ramflag:
            for jdx0 in range(self._q_length_0):
                self._q_array[idx, jdx0] = self.q[jdx0]
    cpdef inline alloc_pointer(self, name, numpy.int64_t length):
        if name == "q":
            self._q_length_0 = length
            self._q_ready = numpy.full(length, 0, dtype=numpy.int64)
            self._q_pointer = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc_pointer(self, name):
        if name == "q":
            PyMem_Free(self._q_pointer)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "q":
            self._q_pointer[idx] = pointer.p_value
            self._q_ready[idx] = 1
    cpdef get_pointervalue(self, str name):
        cdef numpy.int64_t idx
        if name == "q":
            values = numpy.empty(self.len_q)
            for idx in range(self.len_q):
                pointerutils.check0(self._q_length_0)
                if self._q_ready[idx] == 0:
                    pointerutils.check1(self._q_length_0, idx)
                    pointerutils.check2(self._q_ready, idx)
                values[idx] = self._q_pointer[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "q":
            for idx in range(self.len_q):
                pointerutils.check0(self._q_length_0)
                if self._q_ready[idx] == 0:
                    pointerutils.check1(self._q_length_0, idx)
                    pointerutils.check2(self._q_ready, idx)
                self._q_pointer[idx][0] = value[idx]
@cython.final
cdef class FactorSequences:
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
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "waterlevel":
            self._waterlevel_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._waterlevel_outputflag:
            self._waterlevel_outputpointer[0] = self.waterlevel
@cython.final
cdef class FluxSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._precipitation_diskflag_reading:
            self.precipitation = self._precipitation_ncarray[0]
        elif self._precipitation_ramflag:
            self.precipitation = self._precipitation_array[idx]
        if self._adjustedprecipitation_diskflag_reading:
            self.adjustedprecipitation = self._adjustedprecipitation_ncarray[0]
        elif self._adjustedprecipitation_ramflag:
            self.adjustedprecipitation = self._adjustedprecipitation_array[idx]
        if self._potentialevaporation_diskflag_reading:
            self.potentialevaporation = self._potentialevaporation_ncarray[0]
        elif self._potentialevaporation_ramflag:
            self.potentialevaporation = self._potentialevaporation_array[idx]
        if self._adjustedevaporation_diskflag_reading:
            self.adjustedevaporation = self._adjustedevaporation_ncarray[0]
        elif self._adjustedevaporation_ramflag:
            self.adjustedevaporation = self._adjustedevaporation_array[idx]
        if self._actualevaporation_diskflag_reading:
            self.actualevaporation = self._actualevaporation_ncarray[0]
        elif self._actualevaporation_ramflag:
            self.actualevaporation = self._actualevaporation_array[idx]
        if self._inflow_diskflag_reading:
            self.inflow = self._inflow_ncarray[0]
        elif self._inflow_ramflag:
            self.inflow = self._inflow_array[idx]
        if self._saferelease_diskflag_reading:
            self.saferelease = self._saferelease_ncarray[0]
        elif self._saferelease_ramflag:
            self.saferelease = self._saferelease_array[idx]
        if self._aimedrelease_diskflag_reading:
            self.aimedrelease = self._aimedrelease_ncarray[0]
        elif self._aimedrelease_ramflag:
            self.aimedrelease = self._aimedrelease_array[idx]
        if self._unavoidablerelease_diskflag_reading:
            self.unavoidablerelease = self._unavoidablerelease_ncarray[0]
        elif self._unavoidablerelease_ramflag:
            self.unavoidablerelease = self._unavoidablerelease_array[idx]
        if self._outflow_diskflag_reading:
            self.outflow = self._outflow_ncarray[0]
        elif self._outflow_ramflag:
            self.outflow = self._outflow_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._precipitation_diskflag_writing:
            self._precipitation_ncarray[0] = self.precipitation
        if self._precipitation_ramflag:
            self._precipitation_array[idx] = self.precipitation
        if self._adjustedprecipitation_diskflag_writing:
            self._adjustedprecipitation_ncarray[0] = self.adjustedprecipitation
        if self._adjustedprecipitation_ramflag:
            self._adjustedprecipitation_array[idx] = self.adjustedprecipitation
        if self._potentialevaporation_diskflag_writing:
            self._potentialevaporation_ncarray[0] = self.potentialevaporation
        if self._potentialevaporation_ramflag:
            self._potentialevaporation_array[idx] = self.potentialevaporation
        if self._adjustedevaporation_diskflag_writing:
            self._adjustedevaporation_ncarray[0] = self.adjustedevaporation
        if self._adjustedevaporation_ramflag:
            self._adjustedevaporation_array[idx] = self.adjustedevaporation
        if self._actualevaporation_diskflag_writing:
            self._actualevaporation_ncarray[0] = self.actualevaporation
        if self._actualevaporation_ramflag:
            self._actualevaporation_array[idx] = self.actualevaporation
        if self._inflow_diskflag_writing:
            self._inflow_ncarray[0] = self.inflow
        if self._inflow_ramflag:
            self._inflow_array[idx] = self.inflow
        if self._saferelease_diskflag_writing:
            self._saferelease_ncarray[0] = self.saferelease
        if self._saferelease_ramflag:
            self._saferelease_array[idx] = self.saferelease
        if self._aimedrelease_diskflag_writing:
            self._aimedrelease_ncarray[0] = self.aimedrelease
        if self._aimedrelease_ramflag:
            self._aimedrelease_array[idx] = self.aimedrelease
        if self._unavoidablerelease_diskflag_writing:
            self._unavoidablerelease_ncarray[0] = self.unavoidablerelease
        if self._unavoidablerelease_ramflag:
            self._unavoidablerelease_array[idx] = self.unavoidablerelease
        if self._outflow_diskflag_writing:
            self._outflow_ncarray[0] = self.outflow
        if self._outflow_ramflag:
            self._outflow_array[idx] = self.outflow
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "precipitation":
            self._precipitation_outputpointer = value.p_value
        if name == "adjustedprecipitation":
            self._adjustedprecipitation_outputpointer = value.p_value
        if name == "potentialevaporation":
            self._potentialevaporation_outputpointer = value.p_value
        if name == "adjustedevaporation":
            self._adjustedevaporation_outputpointer = value.p_value
        if name == "actualevaporation":
            self._actualevaporation_outputpointer = value.p_value
        if name == "inflow":
            self._inflow_outputpointer = value.p_value
        if name == "saferelease":
            self._saferelease_outputpointer = value.p_value
        if name == "aimedrelease":
            self._aimedrelease_outputpointer = value.p_value
        if name == "unavoidablerelease":
            self._unavoidablerelease_outputpointer = value.p_value
        if name == "outflow":
            self._outflow_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._precipitation_outputflag:
            self._precipitation_outputpointer[0] = self.precipitation
        if self._adjustedprecipitation_outputflag:
            self._adjustedprecipitation_outputpointer[0] = self.adjustedprecipitation
        if self._potentialevaporation_outputflag:
            self._potentialevaporation_outputpointer[0] = self.potentialevaporation
        if self._adjustedevaporation_outputflag:
            self._adjustedevaporation_outputpointer[0] = self.adjustedevaporation
        if self._actualevaporation_outputflag:
            self._actualevaporation_outputpointer[0] = self.actualevaporation
        if self._inflow_outputflag:
            self._inflow_outputpointer[0] = self.inflow
        if self._saferelease_outputflag:
            self._saferelease_outputpointer[0] = self.saferelease
        if self._aimedrelease_outputflag:
            self._aimedrelease_outputpointer[0] = self.aimedrelease
        if self._unavoidablerelease_outputflag:
            self._unavoidablerelease_outputpointer[0] = self.unavoidablerelease
        if self._outflow_outputflag:
            self._outflow_outputpointer[0] = self.outflow
@cython.final
cdef class StateSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._watervolume_diskflag_reading:
            self.watervolume = self._watervolume_ncarray[0]
        elif self._watervolume_ramflag:
            self.watervolume = self._watervolume_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._watervolume_diskflag_writing:
            self._watervolume_ncarray[0] = self.watervolume
        if self._watervolume_ramflag:
            self._watervolume_array[idx] = self.watervolume
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "watervolume":
            self._watervolume_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._watervolume_outputflag:
            self._watervolume_outputpointer[0] = self.watervolume
@cython.final
cdef class LogSequences:
    pass
@cython.final
cdef class AideSequences:
    pass
@cython.final
cdef class OutletSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._q_diskflag_reading:
            self.q = self._q_ncarray[0]
        elif self._q_ramflag:
            self.q = self._q_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._q_diskflag_writing:
            self._q_ncarray[0] = self.q
        if self._q_ramflag:
            self._q_array[idx] = self.q
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "q":
            self._q_pointer = pointer.p_value
    cpdef get_pointervalue(self, str name):
        cdef numpy.int64_t idx
        if name == "q":
            return self._q_pointer[0]
    cpdef set_value(self, str name, value):
        if name == "q":
            self._q_pointer[0] = value
@cython.final
cdef class PegasusWaterVolume(rootutils.PegasusBase):
    def __init__(self, Model model):
        self.model = model
    cpdef double apply_method0(self, double x)  noexcept nogil:
        return self.model.return_waterlevelerror_v1(x)
@cython.final
cdef class Model(masterinterface.MasterInterface):
    def __init__(self):
        super().__init__()
        self.pemodel = None
        self.pemodel_is_mainmodel = False
        self.precipmodel = None
        self.precipmodel_is_mainmodel = False
        self.safereleasemodels = interfaceutils.SubmodelsProperty()
        self.pegasuswatervolume = PegasusWaterVolume(self)
    def get_pemodel(self) -> masterinterface.MasterInterface | None:
        return self.pemodel
    def set_pemodel(self, pemodel: masterinterface.MasterInterface | None) -> None:
        self.pemodel = pemodel
    def get_precipmodel(self) -> masterinterface.MasterInterface | None:
        return self.precipmodel
    def set_precipmodel(self, precipmodel: masterinterface.MasterInterface | None) -> None:
        self.precipmodel = precipmodel
    cpdef inline void simulate(self, numpy.int64_t idx)  noexcept nogil:
        self.idx_sim = idx
        self.reset_reuseflags()
        self.load_data(idx)
        self.update_inlets()
        self.update_observers()
        self.run()
        self.new2old()
        self.update_outlets()
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
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.reset_reuseflags()
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.reset_reuseflags()
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).reset_reuseflags()
    cpdef void load_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.inlets.load_data(idx)
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.load_data(idx)
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.load_data(idx)
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).load_data(idx)
    cpdef void save_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.inlets.save_data(idx)
        self.sequences.factors.save_data(idx)
        self.sequences.fluxes.save_data(idx)
        self.sequences.states.save_data(idx)
        self.sequences.outlets.save_data(idx)
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.save_data(idx)
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.save_data(idx)
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).save_data(idx)
    cpdef void new2old(self) noexcept nogil:
        self.sequences.old_states.watervolume = self.sequences.new_states.watervolume
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.new2old()
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.new2old()
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).new2old()
    cpdef inline void run(self) noexcept nogil:
        self.calc_precipitation_v1()
        self.calc_adjustedprecipitation_v1()
        self.calc_potentialevaporation_v1()
        self.calc_adjustedevaporation_v1()
        self.calc_allowedwaterlevel_v1()
        self.calc_alloweddischarge_v3()
        self.update_watervolume_v5()
        self.calc_actualevaporation_watervolume_v1()
        self.calc_saferelease_v1()
        self.calc_aimedrelease_watervolume_v1()
        self.calc_unavoidablerelease_watervolume_v1()
        self.calc_waterlevel_v1()
        self.calc_outflow_v6()
    cpdef void update_inlets(self) noexcept nogil:
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.update_inlets()
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.update_inlets()
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).update_inlets()
        cdef numpy.int64_t i
        if not self.threading:
            for i in range(self.sequences.inlets._q_length_0):
                if self.sequences.inlets._q_ready[i]:
                    self.sequences.inlets.q[i] = self.sequences.inlets._q_pointer[i][0]
                else:
                    self.sequences.inlets.q[i] = nan
        self.pick_inflow_v1()
    cpdef void update_outlets(self) noexcept nogil:
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.update_outlets()
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.update_outlets()
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).update_outlets()
        self.pass_outflow_v1()
        cdef numpy.int64_t i
        if not self.threading:
            self.sequences.outlets._q_pointer[0] = self.sequences.outlets._q_pointer[0] + self.sequences.outlets.q
    cpdef void update_observers(self) noexcept nogil:
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.update_observers()
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.update_observers()
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).update_observers()
        cdef numpy.int64_t i
    cpdef void update_receivers(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.update_receivers(idx)
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.update_receivers(idx)
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).update_receivers(idx)
        cdef numpy.int64_t i
    cpdef void update_senders(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.update_senders(idx)
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.update_senders(idx)
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).update_senders(idx)
        cdef numpy.int64_t i
    cpdef void update_outputs(self) noexcept nogil:
        if not self.threading:
            self.sequences.factors.update_outputs()
            self.sequences.fluxes.update_outputs()
            self.sequences.states.update_outputs()
        cdef numpy.int64_t i_submodel
        if (self.pemodel is not None) and not self.pemodel_is_mainmodel:
            self.pemodel.update_outputs()
        if (self.precipmodel is not None) and not self.precipmodel_is_mainmodel:
            self.precipmodel.update_outputs()
        for i_submodel in range(self.safereleasemodels.number):
            if self.safereleasemodels.typeids[i_submodel] > 0:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i_submodel]).update_outputs()
    cpdef inline void pick_inflow_v1(self) noexcept nogil:
        cdef numpy.int64_t idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx])
    cpdef inline void calc_precipitation_v1(self) noexcept nogil:
        if self.precipmodel is None:
            self.sequences.fluxes.precipitation = 0.0
        elif self.precipmodel_typeid == 2:
            (<masterinterface.MasterInterface>self.precipmodel).determine_precipitation()
            self.sequences.fluxes.precipitation = (<masterinterface.MasterInterface>self.precipmodel).get_precipitation(0)
    cpdef inline void calc_adjustedprecipitation_v1(self) noexcept nogil:
        self.sequences.fluxes.adjustedprecipitation = (            self.parameters.derived.inputfactor * self.parameters.control.correctionprecipitation * self.sequences.fluxes.precipitation        )
    cpdef inline void calc_potentialevaporation_v1(self) noexcept nogil:
        if self.pemodel is None:
            self.sequences.fluxes.potentialevaporation = 0.0
        elif self.pemodel_typeid == 1:
            (<masterinterface.MasterInterface>self.pemodel).determine_potentialevapotranspiration()
            self.sequences.fluxes.potentialevaporation = (<masterinterface.MasterInterface>self.pemodel).get_potentialevapotranspiration(0)
    cpdef inline void calc_adjustedevaporation_v1(self) noexcept nogil:
        cdef double d_old
        cdef double d_new
        cdef double d_weight
        d_weight = self.parameters.control.weightevaporation
        d_new = self.parameters.derived.inputfactor * self.parameters.control.correctionevaporation * self.sequences.fluxes.potentialevaporation
        d_old = self.sequences.logs.loggedadjustedevaporation[0]
        self.sequences.fluxes.adjustedevaporation = d_weight * d_new + (1.0 - d_weight) * d_old
        self.sequences.logs.loggedadjustedevaporation[0] = self.sequences.fluxes.adjustedevaporation
    cpdef inline void calc_allowedwaterlevel_v1(self) noexcept nogil:
        cdef double w
        if isinf(self.parameters.control.allowedwaterleveldrop):
            self.sequences.aides.allowedwaterlevel = -inf
        else:
            self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.states.watervolume
            self.parameters.control.watervolume2waterlevel.calculate_values()
            w = self.parameters.control.watervolume2waterlevel.outputs[0]
            self.sequences.aides.allowedwaterlevel = w - self.parameters.control.allowedwaterleveldrop
    cpdef inline void calc_alloweddischarge_v3(self) noexcept nogil:
        cdef double v_max
        cdef double v_min
        if isinf(self.sequences.aides.allowedwaterlevel):
            self.sequences.aides.alloweddischarge = inf
        else:
            v_min = self.pegasuswatervolume.find_x(                0.0, self.sequences.states.watervolume, 0.0, self.sequences.states.watervolume, 1e-10, 1e-10, 1000            )
            v_max = self.sequences.states.watervolume + self.parameters.derived.seconds / 1e6 * (                self.sequences.fluxes.inflow + self.sequences.fluxes.adjustedprecipitation - self.sequences.fluxes.adjustedevaporation            )
            self.sequences.aides.alloweddischarge = max(1e6 / self.parameters.derived.seconds * (v_max - v_min), 0.0)
    cpdef inline void update_watervolume_v5(self) noexcept nogil:
        self.sequences.states.watervolume = self.sequences.states.watervolume + (self.parameters.derived.seconds / 1e6 * (self.sequences.fluxes.inflow + self.sequences.fluxes.adjustedprecipitation))
    cpdef inline void calc_actualevaporation_watervolume_v1(self) noexcept nogil:
        cdef double v
        v = self.parameters.derived.seconds / 1e6 * self.sequences.fluxes.adjustedevaporation
        if v < self.sequences.states.watervolume:
            self.sequences.fluxes.actualevaporation = self.sequences.fluxes.adjustedevaporation
            self.sequences.states.watervolume = self.sequences.states.watervolume - (v)
        else:
            self.sequences.fluxes.actualevaporation = 1e6 / self.parameters.derived.seconds * self.sequences.states.watervolume
            self.sequences.states.watervolume = 0.0
    cpdef inline void calc_saferelease_v1(self) noexcept nogil:
        cdef double q
        cdef numpy.int64_t i
        self.sequences.fluxes.saferelease = self.parameters.control.allowedrelease[self.parameters.derived.toy[self.idx_sim]]
        for i in range(self.parameters.control.nmbsafereleasemodels):
            if self.safereleasemodels.typeids[i] == 1:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i]).determine_y()
                q = (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i]).get_y()
                self.sequences.fluxes.saferelease = min(q, self.sequences.fluxes.saferelease)
    cpdef inline void calc_aimedrelease_watervolume_v1(self) noexcept nogil:
        cdef double v
        cdef double q
        cdef double targetvolume
        targetvolume = self.parameters.control.targetvolume[self.parameters.derived.toy[self.idx_sim]]
        q = 1e6 / self.parameters.derived.seconds * (self.sequences.states.watervolume - targetvolume)
        q = min(max(q, self.parameters.control.minimumrelease), self.sequences.fluxes.saferelease, self.sequences.aides.alloweddischarge)
        v = self.parameters.derived.seconds / 1e6 * q
        if v < self.sequences.states.watervolume:
            self.sequences.fluxes.aimedrelease = q
            self.sequences.states.watervolume = self.sequences.states.watervolume - (v)
        else:
            self.sequences.fluxes.aimedrelease = 1e6 / self.parameters.derived.seconds * self.sequences.states.watervolume
            self.sequences.states.watervolume = 0.0
    cpdef inline void calc_unavoidablerelease_watervolume_v1(self) noexcept nogil:
        if self.sequences.states.watervolume < self.parameters.control.maximumvolume:
            self.sequences.fluxes.unavoidablerelease = 0.0
        else:
            self.sequences.fluxes.unavoidablerelease = (                1e6 / self.parameters.derived.seconds * (self.sequences.states.watervolume - self.parameters.control.maximumvolume)            )
            self.sequences.states.watervolume = self.parameters.control.maximumvolume
    cpdef inline void calc_waterlevel_v1(self) noexcept nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.sequences.factors.waterlevel = self.parameters.control.watervolume2waterlevel.outputs[0]
    cpdef inline void calc_outflow_v6(self) noexcept nogil:
        self.sequences.fluxes.outflow = self.sequences.fluxes.aimedrelease + self.sequences.fluxes.unavoidablerelease
    cpdef inline double return_waterlevelerror_v1(self, double watervolume) noexcept nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        return self.parameters.control.watervolume2waterlevel.outputs[0] - self.sequences.aides.allowedwaterlevel
    cpdef inline void pass_outflow_v1(self) noexcept nogil:
        self.sequences.outlets.q = self.sequences.fluxes.outflow
    cpdef inline void pick_inflow(self) noexcept nogil:
        cdef numpy.int64_t idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx])
    cpdef inline void calc_precipitation(self) noexcept nogil:
        if self.precipmodel is None:
            self.sequences.fluxes.precipitation = 0.0
        elif self.precipmodel_typeid == 2:
            (<masterinterface.MasterInterface>self.precipmodel).determine_precipitation()
            self.sequences.fluxes.precipitation = (<masterinterface.MasterInterface>self.precipmodel).get_precipitation(0)
    cpdef inline void calc_adjustedprecipitation(self) noexcept nogil:
        self.sequences.fluxes.adjustedprecipitation = (            self.parameters.derived.inputfactor * self.parameters.control.correctionprecipitation * self.sequences.fluxes.precipitation        )
    cpdef inline void calc_potentialevaporation(self) noexcept nogil:
        if self.pemodel is None:
            self.sequences.fluxes.potentialevaporation = 0.0
        elif self.pemodel_typeid == 1:
            (<masterinterface.MasterInterface>self.pemodel).determine_potentialevapotranspiration()
            self.sequences.fluxes.potentialevaporation = (<masterinterface.MasterInterface>self.pemodel).get_potentialevapotranspiration(0)
    cpdef inline void calc_adjustedevaporation(self) noexcept nogil:
        cdef double d_old
        cdef double d_new
        cdef double d_weight
        d_weight = self.parameters.control.weightevaporation
        d_new = self.parameters.derived.inputfactor * self.parameters.control.correctionevaporation * self.sequences.fluxes.potentialevaporation
        d_old = self.sequences.logs.loggedadjustedevaporation[0]
        self.sequences.fluxes.adjustedevaporation = d_weight * d_new + (1.0 - d_weight) * d_old
        self.sequences.logs.loggedadjustedevaporation[0] = self.sequences.fluxes.adjustedevaporation
    cpdef inline void calc_allowedwaterlevel(self) noexcept nogil:
        cdef double w
        if isinf(self.parameters.control.allowedwaterleveldrop):
            self.sequences.aides.allowedwaterlevel = -inf
        else:
            self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.states.watervolume
            self.parameters.control.watervolume2waterlevel.calculate_values()
            w = self.parameters.control.watervolume2waterlevel.outputs[0]
            self.sequences.aides.allowedwaterlevel = w - self.parameters.control.allowedwaterleveldrop
    cpdef inline void calc_alloweddischarge(self) noexcept nogil:
        cdef double v_max
        cdef double v_min
        if isinf(self.sequences.aides.allowedwaterlevel):
            self.sequences.aides.alloweddischarge = inf
        else:
            v_min = self.pegasuswatervolume.find_x(                0.0, self.sequences.states.watervolume, 0.0, self.sequences.states.watervolume, 1e-10, 1e-10, 1000            )
            v_max = self.sequences.states.watervolume + self.parameters.derived.seconds / 1e6 * (                self.sequences.fluxes.inflow + self.sequences.fluxes.adjustedprecipitation - self.sequences.fluxes.adjustedevaporation            )
            self.sequences.aides.alloweddischarge = max(1e6 / self.parameters.derived.seconds * (v_max - v_min), 0.0)
    cpdef inline void update_watervolume(self) noexcept nogil:
        self.sequences.states.watervolume = self.sequences.states.watervolume + (self.parameters.derived.seconds / 1e6 * (self.sequences.fluxes.inflow + self.sequences.fluxes.adjustedprecipitation))
    cpdef inline void calc_actualevaporation_watervolume(self) noexcept nogil:
        cdef double v
        v = self.parameters.derived.seconds / 1e6 * self.sequences.fluxes.adjustedevaporation
        if v < self.sequences.states.watervolume:
            self.sequences.fluxes.actualevaporation = self.sequences.fluxes.adjustedevaporation
            self.sequences.states.watervolume = self.sequences.states.watervolume - (v)
        else:
            self.sequences.fluxes.actualevaporation = 1e6 / self.parameters.derived.seconds * self.sequences.states.watervolume
            self.sequences.states.watervolume = 0.0
    cpdef inline void calc_saferelease(self) noexcept nogil:
        cdef double q
        cdef numpy.int64_t i
        self.sequences.fluxes.saferelease = self.parameters.control.allowedrelease[self.parameters.derived.toy[self.idx_sim]]
        for i in range(self.parameters.control.nmbsafereleasemodels):
            if self.safereleasemodels.typeids[i] == 1:
                (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i]).determine_y()
                q = (<masterinterface.MasterInterface>self.safereleasemodels.submodels[i]).get_y()
                self.sequences.fluxes.saferelease = min(q, self.sequences.fluxes.saferelease)
    cpdef inline void calc_aimedrelease_watervolume(self) noexcept nogil:
        cdef double v
        cdef double q
        cdef double targetvolume
        targetvolume = self.parameters.control.targetvolume[self.parameters.derived.toy[self.idx_sim]]
        q = 1e6 / self.parameters.derived.seconds * (self.sequences.states.watervolume - targetvolume)
        q = min(max(q, self.parameters.control.minimumrelease), self.sequences.fluxes.saferelease, self.sequences.aides.alloweddischarge)
        v = self.parameters.derived.seconds / 1e6 * q
        if v < self.sequences.states.watervolume:
            self.sequences.fluxes.aimedrelease = q
            self.sequences.states.watervolume = self.sequences.states.watervolume - (v)
        else:
            self.sequences.fluxes.aimedrelease = 1e6 / self.parameters.derived.seconds * self.sequences.states.watervolume
            self.sequences.states.watervolume = 0.0
    cpdef inline void calc_unavoidablerelease_watervolume(self) noexcept nogil:
        if self.sequences.states.watervolume < self.parameters.control.maximumvolume:
            self.sequences.fluxes.unavoidablerelease = 0.0
        else:
            self.sequences.fluxes.unavoidablerelease = (                1e6 / self.parameters.derived.seconds * (self.sequences.states.watervolume - self.parameters.control.maximumvolume)            )
            self.sequences.states.watervolume = self.parameters.control.maximumvolume
    cpdef inline void calc_waterlevel(self) noexcept nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.sequences.factors.waterlevel = self.parameters.control.watervolume2waterlevel.outputs[0]
    cpdef inline void calc_outflow(self) noexcept nogil:
        self.sequences.fluxes.outflow = self.sequences.fluxes.aimedrelease + self.sequences.fluxes.unavoidablerelease
    cpdef inline double return_waterlevelerror(self, double watervolume) noexcept nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        return self.parameters.control.watervolume2waterlevel.outputs[0] - self.sequences.aides.allowedwaterlevel
    cpdef inline void pass_outflow(self) noexcept nogil:
        self.sequences.outlets.q = self.sequences.fluxes.outflow
