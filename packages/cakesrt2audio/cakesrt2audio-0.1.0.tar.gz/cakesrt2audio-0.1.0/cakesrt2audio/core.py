import asyncio
import logging
import srt
import tempfile
import os
import subprocess
from datetime import datetime, timedelta
from pydub import AudioSegment
from edge_tts import Communicate
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
MAX_RETRIES = 3

# --- Helper Functions ---

async def _generate_tts_segment_with_retry(semaphore, sub, voice, temp_dir, index):
    """Coroutine to generate a single TTS audio segment with retries."""
    async with semaphore:
        logging.info(f"Generating audio for subtitle #{index+1}...")
        text = sub.content
        temp_audio_path = os.path.join(temp_dir, f"sub_{index+1}.mp3")
        
        for attempt in range(MAX_RETRIES):
            try:
                communicate = Communicate(text, voice)
                await communicate.save(temp_audio_path)
                logging.info(f"Finished audio for subtitle #{index+1} on attempt {attempt+1}.")
                return temp_audio_path, sub
            except Exception as e:
                logging.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed for subtitle #{index+1}: {e}")
                if attempt + 1 == MAX_RETRIES:
                    logging.error(f"All retries failed for subtitle #{index+1}. Skipping.")
                    return None, sub
                await asyncio.sleep(2) # Wait before retrying
        return None, sub

def run_ffmpeg_command(command):
    """Runs an FFmpeg command using subprocess, raising an error if it fails."""
    process = subprocess.run(command, check=True, capture_output=True, text=True)
    if process.returncode != 0:
        logging.error("FFmpeg Error Stderr: %s", process.stderr)
        logging.error("FFmpeg Error Stdout: %s", process.stdout)
        raise subprocess.CalledProcessError(process.returncode, command, output=process.stdout, stderr=process.stderr)

def get_video_duration(video_path):
    """Get video duration in seconds."""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

# --- Core Logic: Audio-Only Mode ---

async def _create_audio_only(subs, voice, output_file, concurrency):
    """Generates a single audio file by stitching TTS segments based on SRT timings."""
    total_duration_ms = int(subs[-1].end.total_seconds() * 1000)
    final_audio = AudioSegment.silent(duration=total_duration_ms)
    temp_dir = tempfile.mkdtemp(prefix="cakesrt_audio_")
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [_generate_tts_segment_with_retry(semaphore, sub, voice, temp_dir, i) for i, sub in enumerate(subs)]
    results = await asyncio.gather(*tasks)

    logging.info("Stitching audio segments...")
    for i, (audio_path, sub) in enumerate(results):
        if not audio_path:
            continue
        
        try:
            clip = AudioSegment.from_mp3(audio_path)
            start_time_ms = int(sub.start.total_seconds() * 1000)
            final_audio = final_audio.overlay(clip, position=start_time_ms)
            os.remove(audio_path)
        except Exception as e:
            logging.error(f"Could not process segment #{i+1}: {e}")

    final_audio.export(output_file, format="mp3")
    os.rmdir(temp_dir)
    logging.info(f"Successfully generated audio file: {output_file}")

# --- Core Logic: Video Mode ---

def extract_video_segment(video_path, start_time, duration, output_path):
    """Extract video segment from original video."""
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_time),
        '-i', video_path,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ]
    run_ffmpeg_command(cmd)

def scale_video_to_duration(input_video_path, target_duration, output_path):
    """Scale video to exact target duration using setpts."""
    # 获取原视频时长
    original_duration = get_video_duration(input_video_path)
    
    # 计算setpts倍数：目标时长 / 原时长
    # 如果目标时长更长，倍数>1，视频变慢
    # 如果目标时长更短，倍数<1，视频变快
    setpts_multiplier = target_duration / original_duration
    
    logging.info(f"Scaling video: {original_duration:.2f}s -> {target_duration:.2f}s (setpts multiplier: {setpts_multiplier:.3f})")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video_path,
        '-filter:v', f'setpts={setpts_multiplier}*PTS',
        '-an',  # 移除音频
        output_path
    ]
    run_ffmpeg_command(cmd)
    
    # 验证输出时长
    actual_duration = get_video_duration(output_path)
    logging.info(f"Scaled video actual duration: {actual_duration:.2f}s (target: {target_duration:.2f}s)")

def merge_video_audio(video_path, audio_path, output_path):
    """Merge scaled video with generated audio."""
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_path
    ]
    run_ffmpeg_command(cmd)

