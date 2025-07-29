#include "pch.h"
#include "Platform.h"

namespace Minimake
{
	std::string to_string(const Platform& platform)
	{
		switch (platform)
		{
		case Platform::x86:
			return "x86";

		case Platform::x64:
			return "x64";

		default:
			return "Unknown";
		}
	}

	std::ostream& operator<<(std::ostream& stream, const Platform& platform)
	{
		stream << to_string(platform);
		return stream;
	}
}