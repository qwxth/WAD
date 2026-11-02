import type { SyntheticEvent } from 'react';
import { DEFAULT_IMAGE, DEFAULT_VIDEO } from '../constants';

interface PatternMediaProps {
  imageUrl: string | null;
  videoUrl: string | null;
  title: string;
  showVideo?: boolean;
  height?: number;
}

function fallbackToDefault(e: SyntheticEvent<HTMLImageElement>) {
  const img = e.currentTarget;
  img.onerror = null; // защита от зацикливания
  img.src = DEFAULT_IMAGE;
}

export default function PatternMedia({ imageUrl, videoUrl, title, showVideo = true, height = 200 }: PatternMediaProps) {
  return (
    <>
      <img
        src={imageUrl || DEFAULT_IMAGE}
        alt={title}
        onError={fallbackToDefault}
        className="w-100"
        style={{ height, objectFit: 'cover' }}
      />
      {showVideo && (
        <video
          src={videoUrl || DEFAULT_VIDEO}
          controls
          preload="metadata"
          className="w-100"
          style={{ height, objectFit: 'cover', background: '#000' }}
        />
      )}
    </>
  );
}
