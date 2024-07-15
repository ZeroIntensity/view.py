cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

# Source code
file(GLOB _view_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/_view/*.c
)
MESSAGE(DEBUG ${_view_SRC})

# Find Python
find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

# Link Python
python_add_library(_view MODULE ${_view_SRC} WITH_SOABI)

# Compiler settings
target_include_directories(_view PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include/)
target_compile_options(_view PUBLIC -g3)

MESSAGE(STATUS "Everything looks good, let's install!")
# Install extension module
install(TARGETS _view DESTINATION .)
