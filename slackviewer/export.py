import os.path
import shutil
from datetime import datetime

from slackviewer.reader import Reader
from slackviewer.archive import get_export_info
from jinja2 import Environment, PackageLoader


def export_multi(archive, save_dir=None, cache_dir=None):
    if cache_dir is None:
        cache_dir = os.path.join(os.getcwd(), "temp")
    os.environ["SLACKVIEWER_TEMP_PATH"] = os.path.join(cache_dir, "_slackviewer")

    tmpl = Environment(loader=PackageLoader('slackviewer')).get_template("export_multi.html")
    export_file_info = get_export_info(archive)
    r = Reader(export_file_info["readable_path"])
    channel_list = sorted(
        [{"channel_name": k, "messages": v} for (k, v) in r.compile_channels().items()],
        key=lambda d: d["channel_name"]
    )

    # save dir
    if save_dir is None:
        save_dir = os.path.join("static", export_file_info["stripped_name"])
    else:
        save_dir = os.path.join(save_dir, "static", export_file_info["stripped_name"])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # copy css
    css_path = os.path.join(save_dir, "viewer.css")
    if not os.path.exists(css_path):
        current_path = os.path.dirname(os.path.realpath(__file__))
        css_src = os.path.join(current_path, "static", "viewer.css")
        shutil.copyfile(src=css_src, dst=css_path)

    # get channel names
    channel_names = list()
    for channel in channel_list:
        channel_names.append(channel.get("channel_name"))

    for channel in channel_list:
        html = tmpl.render(
            generated_on=datetime.now(),
            workspace_name=export_file_info["workspace_name"],
            source_file=export_file_info["basename"],
            channel_names=channel_names,
            channel=channel
        )
        save_filename = channel.get("channel_name") + ".html"
        outfile = open(os.path.join(save_dir, save_filename), 'wb')
        outfile.write(html.encode('utf-8'))

    # delete cache/temp dir
    shutil.rmtree(cache_dir)
