#pragma once

#include "Minimake/Parameters/Configuration.h"
#include "Minimake/Parameters/Platform.h"
#include "Minimake/Parameters/Ide.h"
#include "Minimake/Parameters/OS.h"

namespace Minimake
{
	class Project
	{
	protected:
		std::string name;

		Configuration configuration;
		Platform platform;
		Ide ide;
		OS os;

		std::ofstream open_file(const std::string& output_dir, bool&& is_valid) const;

		virtual std::string get_extension() const = 0;
		bool has_valid_extension() const;

	public:
		Project(
			const std::string& name,
			Configuration configuration,
			Platform platform,
			Ide ide,
			OS os
		) :
			name(name),
			configuration(configuration),
			platform(platform),
			ide(ide),
			os(os)
		{ }

		virtual ~Project() = default;

		virtual void generate(const std::string& output_dir, int indent_level = 0, const std::string& indent = "\t", bool pretty = true) const = 0;

		std::string get_name() const;

		Configuration get_configuration() const;
		Platform get_platform() const;
		Ide get_ide() const;
		OS get_os() const;
	};
}
