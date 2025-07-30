import sys
from . import api


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        # 执行环境初始化

        from .envs import init_env_file, init_build_json
        import os

        init_env_file()
        cwd = os.getcwd()
        init_build_json(cwd)
        print("已执行pycmakebuild环境初始化")
        return
    # --build 命令：强制执行 build.json 批量编译
    elif len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "--build"):
        import os, json

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
                api.build_and_install(
                    project_path=path,
                    name=name,
                    build_type=api.BuildType[build_type],
                    cmakelists_subpath=cmakelists_subpath,
                    update_source=update_source,
                )
        return
    # ...existing code...


if __name__ == "__main__":
    main()
