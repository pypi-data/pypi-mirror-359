#pragma once

namespace Minimake
{
	enum class OS : long
	{
		Unknown = -1,
		Windows = 0,
		MacOS = 1,
		Linux = 2,
	};

	std::string to_string(const OS& os);
	std::ostream& operator<<(std::ostream& stream, OS os);
}

