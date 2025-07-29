cmake_minimum_required(VERSION 3.4...3.18)
project(minimake)

set(CMAKE_CXX_STANDARD 17)

add_subdirectory(vendor/pybind11)

file(GLOB_RECURSE PROJECT_SOURCES
    "Core/src/*.cpp"
)
list(REMOVE_ITEM PROJECT_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/Core/src/bindings.cpp")

add_library(minimake_lib STATIC ${PROJECT_SOURCES})
target_include_directories(minimake_lib PUBLIC Core/src/)

pybind11_add_module(minimake Core/src/bindings.cpp)
target_link_libraries(minimake PRIVATE minimake_lib)

target_include_directories(minimake PRIVATE Core/src/)