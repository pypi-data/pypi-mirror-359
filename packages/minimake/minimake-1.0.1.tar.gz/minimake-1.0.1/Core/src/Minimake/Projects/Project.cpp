#include "pch.h"
#include "Project.h"

namespace Minimake
{
    std::ofstream Project::open_file(const std::string& output_dir, bool&& is_valid) const
    {
        if (!has_valid_extension())
        {
            std::cerr << "The given project has no valid extension for the given configuration" << std::endl;
            is_valid = false;
            return std::ofstream();
        }

        namespace fs = std::filesystem;
        fs::create_directories(output_dir);

        std::string file_name = name + get_extension();
        std::string file_path = output_dir + '/' + file_name;

        std::ofstream file(file_path);

        if (!file)
        {
            std::cerr << "Failed to create file: " << file_path << std::endl;
            is_valid = false;
            return std::ofstream();
        }

        is_valid = true;
        return file;
    }

    std::string Project::get_name() const
    {
        return name;
    }

    Configuration Project::get_configuration() const
    {
        return configuration;
    }

    Platform Project::get_platform() const
    {
        return platform;
    }

    Ide Project::get_ide() const
    {
        return ide;
    }

    OS Project::get_os() const
    {
        return os;
    }
}