#pragma once

namespace Minimake
{
	class MSBuildEmitter;
}

#include "Minimake/MSBuild/MSBuildParameter.h"

namespace Minimake
{
	class MSBuildManip
	{
	protected:
		static std::string escape(const std::string& input);

	public:
		MSBuildManip() = default;
		virtual ~MSBuildManip() = 0;
	};

	class MSBuildHead : public MSBuildManip
	{
	private:
		std::string xml_version;
		std::string encoding;

	public:
		MSBuildHead(const std::string xml_version = "1.0", const std::string encoding = "utf-8")
			: xml_version(xml_version), encoding(encoding) { }
		~MSBuildHead() override = default;

		friend MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildHead& head);
	};

	class MSBuildElement : public MSBuildManip
	{
	protected:
		std::string name;
		std::vector<MSBuildParameter> parameters;
		bool self_closing;

	public:
		MSBuildElement(const std::string& name, std::initializer_list<MSBuildParameter> parameters = {}, bool self_closing = false)
			: name(name), parameters(parameters), self_closing(self_closing) { }
		virtual ~MSBuildElement() override = default;

		bool is_self_closing() const;
		MSBuildElement& set_self_closing(bool value);

		friend MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildElement& element);
	};

	class MSBuildValue : public MSBuildManip
	{
	protected:
		std::string key;
		std::string value;

	public:
		MSBuildValue(const std::string& key, const std::string& value)
			: key(key), value(value) { }
		virtual ~MSBuildValue() override = default;

		friend MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildValue& value);
	};

	class MSBuildEnd : public MSBuildManip
	{
	private:
		std::string name_override;
		std::string get_name(MSBuildEmitter& emitter) const;

	public:
		MSBuildEnd() = default;
		MSBuildEnd(const std::string& name)
			: name_override(name) { }
		~MSBuildEnd() override = default;

		friend MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildEnd& end);
	};
}

