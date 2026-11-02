import defaultImage from './assets/default-pattern.jpg';
import defaultVideo from './assets/default-pattern.mp4';
import type { PatternFilterValues } from './types';

export const DEFAULT_IMAGE: string = defaultImage;
export const DEFAULT_VIDEO: string = defaultVideo;

export const MAX_EXPECTED = 120_000_000;

export const EMPTY_FILTER: PatternFilterValues = {
  search: '',
  maxExpected: MAX_EXPECTED,
  minRps: '',
  maxRps: '',
};
