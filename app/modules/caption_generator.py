"""
Module 3: Dual-AI Multimodal Vision Engine (Gemini & OpenAI)
Analyzes the actual product image or video frame to identify the product, style, and vibe.
Generates:
1. Viral Curiosity Hook
2. Compelling Product Description & Features with custom Brand CTA
3. 5-8 Trending Hashtags targeted directly to the product
4. Recommended Viral Audio Vibe / Mood for audio syncing
"""
import os
import re
import json
import base64
import subprocess
import requests
from io import BytesIO
from typing import Tuple, Optional, Dict, Any
from PIL import Image

from app.config import config_manager
from app.utils.logger import logger

FALLBACK_TAGS = {
    "instagram": ["#reelsviral", "#instadaily", "#explorepage", "#viralreels", "#trendingnow", "#reelsinstagram"],
    "tiktok": ["#fyp", "#foryoupage", "#viralvideo", "#trending", "#tiktokmademebuyit", "#foryou"],
    "facebook": ["#facebookreels", "#reelsfb", "#viralvideo", "#trending", "#instareels", "#fyp"]
}


class DualAICaptionGenerator:
    def __init__(self):
        pass

    def _prepare_image_base64(self, file_path: str, max_size: int = 1024) -> Tuple[Optional[str], str]:
        """
        Reads image or extracts poster frame from video, resizes to web-friendly dimension,
        and returns (base64_str, mime_type).
        """
        ext = os.path.splitext(file_path)[1].lower()
        temp_thumb = None

        if ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
            # Extract frame from 1 second mark of video
            temp_thumb = file_path + "_ai_temp_frame.jpg"
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", "00:00:01", "-i", file_path, "-vframes", "1", "-q:v", "2", temp_thumb],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
                )
                img_path = temp_thumb
            except Exception:
                return None, "image/jpeg"
        else:
            img_path = file_path

        if not os.path.exists(img_path):
            return None, "image/jpeg"

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((max_size, max_size))
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                b64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
                return b64_data, "image/jpeg"
        except Exception as e:
            logger.warning(f"[AIVision] Image preparation warning: {e}")
            return None, "image/jpeg"
        finally:
            if temp_thumb and os.path.exists(temp_thumb):
                try:
                    os.remove(temp_thumb)
                except Exception:
                    pass

    def generate(self, file_path: str, platform: str = "instagram") -> Tuple[str, str, Optional[str]]:
        """
        Analyzes the image/video using Google Gemini or OpenAI GPT-4o Vision.
        Returns: (caption: str, hashtags: str, recommended_sound_vibe: Optional[str])
        """
        b64_img, mime_type = self._prepare_image_base64(file_path)
        brand = config_manager.config.brand_name or "Our Brand"
        filename_hint = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").replace("-", " ")

        gemini_key = config_manager.config.gemini_api_key.strip()
        openai_key = config_manager.config.openai_api_key.strip()
        preferred_engine = config_manager.config.ai_engine

        # 1. Try Google Gemini Vision
        if (preferred_engine in ["gemini", "auto"] and gemini_key) or (gemini_key and not openai_key):
            try:
                logger.info(f"👁️ [AIVision] Analyzing image via Google Gemini Vision ({config_manager.config.gemini_model}) for Brand: '{brand}'...")
                caption, tags, sound = self._call_gemini_vision(b64_img, mime_type, brand, platform, filename_hint)
                if caption:
                    return caption, tags, sound
            except Exception as e:
                logger.warning(f"[AIVision] Gemini Vision call failed: {e}. Trying fallback...")

        # 2. Try OpenAI GPT-4o Vision
        if (preferred_engine in ["openai", "auto"] and openai_key) or openai_key:
            try:
                logger.info(f"👁️ [AIVision] Analyzing image via OpenAI GPT-4o Vision for Brand: '{brand}'...")
                caption, tags, sound = self._call_openai_vision(b64_img, brand, platform, filename_hint)
                if caption:
                    return caption, tags, sound
            except Exception as e:
                logger.warning(f"[AIVision] OpenAI Vision call failed: {e}. Trying fallback...")

        # 3. Intelligent Heuristic Fallback
        logger.info(f"[AIVision] Generating smart product caption using heuristic templates for '{brand}'...")
        return self._generate_smart_fallback(filename_hint, brand, platform)

    def _call_gemini_vision(
        self,
        b64_img: Optional[str],
        mime_type: str,
        brand: str,
        platform: str,
        filename_hint: str
    ) -> Tuple[str, str, Optional[str]]:
        """Calls Google Gemini 1.5/2.0 Flash Vision API directly via REST."""
        api_key = config_manager.config.gemini_api_key.strip()
        model = config_manager.config.gemini_model or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        prompt = (
            f"You are a viral social media growth copywriter and e-commerce expert for {platform.upper()}.\n"
            f"Brand Name: '{brand}'\n"
            f"File context: '{filename_hint}'\n\n"
            "Analyze this product/scene image carefully.\n"
            "Format your answer EXACTLY as these 4 sections:\n"
            "HOOK: [1 viral, high-retention curiosity hook with emoji]\n"
            "DESCRIPTION: [1-2 sentence compelling product description highlighting aesthetics and benefits, ending with a Call-To-Action mentioning the brand name]\n"
            "SOUND_VIBE: [Recommend a 2-word trending sound vibe, e.g. Upbeat Phonk, Luxury Lo-Fi, Energetic Trap, or Cinematic Beat]\n"
            "HASHTAGS: [Exactly 6 to 8 trending hashtags directly relevant to this product and niche, starting with #]"
        )

        parts = [{"text": prompt}]
        if b64_img:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_img
                }
            })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0.75, "maxOutputTokens": 350}
        }

        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
        data = resp.json()

        if "error" in data:
            raise RuntimeError(data["error"].get("message", "Gemini API error"))

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return self._parse_vision_response(raw_text, platform, brand)

    def _call_openai_vision(
        self,
        b64_img: Optional[str],
        brand: str,
        platform: str,
        filename_hint: str
    ) -> Tuple[str, str, Optional[str]]:
        """Calls OpenAI GPT-4o Vision API directly via REST."""
        api_key = config_manager.config.openai_api_key.strip()
        model = config_manager.config.openai_model or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"

        prompt = (
            f"You are a viral social media growth copywriter and e-commerce expert for {platform.upper()}.\n"
            f"Brand Name: '{brand}'\n"
            f"File context: '{filename_hint}'\n\n"
            "Analyze this product/scene image carefully.\n"
            "Format your answer EXACTLY as these 4 sections:\n"
            "HOOK: [1 viral, high-retention curiosity hook with emoji]\n"
            "DESCRIPTION: [1-2 sentence compelling product description highlighting aesthetics and benefits, ending with a Call-To-Action mentioning the brand name]\n"
            "SOUND_VIBE: [Recommend a 2-word trending sound vibe, e.g. Upbeat Phonk, Luxury Lo-Fi, Energetic Trap, or Cinematic Beat]\n"
            "HASHTAGS: [Exactly 6 to 8 trending hashtags directly relevant to this product and niche, starting with #]"
        )

        content_parts = [{"type": "text", "text": prompt}]
        if b64_img:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
            })

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content_parts}],
            "max_tokens": 350,
            "temperature": 0.75
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        data = resp.json()

        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI API error"))

        raw_text = data["choices"][0]["message"]["content"].strip()
        return self._parse_vision_response(raw_text, platform, brand)

    def _parse_vision_response(self, text: str, platform: str, brand: str) -> Tuple[str, str, Optional[str]]:
        """Parses HOOK, DESCRIPTION, SOUND_VIBE, and HASHTAGS from AI response."""
        hook = ""
        description = ""
        sound_vibe = None
        hashtags = ""

        for line in text.splitlines():
            line_s = line.strip()
            if line_s.upper().startswith("HOOK:"):
                hook = line_s.split(":", 1)[1].strip()
            elif line_s.upper().startswith("DESCRIPTION:"):
                description = line_s.split(":", 1)[1].strip()
            elif line_s.upper().startswith("SOUND_VIBE:"):
                sound_vibe = line_s.split(":", 1)[1].strip()
            elif line_s.upper().startswith("HASHTAGS:"):
                hashtags = line_s.split(":", 1)[1].strip()

        # If strict sections weren't preserved, fallback to regex
        if not hook or not description:
            all_tags = re.findall(r"#\w+", text)
            hashtags = " ".join(all_tags[:8])
            clean_body = re.sub(r"#\w+", "", text).strip()
            caption = clean_body
        else:
            caption = f"{hook}\n\n{description}"

        if not hashtags:
            hashtags = " ".join(FALLBACK_TAGS.get(platform, FALLBACK_TAGS["instagram"]))

        return caption, hashtags, sound_vibe

    def _generate_smart_fallback(self, filename_hint: str, brand: str, platform: str) -> Tuple[str, str, Optional[str]]:
        """Intelligent offline fallback with Brand and Product details."""
        hook = f"Obsessed with this new drop! ✨👀"
        desc = f"Experience the perfect blend of style and quality with {brand}. Save this post and tap the link in bio to explore the collection! 👇"
        caption = f"{hook}\n\n{desc}"

        tags = FALLBACK_TAGS.get(platform, FALLBACK_TAGS["instagram"]).copy()
        clean_brand = re.sub(r"\W+", "", brand.lower())
        if clean_brand:
            tags.insert(0, f"#{clean_brand}")
        clean_prod = re.sub(r"\W+", "", filename_hint.lower())
        if clean_prod and clean_prod not in ["image", "video", "photo"]:
            tags.insert(1, f"#{clean_prod}")

        hashtag_str = " ".join(tags[:8])
        return caption, hashtag_str, "Luxury Lo-Fi"

    def generate_perfume_copy(
        self,
        product_name: str,
        volume_ml: str = "100ml",
        scent_notes: str = "",
        price_offer: str = "",
        platform: str = "instagram",
        image_path: Optional[str] = None
    ) -> Tuple[str, str, Optional[str]]:
        """
        Generates 100% authentic, high-converting luxury perfume sales description
        and targeted trending hashtags based on user's exact perfume name, bottle volume, notes, and pricing.
        """
        brand = config_manager.config.brand_name or "JANI's Perfume"
        product_name = (product_name or "Signature Luxury Fragrance").strip()
        volume_ml = (volume_ml or "100ml").strip()
        scent_notes = (scent_notes or "Rich Woody Oud, Warm Amber, Sensual Vanilla").strip()
        price_offer = (price_offer or "Special Launch Price with Free Delivery").strip()

        gemini_key = config_manager.config.gemini_api_key.strip()
        openai_key = config_manager.config.openai_api_key.strip()

        clean_prod = re.sub(r"\W+", "", product_name)
        clean_brand = re.sub(r"\W+", "", brand)
        clean_vol = re.sub(r"\W+", "", volume_ml)

        prompt = (
            f"You are the master luxury fragrance copywriter for high-end perfume brand '{brand}'.\n"
            f"Perfume Name: '{product_name}'\n"
            f"Bottle Volume / Size: '{volume_ml}'\n"
            f"Fragrance Accords / Notes: '{scent_notes}'\n"
            f"Pricing / Special Offer: '{price_offer}'\n"
            f"Destination Platform: {platform.upper()}\n\n"
            "Write a 100% authentic, captivating, ultra-luxurious fragrance post description.\n"
            "It must sound like a prestigious luxury perfume house.\n"
            "Format your answer EXACTLY as:\n"
            "HOOK: [1 stunning luxury curiosity hook with emojis 👑, ✨, 💎]\n"
            f"DESCRIPTION: [3-4 sentences describing the alluring olfactory journey of '{product_name}'. Explicitly mention the '{volume_ml}' bottle size, 14+ hours beast-mode longevity, projection, and compliment factor. Mention the offer '{price_offer}'. End with a strong Call-to-Action to DM or WhatsApp to order!]\n"
            "SOUND_VIBE: [2-word luxury sound vibe, e.g. Royal Amber or Luxury Lo-Fi]\n"
            f"HASHTAGS: [Exactly 10 to 12 authentic, trending perfume hashtags targeting fragrance lovers, e.g. #{clean_brand} #{clean_prod} #{clean_vol}Perfume #LuxuryFragrance #PerfumesPakistan #LongLastingScent #OudLovers #ScentOfTheDay #KarachiPerfumes #LahoreShopping #EauDeParfum]"
        )

        b64_img, mime_type = (None, "image/jpeg")
        if image_path and os.path.exists(image_path):
            b64_img, mime_type = self._prepare_image_base64(image_path)

        # 1. Try Gemini
        if gemini_key:
            try:
                model = config_manager.config.gemini_model or "gemini-1.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                parts = [{"text": prompt}]
                if b64_img:
                    parts.append({"inline_data": {"mime_type": mime_type, "data": b64_img}})
                resp = requests.post(url, json={"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.75, "maxOutputTokens": 450}}, timeout=15)
                data = resp.json()
                if "candidates" in data and data["candidates"]:
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    cap, tags, vibe = self._parse_vision_response(raw_text, platform, brand)
                    if cap and len(cap) > 20:
                        return cap, tags, vibe
            except Exception as e:
                logger.warning(f"[AIVision] Gemini perfume copy error: {e}")

        # 2. Try OpenAI
        if openai_key:
            try:
                model = config_manager.config.openai_model or "gpt-4o-mini"
                url = "https://api.openai.com/v1/chat/completions"
                parts = [{"type": "text", "text": prompt}]
                if b64_img:
                    parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}})
                resp = requests.post(url, json={"model": model, "messages": [{"role": "user", "content": parts}], "max_tokens": 450, "temperature": 0.75}, headers={"Authorization": f"Bearer {openai_key}"}, timeout=15)
                data = resp.json()
                if "choices" in data and data["choices"]:
                    raw_text = data["choices"][0]["message"]["content"].strip()
                    cap, tags, vibe = self._parse_vision_response(raw_text, platform, brand)
                    if cap and len(cap) > 20:
                        return cap, tags, vibe
            except Exception as e:
                logger.warning(f"[AIVision] OpenAI perfume copy error: {e}")

        # 3. Mastercrafted 100% Authentic Luxury Copywriting Fallback
        hook = f"👑 Step into Unrivaled Elegance with {product_name} by {brand} ✨"
        desc = (
            f"Designed for those who appreciate true artistry in perfumery, {product_name} is a masterwork of olfactory sophistication.\n\n"
            f"💎 Notes Profile: Opening with {scent_notes}, delivering a smooth, intoxicating aura that commands compliments wherever you go.\n"
            f"⏳ Longevity & Sillage: Certified 14+ hours long-lasting performance with an unforgettable royal scent trail.\n"
            f"📦 Bottle Size: Encased in a luxurious {volume_ml} Eau De Parfum spray.\n"
            f"🎁 Special Offer: {price_offer} — available with Cash on Delivery across Pakistan! 🇵🇰\n\n"
            f"📩 Limited batches produced for this season. Tap 'Send Message' or DM us now to secure your bottle!"
        )
        caption = f"{hook}\n\n{desc}"

        tags = [
            f"#{clean_brand}",
            f"#{clean_prod}",
            f"#{clean_vol}Perfume",
            "#LuxuryFragrance",
            "#PerfumesPakistan",
            "#LongLastingScent",
            "#OudLovers",
            "#FragranceCommunity",
            "#ScentOfTheDay",
            "#KarachiPerfumes",
            "#LahoreShopping",
            "#PakistaniBrands",
            "#EauDeParfum"
        ]
        return caption, " ".join(tags), "Royal Velvet"


# Global singleton
caption_generator = DualAICaptionGenerator()

if __name__ == "__main__":
    print("Testing Dual AI Vision Engine...")
    cap, tags, vibe = caption_generator.generate("test_luxury_watch.jpg", platform="instagram")
    print("Caption:\n", cap)
    print("Tags:\n", tags)
    print("Vibe:\n", vibe)
