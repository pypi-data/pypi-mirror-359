#pragma once

namespace Minimake
{
	class MSBuildParameter
	{
	private:
		std::string key;
		std::string value;

	public:
		MSBuildParameter(const std::string& key, const std::string& value)
			: key(key), value(value) { }

		MSBuildParameter(const std::string& key, const char* value)
			: key(key), value(value) { }

		MSBuildParameter(const std::string& key, int value)
			: key(key), value(std::to_string(value)) { }

		MSBuildParameter(const std::string& key, float value)
			: key(key), value(std::to_string(value)) { }

		MSBuildParameter(const std::string& key, double value)
			: key(key), value(std::to_string(value)) { }

		MSBuildParameter(const std::string& key, bool value)
			: key(key), value(value ? "true" : "false") { }

		std::string get_key() const;
		std::string get_value() const;
	};
}

