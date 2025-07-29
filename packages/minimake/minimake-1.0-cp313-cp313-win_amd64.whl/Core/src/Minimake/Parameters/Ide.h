#pragma once

namespace Minimake
{
	enum class Ide : long
	{
		Unknown = -1,
		VisualStudio = 0,
	};

	std::string to_string(const Ide& ide);
	std::ostream& operator<<(std::ostream&, const Ide& ide);
}