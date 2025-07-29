#pragma once

#include "Minimake/Projects/Project.h"

#include "Minimake/MSBuild/MSBuildEmitter.h"

namespace Minimake
{
	class CppProject : public Project
	{
	protected:
		virtual std::string get_extension() const override;

	public:
		virtual void generate(const std::string& output_dir, int indent_level = 0, const std::string& indent = "\t", bool pretty = true) const override;
	};
}