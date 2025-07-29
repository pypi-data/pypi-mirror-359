#pragma once

namespace Minimake
{
	enum class Configuration : long
	{
		Unknown = -1,
		Debug = 0,
		Release = 1,
	};

	std::string to_string(const Configuration& configuration);
	std::ostream& operator<<(std::ostream& stream, const Configuration& configuration);
}