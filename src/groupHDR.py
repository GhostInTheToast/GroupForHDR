import os
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image
import re
from decimal import Decimal


# To whom it may concern:
# I'm using a type of similar algorithm I learned while leetcoding: group anagrams key grouping :)


# def hist_similarity(img1_path, img2_path, size=(128, 128)):
#     try:
#         img1 = Image.open(img1_path).convert("RGB").resize(size)
#         img2 = Image.open(img2_path).convert("RGB").resize(size)
#         hist1 = img1.histogram()
#         hist2 = img2.histogram()
#         sim = sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r))
#                   for l, r in zip(hist1, hist2)) / len(hist1)
#         return sim
#     except Exception as e:
#         print(f"⚠️ Histogram comparison error: {e}")
#         return 0


def get_exif_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        data = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            data[tag] = value
        data['ImageWidth'], data['ImageHeight'] = image.size

        return data

    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None


def parse_exif_datetime(date_str):
    try:
        if '-' in date_str:
            date_str = date_str.split('-')[0]

        return datetime.strptime(date_str.strip(), "%Y:%m:%d %H:%M:%S")

    except Exception:
        return None


def extract_number(filename):
    match = re.search(r'(\d+)', filename)

    return int(match.group(1)) if match else -1


def group_images_by_fuzzy_metadata(folder_path, time_tolerance=15, dimension_tolerance=20, exposure_jump_limit=2.5):
    images = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
    image_data = []

    for image in sorted(images):
        full_path = os.path.join(folder_path, image)
        exif = get_exif_metadata(full_path)
        if not exif:
            continue

        dt_str = exif.get("DateTimeOriginal")
        dt = parse_exif_datetime(dt_str) if dt_str else None
        if not dt:
            continue

        try:
            focal = float(exif.get("FocalLength", 0))
            aperture = float(exif.get("FNumber", 0))
            exposure_comp = float(
                exif.get("ExposureCompensation") or
                exif.get("ExposureBiasValue") or
                0
            )

        except Exception as e:
            print(f"⚠️ Error parsing focal/aperture/exposure_comp for {image}: {e}")
            continue

        try:
            width = int(exif.get("ImageWidth", 0))
            height = int(exif.get("ImageHeight", 0))

        except Exception as e:
            print(f"⚠️ Error parsing dimensions for {image}: {e}")
            continue

        print(f"🔍 {image}")
        print(f"  DateTimeOriginal: {dt}")
        print(f"  Focal: {focal}")
        print(f"  Aperture: {aperture}")
        print(f"  ExposureComp: {exposure_comp}")
        print(f"  Width x Height: {width} x {height}")

        image_data.append({
            "path": full_path,
            "datetime": dt,
            "focal": focal,
            "aperture": aperture,
            "exposure_comp": exposure_comp,
            "width": width,
            "height": height
        })

    image_data.sort(key=lambda x: x["datetime"])

    groups = []
    current_group = []

    for img in image_data:
        if not current_group:
            current_group.append(img)
        else:
            last = current_group[-1]
            time_diff = abs((img["datetime"] - last["datetime"]).total_seconds())
            exposure_diff = abs(img["exposure_comp"] - last["exposure_comp"])

            print("\n🧪 Comparing:")
            print(f"- Current: {img['path']}")
            print(f"- Last in group:   {last['path']}")
            print(f"  Time diff: {time_diff:.2f}s")
            print(f"  Focal:    {img['focal']} vs {last['focal']}")
            print(f"  Aperture: {img['aperture']} vs {last['aperture']}")
            print(f"  Width:    {img['width']} vs {last['width']}")
            print(f"  Height:   {img['height']} vs {last['height']}")
            print(f"  ExposureComp: {img['exposure_comp']} vs {last['exposure_comp']}")

            same_meta = (
                abs(img["focal"] - last["focal"]) <= 0.5 and
                abs(img["aperture"] - last["aperture"]) <= 0.2 and
                abs(img["width"] - last["width"]) <= dimension_tolerance and
                abs(img["height"] - last["height"]) <= dimension_tolerance
            )

            exposure_jump_conflict = exposure_diff > exposure_jump_limit and time_diff > 5

            if time_diff <= time_tolerance and same_meta and not exposure_jump_conflict:
                current_group.append(img)
            else:
                if exposure_jump_conflict:
                    print("⛔ Not grouped: large exposure jump + time gap.")
                elif time_diff > time_tolerance:
                    print("⛔ Not grouped: time difference too large.")
                elif not same_meta:
                    print("⛔ Not grouped: metadata mismatch.")
                groups.append([x["path"] for x in current_group])
                current_group = [img]

    if current_group:
        groups.append([x["path"] for x in current_group])

    return {i + 1: group for i, group in enumerate(groups)}


def display_groupings(groupings, max_rows=5):
    for group_num, image_paths in list(groupings.items())[:max_rows]:
        fig, axes = plt.subplots(1, len(image_paths), figsize=(15, 4))
        if len(image_paths) == 1:
            axes = [axes]
        for ax, img_path in zip(axes, image_paths):
            img = Image.open(img_path)
            ax.imshow(img)
            ax.set_title(os.path.basename(img_path), fontsize=8)
            ax.axis('off')
        plt.suptitle(f"Group {group_num}")
        plt.tight_layout()
        plt.show()





if __name__ == "__main__":
    parent_folder = "../shoots"  # Relative path from src/

    for shoot_name in sorted(os.listdir(parent_folder)):
        shoot_path = os.path.join(parent_folder, shoot_name)
        if os.path.isdir(shoot_path):
            print(f"\n📸 Processing: {shoot_name}")
            groupings = group_images_by_fuzzy_metadata(shoot_path)
            display_groupings(groupings)
