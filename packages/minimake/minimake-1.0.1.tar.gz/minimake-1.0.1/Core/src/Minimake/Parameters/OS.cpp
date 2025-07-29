#include "pch.h"
#include "Os.h"

namespace Minimake
{
	std::string to_string(const OS& os)
	{
		switch (os)
		{
		case OS::Windows:
			return "Windows";

		case OS::MacOS:
			return "MacOS";

		case OS::Linux:
			return "Linux";

		default:
			return "Unknown";
		}
	}
	std::ostream& operator<<(std::ostream& stream, OS os)
	{
		stream << to_string(os);
		return stream;
	}
}