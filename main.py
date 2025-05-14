import subprocess
import os
import webvtt
from flask import Flask, request, jsonify

app = Flask(__name__)

def download_and_extract_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = f"/tmp/{video_id}.%(ext)s"

    # 한국어 → 영어 순서로 자막 시도
    for lang in ["ko", "en"]:
        try:
            # 자동 및 수동 자막 모두 다운로드 시도
            result = subprocess.run([
                "yt-dlp",
                "--cookies", "cookies.txt",          # 로그인 쿠키 사용
                "--write-auto-sub", "--write-sub",   # 자동 + 수동 자막 다운로드
                "--sub-langs", lang,                 # 지정 언어만
                "--skip-download",                   # 영상 다운로드 X
                "--output", output_template,
                url
            ], check=True, capture_output=True, text=True)

            print("stdout:", result.stdout)
            print("stderr:", result.stderr)

            # 저장된 자막 파일 경로
            vtt_path = f"/tmp/{video_id}.{lang}.vtt"
            if os.path.exists(vtt_path):
                transcript_text = ""
                for caption in webvtt.read(vtt_path):
                    transcript_text += caption.text + " "
                return transcript_text.strip(), None

        except subprocess.CalledProcessError as e:
            print(f"[yt-dlp 오류 - {lang}]:", e.stderr)
            continue

    return None, "해당 비디오에는 한국어 또는 영어 자막이 없습니다."

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({'error': 'videoId가 필요합니다.'}), 400

    transcript, error = download_and_extract_transcript(video_id)
    if error:
        return jsonify({'error': error}), 400

    return jsonify({'transcript': transcript})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