async def process_single_segment(semaphore, video_path, sub, voice, segment_dir, index):
    """Process a single SRT segment: extract video, generate audio, scale and merge."""
    async with semaphore:
        segment_id = f"segment_{index+1:03d}"
        logging.info(f"Processing {segment_id}...")
        
        # 创建条目文件夹
        segment_folder = os.path.join(segment_dir, segment_id)
        os.makedirs(segment_folder, exist_ok=True)
        
        try:
            # 步骤1: 提取原始视频片段
            srt_start = sub.start.total_seconds()
            srt_duration = (sub.end - sub.start).total_seconds()
            
            original_video_segment = os.path.join(segment_folder, f"original_video_{segment_id}.mp4")
            extract_video_segment(video_path, srt_start, srt_duration, original_video_segment)
            orig_duration = get_video_duration(original_video_segment)
            logging.info(f"{segment_id}: Extracted original video segment ({orig_duration:.2f}s)")
            
            # 步骤2: 生成音频
            text = sub.content
            audio_path = os.path.join(segment_folder, f"audio_{segment_id}.mp3")
            
            for attempt in range(MAX_RETRIES):
                try:
                    communicate = Communicate(text, voice)
                    await communicate.save(audio_path)
                    logging.info(f"{segment_id}: Generated audio on attempt {attempt+1}")
                    break
                except Exception as e:
                    logging.warning(f"{segment_id}: Audio generation attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
                    if attempt + 1 == MAX_RETRIES:
                        logging.error(f"{segment_id}: All audio generation attempts failed")
                        return None
                    await asyncio.sleep(2)
            
            # 步骤3: 计算音频时长并缩放视频
            audio_clip = AudioSegment.from_mp3(audio_path)
            target_duration = len(audio_clip) / 1000.0
            
            scaled_video_path = os.path.join(segment_folder, f"scaled_video_{segment_id}.mp4")
            scale_video_to_duration(original_video_segment, target_duration, scaled_video_path)
            scaled_duration = get_video_duration(scaled_video_path)
            logging.info(f"{segment_id}: Scaled video from {orig_duration:.2f}s to {scaled_duration:.2f}s (target: {target_duration:.2f}s)")
            
            # 步骤4: 合并缩放后的视频和音频
            final_segment_path = os.path.join(segment_folder, f"final_{segment_id}.mp4")
            merge_video_audio(scaled_video_path, audio_path, final_segment_path)
            final_duration = get_video_duration(final_segment_path)
            logging.info(f"{segment_id}: Final segment duration: {final_duration:.2f}s")
            
            return final_segment_path
            
        except Exception as e:
            logging.error(f"{segment_id}: Processing failed: {e}")
            return None

async def _create_video_output(subs, voice, video_path, srt_file, output_file, concurrency):
    """Generates a video with synced audio where each segment duration equals its audio duration."""
    
    # 创建workspace目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace_dir = os.path.join("workspace", f"video_process_{timestamp}")
    os.makedirs(workspace_dir, exist_ok=True)
    
    semaphore = asyncio.Semaphore(concurrency)
    
    # 并行处理所有片段
    logging.info("Step 1: Processing all segments in parallel...")
    segment_tasks = [
        process_single_segment(semaphore, video_path, sub, voice, workspace_dir, i) 
        for i, sub in enumerate(subs)
    ]
    segment_results = await asyncio.gather(*segment_tasks)
    
    # 过滤出成功处理的片段
    successful_segments = [path for path in segment_results if path is not None]
    
    if not successful_segments:
        logging.error("No segments were successfully processed.")
        return
    
    logging.info(f"Step 2: Successfully processed {len(successful_segments)}/{len(subs)} segments")
    
    # 合并所有片段
    logging.info("Step 3: Concatenating all segments...")
    concat_list_path = os.path.join(workspace_dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for segment_path in successful_segments:
            f.write(f"file '{os.path.abspath(segment_path)}'\n")
    
    temp_concatenated = os.path.join(workspace_dir, "concatenated_video.mp4")
    cmd_concat = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', concat_list_path,
        '-c', 'copy',
        temp_concatenated
    ]
    run_ffmpeg_command(cmd_concat)
    
    # 添加字幕
    logging.info("Step 4: Adding subtitles to final video...")
    cmd_add_subtitles = [
        'ffmpeg', '-y',
        '-i', temp_concatenated,
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-vf', f"subtitles='{os.path.abspath(srt_file)}'",
        output_file
    ]
    run_ffmpeg_command(cmd_add_subtitles)
    
    logging.info(f"Step 5: Process completed successfully!")
    logging.info(f"Workspace directory: {workspace_dir}")
    logging.info(f"Output file: {output_file}")

# --- Main Entry Point ---

async def create_audio_from_srt(srt_file: str, voice: str, output_file: str, concurrency: int, video_path: str = None):
    """Main function to orchestrate audio or video generation."""
    logging.info(f"Starting process for SRT: {srt_file}")
    
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            subs = list(srt.parse(f.read()))
    except Exception as e:
        logging.error(f"Failed to read or parse SRT file: {e}")
        return

    if not subs:
        logging.warning("SRT file is empty or invalid. No output will be generated.")
        return

    # 确保workspace目录存在
    if video_path and not os.path.exists("workspace"):
        os.makedirs("workspace")

    if video_path:
        await _create_video_output(subs, voice, video_path, srt_file, output_file, concurrency)
    else:
        await _create_audio_only(subs, voice, output_file, concurrency)