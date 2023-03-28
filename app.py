from flask import Flask
from flask import request
from flask import jsonify
import threading
from lark_helper import LarkHelper
from image_helper import ImageHelper
import os


app = Flask(__name__)

msg_ids = set()


def reply(req):
    lark_helper = LarkHelper(
        os.environ.get("LARK_APP_KEY"), os.environ.get("LARK_APP_SECRET")
    )

    msg_id = req.get("event", {}).get("message", {}).get("message_id")
    if msg_id in msg_ids:
        msg_ids.add(msg_id)
        return None

    source_img = lark_helper.download_img(req)
    img_helper = ImageHelper()
    img_helper.set_size_limit(256, 256)
    img_helper.load_bytes(source_img)
    img_helper.remove_background()
    img_helper.gen_tiktok_style()
    final_img = img_helper.get_img()
    img_key = lark_helper.upload_img(final_img)

    lark_helper.reply_img(msg_id, img_key)


@app.route("/api/lark/callback", methods=["POST"])
def lark_callback():
    req = request.get_json()

    thread = threading.Thread(target=reply, args=(req,))
    thread.daemon = True
    thread.start()

    return jsonify({"success": True})


def main():
    app.run(host="::", port=8888, debug=True)


if __name__ == "__main__":
    main()
