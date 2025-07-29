#include "pch.h"
#include "MSBuildParameter.h"

namespace Minimake
{
	std::string MSBuildParameter::get_key() const
	{
		return key;
	}

	std::string MSBuildParameter::get_value() const
	{
		return value;
	}
}