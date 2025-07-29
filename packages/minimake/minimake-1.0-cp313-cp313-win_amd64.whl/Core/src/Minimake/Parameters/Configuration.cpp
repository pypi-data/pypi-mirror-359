#include "pch.h"
#include "Configuration.h"

namespace Minimake
{
	std::string to_string(const Configuration& configuration)
	{
		switch (configuration)
		{
		case Configuration::Debug:
			return "Win32";

		case Configuration::Release:
			return "Release";

		default:
			return "Unknown";
		}
	}

	std::ostream& operator<<(std::ostream& stream, const Configuration& configuration)
	{
		stream << to_string(configuration);
		return stream;
	}
}