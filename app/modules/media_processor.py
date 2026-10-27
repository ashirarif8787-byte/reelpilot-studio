"""
Module 2b: Media Processing Engine (FFmpeg Powered)
Converts images into 7-10s vertical 9:16 Reels/TikToks with blurred aesthetic padding,
merges trending viral audio tracks, and normalizes silent or non-standard videos.
"""
import os
import subprocess
from typing import Optional, Tuple
from app.config import config_manager
from app.database.models import MediaType
from app.modules.audio_fetcher import audio_service
from app.utils.helpers import detect_media_type, video_has_audio, get_media_duration
from app.utils.logger import logger


class MediaProcessor:
    def __init__(self, output_dir: Optional[str] = None):
        if os.environ.get("VERCEL"):
            self.output_dir = "/tmp/processed_media"
        else:
            self.output_dir = output_dir or config_manager.config.processed_folder
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception:
            pass

    def process_media(
        self,
        input_path: str,
        target_platform: str,
        custom_audio_path: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Main entry point for media processing.
        Returns: (success: bool, processed_file_path: str, error_message: Optional[str])
        """
        if not os.path.exists(input_path):
            return False, "", f"Input file not found: {input_path}"

        media_type = detect_media_type(input_path)
        if not media_type:
            return False, "", f"Unsupported file extension: {input_path}"

        file_basename = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{target_platform}_{file_basename}_processed.mp4"
        output_path = os.path.join(self.output_dir, output_filename)

        # Select audio track
        audio_path = custom_audio_path or audio_service.get_random_viral_track()
        if not audio_path or not os.path.exists(audio_path):
            audio_service.ensure_default_sounds()
            audio_path = audio_service.get_random_viral_track()

        duration = duration or config_manager.config.image_duration_seconds

        try:
            if media_type == MediaType.IMAGE.value:
                success = self.convert_image_to_reel(
                    image_path=input_path,
                    audio_path=audio_path,
                    output_path=output_path,
                    duration=duration
                )
            else:
                success = self.process_video_with_audio(
                    video_path=input_path,
                    audio_path=audio_path,
                    output_path=output_path
                )

            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
                # Generate a quick thumbnail preview poster for UI cards
                thumb_path = output_path.replace(".mp4", "_thumb.jpg")
                try:
                    subprocess.run(["ffmpeg", "-y", "-ss", "00:00:01", "-i", output_path, "-vframes", "1", "-q:v", "2", thumb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception:
                    pass
                logger.info(f"✅ [MediaProcessor] Successfully rendered: {os.path.basename(output_path)}")
                return True, os.path.abspath(output_path), None
            else:
                return False, "", "Output file was not generated or has zero size."

        except Exception as e:
            logger.error(f"[MediaProcessor] Error processing {input_path}: {e}")
            return False, "", str(e)

    def convert_image_to_reel(
        self,
        image_path: str,
        audio_path: Optional[str],
        output_path: str,
        duration: int = 8
    ) -> bool:
        """
        Converts a static image into an 8-second 1080x1920 9:16 vertical Reel/TikTok.
        Uses background blur with foreground centering and smooth audio fade out.
        """
        w = config_manager.config.video_width
        h = config_manager.config.video_height
        fps = config_manager.config.fps

        # FFmpeg filter:
        # Background: scaled to fill 1080x1920 + blurred
        # Foreground: scaled to fit maintaining aspect ratio
        # Overlay: centered on background
        filter_complex = (
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},boxblur=20:5[bg];"
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]"
        )

        audio_input = []
        audio_map = []
        if audio_path and os.path.exists(audio_path):
            audio_input = ["-stream_loop", "-1", "-i", audio_path]
            # Add subtle fade-out in last 0.5 seconds
            fade_out_start = max(0, duration - 1)
            audio_map = [
                "-filter:a", f"afade=t=out:st={fade_out_start}:d=1.0",
                "-map", "[v]",
                "-map", "1:a"
            ]
        else:
            audio_map = ["-map", "[v]"]

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-framerate", str(fps),
            "-t", str(duration),
            "-i", image_path
        ] + audio_input + [
            "-filter_complex", filter_complex
        ] + audio_map + [
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-t", str(duration),
            "-movflags", "+faststart",
            output_path
        ]

        logger.info(f"[MediaProcessor] Rendering image to vertical Reel: {os.path.basename(image_path)} -> {os.path.basename(output_path)}")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            logger.error(f"[MediaProcessor] FFmpeg failed: {res.stderr[-500:]}")
            return False
        return True

    def process_video_with_audio(
        self,
        video_path: str,
        audio_path: Optional[str],
        output_path: str
    ) -> bool:
        """
        Normalizes video into 1080x1920 vertical format.
        If video is silent, merges the viral audio track automatically.
        """
        w = config_manager.config.video_width
        h = config_manager.config.video_height
        has_audio = video_has_audio(video_path)
        video_duration = get_media_duration(video_path) or 10.0

        filter_complex = (
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},boxblur=20:5[bg];"
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]"
        )

        if not has_audio and audio_path and os.path.exists(audio_path):
            logger.info(f"[MediaProcessor] Silent video detected. Merging viral audio: {os.path.basename(audio_path)}")
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-stream_loop", "-1",
                "-i", audio_path,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "1:a",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", str(video_duration),
                "-movflags", "+faststart",
                output_path
            ]
        else:
            logger.info(f"[MediaProcessor] Normalizing video aspect ratio to 1080x1920...")
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-c:v", "libx264",
                "-c:a", "copy" if has_audio else "aac",
                "-movflags", "+faststart",
                output_path
            ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            logger.error(f"[MediaProcessor] FFmpeg failed: {res.stderr[-500:]}")
            return False
        return True


# Global singleton
media_processor = MediaProcessor()


if __name__ == "__main__":
    print("=== Testing Module 2b: Media Processor ===")
    from PIL import Image, ImageDraw
    # Create a quick sample test image
    test_img_path = os.path.join(config_manager.config.watch_folder_insta, "sample_test.png")
    os.makedirs(os.path.dirname(test_img_path), exist_ok=True)
    img = Image.new("RGB", (800, 800), color=(30, 144, 255))
    draw = ImageDraw.Draw(img)
    draw.text((250, 380), "Viral Automation Test", fill=(255, 255, 255))
    img.save(test_img_path)
    print(f"Created sample image: {test_img_path}")

    success, processed, err = media_processor.process_media(
        input_path=test_img_path,
        target_platform="instagram"
    )
    print(f"Result: success={success}, processed={processed}, err={err}")
