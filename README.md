# GroupForHDR

Automatically group real estate bracketed photos by shared EXIF metadata — preparing them for HDR blending via ML models.

## 📸 Overview

Real estate photographers often capture multiple photos of the same angle at different exposure levels ("brackets") to later merge them into one HDR image.

This script takes a folder containing photo shoots (each in its own subfolder), extracts EXIF metadata, and groups the bracketed photos that represent the same angle.

## 🔧 How It Works

- Groups are formed based on:
  - Matching focal length, aperture, image dimensions
  - Timestamps within a small time window (e.g. 15 seconds)
  - Similar exposure compensation (e.g. +0, -2, +2)
- Handles edge cases like:
  - False positives due to same camera settings
  - Exposure jumps indicating different scenes
- Outputs a dictionary of groupings:
  ```python
  {
      1: ['shoot_1/IMG_001.jpg', 'shoot_1/IMG_002.jpg'],
      2: ['shoot_1/IMG_003.jpg', 'shoot_1/IMG_004.jpg', 'shoot_1/IMG_005.jpg'],
      ...
  }
