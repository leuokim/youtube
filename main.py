import subprocess
import os
import webvtt
from flask import Flask, request, jsonify

app = Flask(__name__)

def download_and_extract_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = f"/tmp/{video_id}.%(ext)s"  # 자막 저장 경로

    try:
        # yt-dlp 명령어 실행
        result = subprocess.run([
            "yt-dlp",
            "--cookies", "cookies.txt",  # 쿠키 파일 사용
            "--write-auto-sub",          # 자동 생성 자막 다운로드
            "--sub-lang", "ko",          # 한글 자막만
            "--skip-download",           # 영상은 다운로드하지 않음
            "--output", output_template, # 저장 경로
            url
        ], check=True, capture_output=True, text=True)

        # 로그 출력 (디버깅용)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)

        # 저장된 자막 파일 경로
        vtt_path = f"/tmp/{video_id}.ko.vtt"
        if not os.path.exists(vtt_path):
            return None, "해당 비디오에는 한국어 자막이 없습니다."

        # 자막 파일 읽기
        transcript_text = ""
        for caption in webvtt.read(vtt_path):
            transcript_text += caption.text + " "

        return transcript_text.strip(), None

    except subprocess.CalledProcessError as e:
        return None, f"yt-dlp 오류: {e.stderr}"
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
    app.run(host='0.0.0.0', port=5000)
