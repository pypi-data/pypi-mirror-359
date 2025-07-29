#include "pch.h"
#include "CppProject.h"

namespace Minimake
{
	std::string CppProject::get_extension() const
	{
		switch (ide)
		{
		case Ide::VisualStudio:
			return ".vcxproj";
		}
		return std::string();
	}

	bool Project::has_valid_extension() const
	{
		return !get_extension().empty();
	}

	void CppProject::generate(const std::string& output_dir, int indent_level, const std::string& indent, bool pretty) const
	{
		bool file_valid = false;
		std::ofstream file = open_file(output_dir, &file_valid);

		if (file_valid)
		{
			MSBuildEmitter emitter(file, indent_level, indent, pretty);

			emitter << MSBuildHead()
					<< MSBuildElement("Project", { { "DefaultTargets", "Build" }, { "ToolsVersion", "17.0" } })
						<< MSBuildElement("PropertyGroup").set_self_closing(true)
						<< MSBuildElement("ItemGroup")
							<< MSBuildElement("ProjectConfiguration", { { "Include", to_string(configuration) + '|' + to_string(platform) } })
								<< MSBuildValue("Configuration", to_string(configuration))
								<< MSBuildValue("Platform", to_string(platform))
							<< MSBuildEnd()
						<< MSBuildEnd()
					<< MSBuildEnd();

			file.close();
		}
	}
}