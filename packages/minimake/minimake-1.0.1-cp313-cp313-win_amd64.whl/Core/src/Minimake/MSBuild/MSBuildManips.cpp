#include "pch.h"
#include "MSBuildManips.h"

#include "Minimake/MSBuild/MSBuildEmitter.h"

namespace Minimake
{
	std::string MSBuildManip::escape(const std::string& input)
	{
		std::ostringstream out;
		for (char c : input)
		{
			switch (c)
			{
			case '&':
				out << "&amp";
				break;

			case '<':
				out << "&lt";
				break;

			case '>':
				out << "&gt";
				break;

			case '"':
				out << "&quot";
				break;

			case '\'':
				out << "&apos";
				break;

			default:
				out << c;
				break;
			}
		}
		return out.str();
	}

	MSBuildManip::~MSBuildManip() = default;

	MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildHead& head)
	{
		emitter.start_line();
		emitter.stream() << "<?xml version=\"" << head.xml_version << "\" encoding=\"" << head.encoding << "\"?>";
		emitter.end_line();
		return emitter;
	}

	MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildElement& element)
	{
		emitter.start_line();
		emitter.stream() << '<' << element.name;

		for (const MSBuildParameter& parameter : element.parameters)
		{
			emitter.stream() << ' ' << parameter.get_key() << '=\"' << MSBuildManip::escape(parameter.get_value()) << '"';
		}

		if (element.self_closing)
		{
			emitter.stream() << " />";
			emitter.end_line();
		}
		else
		{
			emitter.stream() << '>';
			emitter.end_line();
			emitter.push_element(element.name);
			emitter.increase_indent();
		}

		return emitter;
	}

	MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildValue& value)
	{
		emitter.start_line();
		emitter.stream() << '<' << value.key << '>' << MSBuildManip::escape(value.value) << "/<" << value.key << ">";
		emitter.end_line();
		return emitter;
	}

	std::string MSBuildEnd::get_name(MSBuildEmitter& emitter) const
	{
		if (name_override.empty())
		{
			return emitter.pop_element();
		}
		else
		{
			return name_override;
		}
	}

	MSBuildEmitter& operator<<(MSBuildEmitter& emitter, const MSBuildEnd& end)
	{
		emitter.decrease_indent();
		std::string name = end.get_name(emitter);
		emitter.start_line();
		emitter.stream() << "</" << name << '>';
		emitter.end_line();
		return emitter;
	}

	bool MSBuildElement::is_self_closing() const
	{
		return self_closing;
	}

	MSBuildElement& MSBuildElement::set_self_closing(bool value)
	{
		self_closing = value;
		return *this;
	}
}
