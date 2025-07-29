#include "pch.h"
#include "Ide.h"

namespace Minimake
{
	std::string to_string(const Ide& ide)
	{
		switch (ide)
		{
		case (Ide::VisualStudio):
			return "VisualStudio";

		default:
			return "Unknown";
		}
	}

	std::ostream& operator<<(std::ostream& stream, const Ide& ide)
	{
		stream << to_string(ide);
		return stream;
	}
}