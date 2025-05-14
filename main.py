import subprocess
import os
import webvtt
from flask import Flask, request, jsonify

app = Flask(__name__)

def download_and_extract_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = f"/tmp/{video_id}.%(ext)s"  # 파일 저장 경로 설정

    try:
        # 1. 자막 다운로드 (자동 생성 한글 자막)
        result = subprocess.run([
            "yt-dlp",
            "--write-auto-sub",  # 자동 생성 자막 다운로드
            "--sub-lang", "ko",  # 한글 자막만 다운로드
            "--skip-download",  # 비디오는 다운로드하지 않음
            "--output", output_template,  # 저장 경로
            url
        ], check=True, capture_output=True, text=True)

        # 실행된 명령어 출력
        print("stdout:", result.stdout)  # 명령어 실행 로그
        print("stderr:", result.stderr)  # 명령어 오류 로그

        # 2. 자막 파일 경로
        vtt_path = f"/tmp/{video_id}.ko.vtt"
        if not os.path.exists(vtt_path):
            return None, "해당 비디오에는 한국어 자막이 없습니다."

        # 3. 자막 파일 읽고 텍스트 추출
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
