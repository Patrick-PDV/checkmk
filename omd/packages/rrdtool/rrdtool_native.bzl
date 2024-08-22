load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("//:bazel_variables.bzl", "UPSTREAM_MIRROR_URL")

def glib_header_local_repo(name):
    native.new_local_repository(
        name = name,
        build_file = "@//omd/packages/rrdtool:glib.bzl",
        path = "/usr",
    )

def rrdtool_native(version_str, sha256):
    filename = "rrdtool-" + version_str + ".tar.gz"
    http_archive(
        name = "rrdtool_native",
        build_file = "@omd_packages//omd/packages/rrdtool:BUILD.rrdtool-native.bazel",
        strip_prefix = "rrdtool-" + version_str,
        urls = [
            "https://github.com/oetiker/rrdtool-1.x/releases/download/v" + version_str + "/" + filename,
            UPSTREAM_MIRROR_URL + filename,
        ],
        patches = [
            "//omd/packages/rrdtool/patches:0001-xff_field_missing_from_rrdinfo.dif",
            "//omd/packages/rrdtool/patches:0003-cli-xport-consistency.dif",
            "//omd/packages/rrdtool/patches:0004-fix-error-formatting.dif",
            "//omd/packages/rrdtool/patches:0005-config-disable_nls.dif",
            "//omd/packages/rrdtool/patches:0006-config-disable_rrd_graph.dif",
            "//omd/packages/rrdtool/patches:0007-config-disable_rrd_restore.dif",
        ],
        patch_args = ["-p1"],
        patch_tool = "patch",
        sha256 = sha256,
    )
