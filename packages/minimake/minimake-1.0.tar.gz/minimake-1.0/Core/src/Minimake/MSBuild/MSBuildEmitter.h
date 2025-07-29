#pragma once

#include "Minimake/MSBuild/MSBuildManips.h"

namespace Minimake
{
	class MSBuildEmitter
	{
	private:
		std::ostream& out;

		int indent_level;
		std::stack<std::string> open_elements;

		std::string indent;
		bool pretty;

	public:
		MSBuildEmitter(std::ostream& out, int indent_level = 0, const std::string& indent = "\t", bool pretty = true)
			: out(out), indent_level(indent_level), indent(indent), pretty(pretty) { }
		~MSBuildEmitter() = default;

		void start_line();
		void end_line();

		void increase_indent();
		void decrease_indent();

		void push_element(const std::string& name);
		std::string pop_element();

		std::ostream& stream();
	};
}
