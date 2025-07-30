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
        if self._longq_diskflag_reading:
            k = 0
            for jdx0 in range(self._longq_length_0):
                self.longq[jdx0] = self._longq_ncarray[k]
                k += 1
        elif self._longq_ramflag:
            for jdx0 in range(self._longq_length_0):
                self.longq[jdx0] = self._longq_array[idx, jdx0]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t jdx0
        cdef numpy.int64_t k
        if self._longq_diskflag_writing:
            k = 0
            for jdx0 in range(self._longq_length_0):
                self._longq_ncarray[k] = self.longq[jdx0]
                k += 1
        if self._longq_ramflag:
            for jdx0 in range(self._longq_length_0):
                self._longq_array[idx, jdx0] = self.longq[jdx0]
    cpdef inline alloc_pointer(self, name, numpy.int64_t length):
        if name == "longq":
            self._longq_length_0 = length
            self._longq_ready = numpy.full(length, 0, dtype=numpy.int64)
            self._longq_pointer = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc_pointer(self, name):
        if name == "longq":
            PyMem_Free(self._longq_pointer)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, numpy.int64_t idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "longq":
            self._longq_pointer[idx] = pointer.p_value
            self._longq_ready[idx] = 1
    cpdef get_pointervalue(self, str name):
        cdef numpy.int64_t idx
        if name == "longq":
            values = numpy.empty(self.len_longq)
            for idx in range(self.len_longq):
                pointerutils.check0(self._longq_length_0)
                if self._longq_ready[idx] == 0:
                    pointerutils.check1(self._longq_length_0, idx)
                    pointerutils.check2(self._longq_ready, idx)
                values[idx] = self._longq_pointer[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "longq":
            for idx in range(self.len_longq):
                pointerutils.check0(self._longq_length_0)
                if self._longq_ready[idx] == 0:
                    pointerutils.check1(self._longq_length_0, idx)
                    pointerutils.check2(self._longq_ready, idx)
                self._longq_pointer[idx][0] = value[idx]
@cython.final
cdef class FactorSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._maxtimestep_diskflag_reading:
            self.maxtimestep = self._maxtimestep_ncarray[0]
        elif self._maxtimestep_ramflag:
            self.maxtimestep = self._maxtimestep_array[idx]
        if self._timestep_diskflag_reading:
            self.timestep = self._timestep_ncarray[0]
        elif self._timestep_ramflag:
            self.timestep = self._timestep_array[idx]
        if self._waterdepth_diskflag_reading:
            self.waterdepth = self._waterdepth_ncarray[0]
        elif self._waterdepth_ramflag:
            self.waterdepth = self._waterdepth_array[idx]
        if self._waterlevel_diskflag_reading:
            self.waterlevel = self._waterlevel_ncarray[0]
        elif self._waterlevel_ramflag:
            self.waterlevel = self._waterlevel_array[idx]
        if self._waterlevelupstream_diskflag_reading:
            self.waterlevelupstream = self._waterlevelupstream_ncarray[0]
        elif self._waterlevelupstream_ramflag:
            self.waterlevelupstream = self._waterlevelupstream_array[idx]
        if self._wettedarea_diskflag_reading:
            self.wettedarea = self._wettedarea_ncarray[0]
        elif self._wettedarea_ramflag:
            self.wettedarea = self._wettedarea_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._maxtimestep_diskflag_writing:
            self._maxtimestep_ncarray[0] = self.maxtimestep
        if self._maxtimestep_ramflag:
            self._maxtimestep_array[idx] = self.maxtimestep
        if self._timestep_diskflag_writing:
            self._timestep_ncarray[0] = self.timestep
        if self._timestep_ramflag:
            self._timestep_array[idx] = self.timestep
        if self._waterdepth_diskflag_writing:
            self._waterdepth_ncarray[0] = self.waterdepth
        if self._waterdepth_ramflag:
            self._waterdepth_array[idx] = self.waterdepth
        if self._waterlevel_diskflag_writing:
            self._waterlevel_ncarray[0] = self.waterlevel
        if self._waterlevel_ramflag:
            self._waterlevel_array[idx] = self.waterlevel
        if self._waterlevelupstream_diskflag_writing:
            self._waterlevelupstream_ncarray[0] = self.waterlevelupstream
        if self._waterlevelupstream_ramflag:
            self._waterlevelupstream_array[idx] = self.waterlevelupstream
        if self._wettedarea_diskflag_writing:
            self._wettedarea_ncarray[0] = self.wettedarea
        if self._wettedarea_ramflag:
            self._wettedarea_array[idx] = self.wettedarea
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "maxtimestep":
            self._maxtimestep_outputpointer = value.p_value
        if name == "timestep":
            self._timestep_outputpointer = value.p_value
        if name == "waterdepth":
            self._waterdepth_outputpointer = value.p_value
        if name == "waterlevel":
            self._waterlevel_outputpointer = value.p_value
        if name == "waterlevelupstream":
            self._waterlevelupstream_outputpointer = value.p_value
        if name == "wettedarea":
            self._wettedarea_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._maxtimestep_outputflag:
            self._maxtimestep_outputpointer[0] = self.maxtimestep
        if self._timestep_outputflag:
            self._timestep_outputpointer[0] = self.timestep
        if self._waterdepth_outputflag:
            self._waterdepth_outputpointer[0] = self.waterdepth
        if self._waterlevel_outputflag:
            self._waterlevel_outputpointer[0] = self.waterlevel
        if self._waterlevelupstream_outputflag:
            self._waterlevelupstream_outputpointer[0] = self.waterlevelupstream
        if self._wettedarea_outputflag:
            self._wettedarea_outputpointer[0] = self.wettedarea
@cython.final
cdef class FluxSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._outflow_diskflag_reading:
            self.outflow = self._outflow_ncarray[0]
        elif self._outflow_ramflag:
            self.outflow = self._outflow_array[idx]
        if self._dischargevolume_diskflag_reading:
            self.dischargevolume = self._dischargevolume_ncarray[0]
        elif self._dischargevolume_ramflag:
            self.dischargevolume = self._dischargevolume_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._outflow_diskflag_writing:
            self._outflow_ncarray[0] = self.outflow
        if self._outflow_ramflag:
            self._outflow_array[idx] = self.outflow
        if self._dischargevolume_diskflag_writing:
            self._dischargevolume_ncarray[0] = self.dischargevolume
        if self._dischargevolume_ramflag:
            self._dischargevolume_array[idx] = self.dischargevolume
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "outflow":
            self._outflow_outputpointer = value.p_value
        if name == "dischargevolume":
            self._dischargevolume_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._outflow_outputflag:
            self._outflow_outputpointer[0] = self.outflow
        if self._dischargevolume_outputflag:
            self._dischargevolume_outputpointer[0] = self.dischargevolume
@cython.final
cdef class StateSequences:
    cpdef inline void load_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._discharge_diskflag_reading:
            self.discharge = self._discharge_ncarray[0]
        elif self._discharge_ramflag:
            self.discharge = self._discharge_array[idx]
    cpdef inline void save_data(self, numpy.int64_t idx)  noexcept nogil:
        cdef numpy.int64_t k
        if self._discharge_diskflag_writing:
            self._discharge_ncarray[0] = self.discharge
        if self._discharge_ramflag:
            self._discharge_array[idx] = self.discharge
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "discharge":
            self._discharge_outputpointer = value.p_value
    cpdef inline void update_outputs(self) noexcept nogil:
        if self._discharge_outputflag:
            self._discharge_outputpointer[0] = self.discharge
@cython.final
cdef class Model(masterinterface.MasterInterface):
    def __init__(self):
        super().__init__()
        self.crosssection = None
        self.crosssection_is_mainmodel = False
        self.routingmodelsupstream = interfaceutils.SubmodelsProperty()
        self.storagemodelupstream = None
        self.storagemodelupstream_is_mainmodel = False
    def get_crosssection(self) -> masterinterface.MasterInterface | None:
        return self.crosssection
    def set_crosssection(self, crosssection: masterinterface.MasterInterface | None) -> None:
        self.crosssection = crosssection
    def get_storagemodelupstream(self) -> masterinterface.MasterInterface | None:
        return self.storagemodelupstream
    def set_storagemodelupstream(self, storagemodelupstream: masterinterface.MasterInterface | None) -> None:
        self.storagemodelupstream = storagemodelupstream
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
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.reset_reuseflags()
    cpdef void load_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.inlets.load_data(idx)
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.load_data(idx)
    cpdef void save_data(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        self.sequences.inlets.save_data(idx)
        self.sequences.factors.save_data(idx)
        self.sequences.fluxes.save_data(idx)
        self.sequences.states.save_data(idx)
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.save_data(idx)
    cpdef void new2old(self) noexcept nogil:
        self.sequences.old_states.discharge = self.sequences.new_states.discharge
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.new2old()
    cpdef inline void run(self) noexcept nogil:
        pass
    cpdef void update_inlets(self) noexcept nogil:
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.update_inlets()
        cdef numpy.int64_t i
        if not self.threading:
            for i in range(self.sequences.inlets._longq_length_0):
                if self.sequences.inlets._longq_ready[i]:
                    self.sequences.inlets.longq[i] = self.sequences.inlets._longq_pointer[i][0]
                else:
                    self.sequences.inlets.longq[i] = nan
        self.pick_outflow_v1()
    cpdef void update_outlets(self) noexcept nogil:
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.update_outlets()
        self.calc_dischargevolume_v2()
        cdef numpy.int64_t i
    cpdef void update_observers(self) noexcept nogil:
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.update_observers()
        cdef numpy.int64_t i
    cpdef void update_receivers(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.update_receivers(idx)
        cdef numpy.int64_t i
    cpdef void update_senders(self, numpy.int64_t idx) noexcept nogil:
        self.idx_sim = idx
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.update_senders(idx)
        cdef numpy.int64_t i
    cpdef void update_outputs(self) noexcept nogil:
        if not self.threading:
            self.sequences.factors.update_outputs()
            self.sequences.fluxes.update_outputs()
            self.sequences.states.update_outputs()
        if (self.crosssection is not None) and not self.crosssection_is_mainmodel:
            self.crosssection.update_outputs()
    cpdef inline void pick_outflow_v1(self) noexcept nogil:
        cdef numpy.int64_t i
        self.sequences.fluxes.outflow = 0.0
        for i in range(self.sequences.inlets.len_longq):
            self.sequences.fluxes.outflow = self.sequences.fluxes.outflow + (self.sequences.inlets.longq[i])
    cpdef inline void calc_waterlevelupstream_v1(self) noexcept nogil:
        if self.storagemodelupstream_typeid == 1:
            self.sequences.factors.waterlevelupstream = (<masterinterface.MasterInterface>self.storagemodelupstream).get_waterlevel()
    cpdef inline void calc_waterlevel_v3(self) noexcept nogil:
        self.sequences.factors.waterlevel = self.sequences.factors.waterlevelupstream
    cpdef inline void calc_waterdepth_wettedarea_crosssectionmodel_v2(self, masterinterface.MasterInterface submodel) noexcept nogil:
        submodel.use_waterlevel(self.sequences.factors.waterlevel)
        self.sequences.factors.waterdepth = submodel.get_waterdepth()
        self.sequences.factors.wettedarea = submodel.get_wettedarea()
    cpdef inline void calc_waterdepth_wettedarea_v1(self) noexcept nogil:
        if self.crosssection_typeid == 2:
            self.calc_waterdepth_wettedarea_crosssectionmodel_v2(                (<masterinterface.MasterInterface>self.crosssection)            )
    cpdef inline void calc_maxtimestep_v4(self) noexcept nogil:
        cdef double cel
        if (self.sequences.fluxes.outflow != 0.0) and (self.sequences.factors.wettedarea > 0.0):
            cel = fabs(5.0 / 3.0 * self.sequences.fluxes.outflow / self.sequences.factors.wettedarea)
            self.sequences.factors.maxtimestep = self.parameters.control.timestepfactor * 1000.0 * self.parameters.control.lengthupstream / cel
        else:
            self.sequences.factors.maxtimestep = inf
    cpdef inline void calc_dischargevolume_v2(self) noexcept nogil:
        self.sequences.fluxes.dischargevolume = self.parameters.derived.seconds * self.sequences.fluxes.outflow
    cpdef void determine_discharge_v4(self) noexcept nogil:
        self.sequences.states.discharge = self.sequences.fluxes.outflow
    cpdef double get_maxtimestep_v1(self) noexcept nogil:
        return self.sequences.factors.maxtimestep
    cpdef double get_discharge_v1(self) noexcept nogil:
        return self.sequences.states.discharge
    cpdef double get_partialdischargedownstream_v1(self, double clientdischarge) noexcept nogil:
        cdef numpy.int64_t i
        cdef double dischargeupstream
        dischargeupstream = 0.0
        for i in range(self.routingmodelsupstream.number):
            if self.routingmodelsupstream.typeids[i] in (1, 2):
                dischargeupstream = dischargeupstream + (fabs(                    (<masterinterface.MasterInterface>self.routingmodelsupstream.submodels[i]).get_discharge()                ))
        if dischargeupstream == 0.0:
            return 0.0
        return fabs(self.sequences.states.discharge) * clientdischarge / dischargeupstream
    cpdef double get_dischargevolume_v1(self) noexcept nogil:
        return self.sequences.fluxes.dischargevolume
    cpdef void set_timestep_v1(self, double timestep) noexcept nogil:
        self.sequences.factors.timestep = timestep
    cpdef inline void pick_outflow(self) noexcept nogil:
        cdef numpy.int64_t i
        self.sequences.fluxes.outflow = 0.0
        for i in range(self.sequences.inlets.len_longq):
            self.sequences.fluxes.outflow = self.sequences.fluxes.outflow + (self.sequences.inlets.longq[i])
    cpdef inline void calc_waterlevelupstream(self) noexcept nogil:
        if self.storagemodelupstream_typeid == 1:
            self.sequences.factors.waterlevelupstream = (<masterinterface.MasterInterface>self.storagemodelupstream).get_waterlevel()
    cpdef inline void calc_waterlevel(self) noexcept nogil:
        self.sequences.factors.waterlevel = self.sequences.factors.waterlevelupstream
    cpdef inline void calc_waterdepth_wettedarea_crosssectionmodel(self, masterinterface.MasterInterface submodel) noexcept nogil:
        submodel.use_waterlevel(self.sequences.factors.waterlevel)
        self.sequences.factors.waterdepth = submodel.get_waterdepth()
        self.sequences.factors.wettedarea = submodel.get_wettedarea()
    cpdef inline void calc_waterdepth_wettedarea(self) noexcept nogil:
        if self.crosssection_typeid == 2:
            self.calc_waterdepth_wettedarea_crosssectionmodel_v2(                (<masterinterface.MasterInterface>self.crosssection)            )
    cpdef inline void calc_maxtimestep(self) noexcept nogil:
        cdef double cel
        if (self.sequences.fluxes.outflow != 0.0) and (self.sequences.factors.wettedarea > 0.0):
            cel = fabs(5.0 / 3.0 * self.sequences.fluxes.outflow / self.sequences.factors.wettedarea)
            self.sequences.factors.maxtimestep = self.parameters.control.timestepfactor * 1000.0 * self.parameters.control.lengthupstream / cel
        else:
            self.sequences.factors.maxtimestep = inf
    cpdef inline void calc_dischargevolume(self) noexcept nogil:
        self.sequences.fluxes.dischargevolume = self.parameters.derived.seconds * self.sequences.fluxes.outflow
    cpdef void determine_discharge(self) noexcept nogil:
        self.sequences.states.discharge = self.sequences.fluxes.outflow
    cpdef double get_maxtimestep(self) noexcept nogil:
        return self.sequences.factors.maxtimestep
    cpdef double get_discharge(self) noexcept nogil:
        return self.sequences.states.discharge
    cpdef double get_partialdischargedownstream(self, double clientdischarge) noexcept nogil:
        cdef numpy.int64_t i
        cdef double dischargeupstream
        dischargeupstream = 0.0
        for i in range(self.routingmodelsupstream.number):
            if self.routingmodelsupstream.typeids[i] in (1, 2):
                dischargeupstream = dischargeupstream + (fabs(                    (<masterinterface.MasterInterface>self.routingmodelsupstream.submodels[i]).get_discharge()                ))
        if dischargeupstream == 0.0:
            return 0.0
        return fabs(self.sequences.states.discharge) * clientdischarge / dischargeupstream
    cpdef double get_dischargevolume(self) noexcept nogil:
        return self.sequences.fluxes.dischargevolume
    cpdef void set_timestep(self, double timestep) noexcept nogil:
        self.sequences.factors.timestep = timestep
    cpdef void determine_maxtimestep_v4(self) noexcept nogil:
        self.calc_waterlevelupstream_v1()
        self.calc_waterlevel_v3()
        self.calc_waterdepth_wettedarea_v1()
        self.calc_maxtimestep_v4()
    cpdef void determine_maxtimestep(self) noexcept nogil:
        self.calc_waterlevelupstream_v1()
        self.calc_waterlevel_v3()
        self.calc_waterdepth_wettedarea_v1()
        self.calc_maxtimestep_v4()
