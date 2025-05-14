from flask import Flask, request, jsonify
import subprocess
import os
import webvtt

app = Flask(__name__)

def download_and_extract_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = f"/tmp/{video_id}.%(ext)s"

    try:
        # 1. 자막 다운로드 (자동 생성 한글 자막)
        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "ko",
            "--skip-download",
            "--output", output_template,
            url
        ], check=True)

        # 2. 저장된 VTT 파일 경로
        vtt_path = f"/tmp/{video_id}.ko.vtt"
        if not os.path.exists(vtt_path):
            return None, "자막 파일이 존재하지 않습니다."

        # 3. 자막 파싱 및 텍스트 추출
        transcript_text = ""
        for caption in webvtt.read(vtt_path):
            transcript_text += caption.text + " "

        return transcript_text.strip(), None

    except subprocess.CalledProcessError as e:
        return None, f"yt-dlp 오류: {e}"
    except Exception as e:
        return None, str(e)

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
    app.run()
