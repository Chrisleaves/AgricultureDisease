import type { SelectedImage } from "@/types/diagnosis";

export const MAX_IMAGE_SIZE = 10 * 1024 * 1024;
const SUPPORTED_TYPES = ["jpg", "jpeg", "png", "webp"];

export class ImageValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ImageValidationError";
  }
}

function getImageInfo(path: string): Promise<UniApp.GetImageInfoSuccessData> {
  return new Promise((resolve, reject) => {
    uni.getImageInfo({
      src: path,
      success: resolve,
      fail: () => reject(new ImageValidationError("图片无法读取，请重新选择")),
    });
  });
}

export async function validateSelectedImage(path: string, size: number): Promise<SelectedImage> {
  if (size > MAX_IMAGE_SIZE) throw new ImageValidationError("单张图片不能超过 10 MB");
  if (size <= 0) throw new ImageValidationError("图片内容为空，请重新选择");

  const info = await getImageInfo(path);
  const type = info.type?.toLowerCase();
  if (type && !SUPPORTED_TYPES.includes(type)) {
    throw new ImageValidationError("仅支持 JPG、PNG 或 WEBP 图片");
  }

  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    path,
    size,
    width: info.width,
    height: info.height,
    type,
  };
}

export function formatFileSize(bytes: number): string {
  return bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.ceil(bytes / 1024)} KB`;
}

export function persistSelectedImage(path: string): Promise<string> {
  if (!path) return Promise.resolve("");
  return new Promise((resolve) => {
    uni.saveFile({
      tempFilePath: path,
      success: (response) => resolve(response.savedFilePath),
      fail: () => resolve(path),
    });
  });
}
