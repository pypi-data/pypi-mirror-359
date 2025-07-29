#include "pch.h"
#include "MSBuildEmitter.h"

namespace Minimake
{
	void MSBuildEmitter::start_line()
	{
		if (pretty)
		{
			for (int i = 0; i < indent_level; i++)
			{
				out << indent;
			}
		}
	}

	void MSBuildEmitter::end_line()
	{
		if (pretty)
		{
			out << std::endl;
		}
	}

	void MSBuildEmitter::increase_indent()
	{
		indent_level++;
	}

	void MSBuildEmitter::decrease_indent()
	{
		if (indent_level > 0)
		{
			indent_level--;
		}
	}

	void MSBuildEmitter::push_element(const std::string& name)
	{
		open_elements.push(name);
	}

	std::string MSBuildEmitter::pop_element()
	{
		if (!open_elements.empty())
		{
			std::string name = open_elements.top();
			open_elements.pop();
			return name;
		}
		return std::string();
	}

	std::ostream& MSBuildEmitter::stream()
	{
		return out;
	}
}
