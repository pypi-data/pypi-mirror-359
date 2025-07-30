# -*- coding: utf-8 -*-
import sys, os
from pathlib import Path
from dotenv import load_dotenv


def init_env_file():
    """初始化环境变量文件 .env"""
    if not os.path.exists(".env"):
        envs = []
        script_dir = Path(__file__).resolve().parent
        parent_dir = script_dir.parent
        libs_dir = parent_dir / "libs"
        envs.append(f"# 安装路径，所有库的安装输出目录")
        envs.append(f"INSTALL_PATH={libs_dir}")
        envs.append(f"# 架构类型")
        envs.append(f"ARCH=x64")
        envs.append(f"# 构建中间文件夹路径")
        envs.append(f"BUILD_DIR=build")
        if sys.platform.startswith("win"):
            envs.append(f"# CMake生成器类型")
            envs.append(f"GENERATOR=Visual Studio 16 2019")
        else:
            envs.append(f"# CMake生成器类型")
            envs.append(f"GENERATOR=Unix Makefiles")

        with open(".env", "w", encoding="utf-8") as f:
            f.write("\n".join(envs))


def init_build_json(target_dir=None, name=None):
    import json

    build_json_path = os.path.join(target_dir or os.getcwd(), "build.json")
    if not os.path.exists(build_json_path):
        build_json = {
            "sources": [
                {
                    "path": "源码路径",
                    "name": "目标目录名称",
                    "build_types": ["Debug", "Release"],
                    "cmakelists_subpath": "CMakeLists.txt所在子目录（可选）",
                    "update_source": True,
                    "other_build_params": ["-DCUSTOM_OPTION=ON"]
                }
            ]
        }
        with open(build_json_path, "w", encoding="utf-8") as f:
            json.dump(build_json, f, indent=2, ensure_ascii=False)
        print(f"已创建 {build_json_path}")
    else:
        print(f"已存在 {build_json_path}")


IS_WINDOWS = sys.platform.startswith("win")
print(f"IS_WINDOWS={IS_WINDOWS}")

load_dotenv(".env")

INSTALL_PATH = os.getenv("INSTALL_PATH")
if len(INSTALL_PATH) == 0:
    raise ("未设置INSTALL_PATH")
else:
    print(f"INSTALL_PATH={INSTALL_PATH}")

GENERATOR = os.getenv("GENERATOR")
if len(GENERATOR) == 0:
    raise ("未设置GENERATOR")
else:
    print(f"GENERATOR={GENERATOR}")

ARCH = os.getenv("ARCH")
if len(ARCH) == 0:
    raise ("未设置ARCH")
else:
    print(f"ARCH={ARCH}")


BUILD_DIR = os.getenv("BUILD_DIR")
if len(BUILD_DIR) == 0:
    BUILD_DIR = "build"

print(f"BUILD_DIR={BUILD_DIR}")


# 根据平台、GENERATOR和ARCH自动推断CMAKE_ARCH
def guess_cmake_arch():
    if not IS_WINDOWS:
        return ""
    gen = GENERATOR.lower() if GENERATOR else ""
    arch = ARCH.lower() if ARCH else ""
    # Visual Studio 2019/2022
    if "visual studio" in gen:
        if arch in ["x86", "win32"]:
            return "-A Win32"
        elif arch in ["x64", "amd64"]:
            return "-A x64"
        elif arch in ["arm64"]:
            return "-A ARM64"
    # Ninja/MinGW等
    if "ninja" in gen or "mingw" in gen:
        if arch in ["x64", "amd64"]:
            return "-D CMAKE_GENERATOR_PLATFORM=x64"
        elif arch in ["x86", "win32"]:
            return "-D CMAKE_GENERATOR_PLATFORM=Win32"
        elif arch in ["arm64"]:
            return "-D CMAKE_GENERATOR_PLATFORM=ARM64"
    return ""


CMAKE_ARCH = os.getenv("CMAKE_ARCH")
if not CMAKE_ARCH or CMAKE_ARCH.strip() == "":
    CMAKE_ARCH = guess_cmake_arch()
print(f"CMAKE_ARCH={CMAKE_ARCH}")
