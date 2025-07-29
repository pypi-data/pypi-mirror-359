#pragma once

namespace Minimake
{
	enum class Platform : long
	{
		Unknown = -1,
		x86 = 0,
		x64 = 1,
	};

	std::string to_string(const Platform& platform);
	std::ostream& operator<<(std::ostream& stream, const Platform& platform);
}

