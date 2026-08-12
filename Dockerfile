FROM python:3.10-slim

# FFmpeg ইনস্টল করা
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# --no-cache-dir দিয়ে সবসময় সর্বাধুনিক ভার্সন ইনস্টল করা নিশ্চিত করা
RUN pip install --no-cache-dir -U pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# yt-dlp যেন সবসময় একদম লেটেস্ট ভার্সনে আপডেট থাকে
RUN pip install --no-cache-dir -U yt-dlp

COPY . .

CMD ["python", "main.py"]
