#include "pch.h"
#include "Minimake.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace Minimake;

using ConfigurationToString = std::string(*)(const Configuration&);
using PlatformToString = std::string(*)(const Platform&);
using OSToString = std::string(*)(const OS&);
using IdeToString = std::string(*)(const Ide&);

PYBIND11_MODULE(minimake, m)
{
	m.doc() = "Multi Platform Project/Solution Builder";
	m.attr("__version__") = "1.0.1";

	m.def("to_string", (ConfigurationToString)&to_string);
	py::enum_<Configuration>(m, "Configuration")
		.value("Unknown", Configuration::Unknown)
		.value("Debug", Configuration::Debug)
		.value("Release", Configuration::Release)
		.export_values();

	m.def("to_string", (PlatformToString)&to_string);
	py::enum_<Platform>(m, "Platform")
		.value("Unknown", Platform::Unknown)
		.value("x86", Platform::x86)
		.value("x64", Platform::x64)
		.export_values();

	m.def("to_string", (OSToString)&to_string);
	py::enum_<OS>(m, "OperatingSystem")
		.value("Unknown", OS::Unknown)
		.value("Windows", OS::Windows)
		.value("MacOS", OS::MacOS)
		.value("Linux", OS::Linux)
		.export_values();

	m.def("to_string", (IdeToString)&to_string);
	py::enum_<Ide>(m, "Ide")
		.value("Unknown", Ide::Unknown)
		.value("VisualStudio", Ide::VisualStudio)
		.export_values();

	py::class_<Project>(m, "Project")
		.def("generate", &Project::generate)
		.def("get_name", &Project::get_name)
		.def("get_configuration", &Project::get_configuration)
		.def("get_platform", &Project::get_platform)
		.def("get_ide", &Project::get_ide)
		.def("get_os", &Project::get_os);
}