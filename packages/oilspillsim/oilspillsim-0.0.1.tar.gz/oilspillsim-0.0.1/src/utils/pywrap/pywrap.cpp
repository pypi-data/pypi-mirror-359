// pywrap.cpp
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h> 
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include "basic_simulator.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;
constexpr auto byref = py::return_value_policy::reference_internal;

PYBIND11_MODULE(oilspillsim, m) {
    m.doc() = "optional module docstring";
    py::class_<SIMULATOR>(m, "oilspillsim")
    .def(py::init<const std::string &, const double, const double, const double, const double, const double, const int, const int, const int, const int, bool>(),py::arg("_filepath"), py::arg("_dt") = 10., py::arg("_kw") = 0.5, py::arg("_kc") = 1., py::arg("_gamma") = 1., py::arg("_flow") = 50., py::arg("_number_of_sources") = int(3), py::arg("_max_contamination_value") = int(5), py::arg("_source_fuel") = int(1000),  py::arg("_random_seed") = int(-1),  py::arg("_triangular") = false)  
    .def(py::init<Eigen::MatrixXi &, const double, const double, const double, const double, const double, const int, const int, const int, const int, bool>(),py::arg("base_matrix"), py::arg("_dt") = 10., py::arg("_kw") = 0.5, py::arg("_kc") = 1., py::arg("_gamma") = 1., py::arg("_flow") = 50., py::arg("_number_of_sources") = int(3), py::arg("_max_contamination_value") = int(5), py::arg("_source_fuel") = int(1000),  py::arg("_random_seed") = int(-1),  py::arg("_triangular") = false)  
    .def("step", &SIMULATOR::step, py::call_guard<py::gil_scoped_release>())
    .def("reset", &SIMULATOR::reset, py::arg("_seed") = int(-1), py::call_guard<py::gil_scoped_release>())
    .def("get_normalized_density", &SIMULATOR::get_normalized_density, py::arg("gaussian") = true, py::call_guard<py::gil_scoped_release>())
    .def_readonly("source_points", &SIMULATOR::source_points, byref)
    .def_readonly("contamination_position", &SIMULATOR::contamination_position, byref)
    .def_readonly("density", &SIMULATOR::density, byref)
    .def_readonly("x", &SIMULATOR::x, byref)
    .def_readonly("y", &SIMULATOR::y, byref)
    .def_readonly("u", &SIMULATOR::u, byref)
    .def_readonly("v", &SIMULATOR::v, byref)
    .def_readonly("wind_speed", &SIMULATOR::wind_speed, byref)
    ;
#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}