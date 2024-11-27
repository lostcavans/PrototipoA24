import * as tf from '@tensorflow/tfjs'

export interface Box {
  top: number
  left: number
  bottom: number
  right: number
  width: number
  height: number
  scores: number
  classes: string
}

type yolo = ($img: HTMLImageElement) => Promise<Box[]> 

export declare function yolov3 (
  { modelUrl, anchors }? :
  { modelUrl?: string, anchors?: number[] }
): Promise<yolo>

export declare function yolov3Tiny (
  { modelUrl, anchors }? :
  { modelUrl?: string, anchors?: number[] }
): Promise<yolo>
