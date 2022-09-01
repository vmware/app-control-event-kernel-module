# SPDX-License-Identifier: GPL-2.0
# Copyright (c) 2021 VMware, Inc. All rights reserved.

from conans import python_requires, CMake, tools, AutoToolsBuildEnvironment
import os
from datetime import datetime

from conan_util.CbConanFile import CbConanFile

class DynSec(CbConanFile):
    name     = "DynSec"
    version  = "PROJECT_VERSION"
    settings = "os", "arch"
    generators = "cmake"
    options = {
        'module_name': ['cb_appc_events']
    }
    default_options = "module_name=cb_appc_events"

    kernelDeps = [
        "KERNEL_RHEL_7_0_VERSION",
        "KERNEL_RHEL_7_1_VERSION",
        "KERNEL_RHEL_7_2_VERSION",
        "KERNEL_RHEL_7_3_VERSION",
        "KERNEL_RHEL_7_4_VERSION",
        "KERNEL_RHEL_7_5_VERSION",
        "KERNEL_RHEL_7_6_VERSION",
        "KERNEL_RHEL_7_7_VERSION",
        "KERNEL_RHEL_7_8_VERSION",
        "KERNEL_RHEL_7_9_VERSION",
        "KERNEL_RHEL_8_0_VERSION",
        "KERNEL_RHEL_8_1_VERSION",
        "KERNEL_RHEL_8_2_VERSION",
        "KERNEL_RHEL_8_3_VERSION",
        "KERNEL_RHEL_8_4_VERSION",
        "KERNEL_RHEL_8_5_VERSION",
        "KERNEL_RHEL_8_6_VERSION",
        "KERNEL_RHEL_9_0_VERSION",
        # Temporarily use this static version
        "Kernel_4.18.0-305.19.1.el8_4.x86_64/cb-1119@re/develop",
    ]
    override_list = "KERNEL_OVERRIDE_LIST"

    def configure(self):
        self.KernelHelper.AddKernelRequires(self,
                                            requires=self.kernelDeps,
                                            override_list=self.override_list)

    #############################################################################################
    # Gets the module version suffix, from the PACKAGE_VERSION.
    # This version suffix becomes a part of the ".ko" filename, also is compiled into code and
    # becomes a part of the device name created by the module.
    # Doing this should allow for more than one kernel-modules to be installed on the system
    # (since each will have its own unique device-node.)
    # example:
    # PACKAGE_VERSION would be 1.6.12349
    # module_version_suffix would be 1_6_12349
    #
    # Converting dots to underscore just because insmod does not like dots.
    #############################################################################################
    def getModuleVersionSuffix(self):

        # Extracting the package_version from
        module_version_suffix = "PROJECT_VERSION"
        module_version_suffix = module_version_suffix.replace('.', '_')

        return module_version_suffix

    def build(self):
        cmake = CMake(self)
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            if os.getenv("FAST_BUILD") != "1":
                cmake.configure(source_dir=self.source_folder + os.path.sep + "src")
            cmake.build()

    def package(self):
        include_dir = "include" + os.path.sep + "dynsec_kmod"
        self.copy("*.h", dst=include_dir, src="include", keep_path=True)
        self.copy("*.ko.*", excludes="*.debug", dst="modules", src="kernel-builds", keep_path=True)
        self.copy("*.symvers.*", dst="symvers", src="kernel-builds", keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs     = ["modules"]
        self.cpp_info.resdirs     = ["symvers"]


        self.user_info.module_version_suffix = self.getModuleVersionSuffix()
        self.user_info.module_name = self.options.module_name + "_" + self.getModuleVersionSuffix()
