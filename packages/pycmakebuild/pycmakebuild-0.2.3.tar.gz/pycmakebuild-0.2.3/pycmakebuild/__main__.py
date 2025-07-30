import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("""
pycmakebuild - 批量构建CMake工程的Python工具

用法:
  pycmakebuild --init        初始化环境和 build.json 模板
  pycmakebuild --build       根据 build.json 批量构建
  pycmakebuild --version/-v  显示版本号
  pycmakebuild --help/-h     显示帮助信息
  pycmakebuild               自动检测 build.json 并批量构建

build.json 支持字段:
  path              CMake 项目源码路径
  name              目标名称
  build_types       构建类型数组（如 Debug/Release）
  cmakelists_subpath CMakeLists.txt 所在子目录（可选）
  update_source     是否自动 git clean/pull（可选）
  other_build_params  传递给 cmake 的额外参数列表（可选）
        """)
        return
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v"):
        try:
            from importlib.metadata import version
        except ImportError:
            from pkg_resources import get_distribution as version
        try:
            ver = version("pycmakebuild")
        except Exception:
            ver = "(dev)"
        print(f"pycmakebuild version: {ver}")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        # 执行环境初始化

        import os
        from .envs import init_env_file, init_build_json

        init_env_file()
        cwd = os.getcwd()
        init_build_json(cwd)
        print("已执行pycmakebuild环境初始化")
        return
    # --build 命令：强制执行 build.json 批量编译
    elif len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "--build"):
        import os, json
        from .api import build_and_install, BuildType

        build_json_path = os.path.join(os.getcwd(), "build.json")
        if not os.path.exists(build_json_path):
            print("未找到 build.json")
            return
        with open(build_json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        sources = config.get("sources", [])
        for item in sources:
            path = item.get("path")
            name = item.get("name")
            build_types = item.get("build_types", ["Debug"])
            cmakelists_subpath = item.get("cmakelists_subpath", "")
            update_source = item.get("update_source", False)
            for build_type in build_types:
                print(f"\n==== 构建 {name} [{build_type}] ====")
                build_and_install(
                    project_path=path,
                    name=name,
                    build_type=BuildType[build_type],
                    cmakelists_subpath=cmakelists_subpath,
                    update_source=update_source,
                )
        return
    # ...existing code...


if __name__ == "__main__":
    main()
