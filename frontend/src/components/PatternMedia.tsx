import { DEFAULT_IMAGE, DEFAULT_VIDEO } from '../constants';

interface PatternMediaProps {
  imageUrl: string | null;
  videoUrl: string | null;
  title: string;
  showVideo?: boolean;
  height?: number;
}

function fallbackToDefault(element: HTMLImageElement | HTMLVideoElement, fallback: string) {
  if (element.getAttribute('src') !== fallback) {
    element.src = fallback;
  }
}

export default function PatternMedia({ imageUrl, videoUrl, title, showVideo = true, height = 200 }: PatternMediaProps) {
  return (
    <>
      <img
        src={imageUrl || DEFAULT_IMAGE}
        alt={title}
        onError={(event) => fallbackToDefault(event.currentTarget, DEFAULT_IMAGE)}
        className="w-100"
        style={{ height, objectFit: 'cover' }}
      />
      {showVideo && (
        <video
          src={videoUrl || DEFAULT_VIDEO}
          onError={(event) => fallbackToDefault(event.currentTarget, DEFAULT_VIDEO)}
          controls
          preload="metadata"
          className="w-100"
          style={{ height, objectFit: 'cover', background: '#000' }}
        />
      )}
    </>
  );
}
