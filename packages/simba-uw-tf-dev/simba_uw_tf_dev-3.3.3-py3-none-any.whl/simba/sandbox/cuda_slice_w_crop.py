import math
import os
import time
from typing import Optional, Tuple, Union
from simba.mixins.geometry_mixin import GeometryMixin
try:
    from typing import Literal
except:
    from typing_extensions import Literal
try:
    import cupy as cp
    from cupyx.scipy.ndimage import rotate
except:
    import numpy as cp
    from scipy.ndimage import rotate
import numpy as np
from numba import cuda
from simba.mixins.image_mixin import ImageMixin
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (
    check_if_hhmmss_timestamp_is_valid_part_of_video,
    concatenate_videos_in_folder, create_directory, get_fn_ext,
    get_memory_usage_array, get_video_meta_data, read_df,
    read_img_batch_from_video, read_img_batch_from_video_gpu)
from simba.video_processors.async_frame_reader import (AsyncVideoFrameReader,
                                                       get_async_frame_batch)

@cuda.jit(device=True)
def _cuda_is_inside_polygon(x, y, polygon_vertices):
    """
    Checks if the pixel location is inside the polygon.

    :param int x: Pixel x location.
    :param int y: Pixel y location.
    :param np.ndarray polygon_vertices: 2-dimensional array representing the x and y coordinates of the polygon vertices.
    :return: Boolean representing if the x and y are located in the polygon.
    """

    n = len(polygon_vertices)
    p2x, p2y, xints, inside = 0.0, 0.0, 0.0, False
    p1x, p1y = polygon_vertices[0]
    for j in range(n + 1):
        p2x, p2y = polygon_vertices[j % n]
        if ((y > min(p1y, p2y)) and (y <= max(p1y, p2y)) and (x <= max(p1x, p2x))):
            if p1y != p2y:
                xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xints:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside



@cuda.jit(device=True)
def _cuda_is_inside_circle(x, y, circle_x, circle_y, circle_r):
    """
    Device func to check if the pixel location is inside a circle.

    :param int x: Pixel x location.
    :param int y: Pixel y location.
    :param int circle_x: Center of circle x coordinate.
    :param int circle_y: Center of circle y coordinate.
    :param int y: Circle radius.
    :return: Boolean representing if the x and y are located in the circle.
    """

    p = (math.sqrt((x - circle_x) ** 2 + (y - circle_y) ** 2))
    if p <= circle_r:
        return True
    else:
        return False




@cuda.jit()
def _cuda_create_circle_masks(shapes, imgs):
    x, y, n = cuda.grid(3)
    if n < 0 or n > (imgs.shape[0] -1):
        return
    if y < 0 or y > (imgs.shape[1] -1):
        return
    if x < 0 or x > (imgs.shape[2] -1):
        return
    else:
        circle_x, circle_y, circle_r = shapes[n][0], shapes[n][1], shapes[n][2]
        inside = _cuda_is_inside_circle(x, y, circle_x, circle_y, circle_r)
        if not inside:
            imgs[n, y, x] = 0



@cuda.jit()
@cuda.jit()
def _cuda_create_rectangle_masks(shapes, imgs, results, bboxes):
    n, y, x = cuda.grid(3)
    if n >= imgs.shape[0]:
        return

    x_min = bboxes[n, 0]
    y_min = bboxes[n, 1]
    x_max = bboxes[n, 2]
    y_max = bboxes[n, 3]

    max_w = x_max - x_min
    max_h = y_max - y_min

    if x >= max_w or y >= max_h:
        return

    x_input = x + x_min
    y_input = y + y_min

    polygon = shapes[n]

    if _cuda_is_inside_polygon(x_input, y_input, polygon):
        if imgs.ndim == 4:
            for c in range(imgs.shape[3]):
                results[n, y, x, c] = imgs[n, y_input, x_input, c]
        else:
            results[n, y, x] = imgs[n, y_input, x_input]

def get_bboxes(shapes):
    bboxes = []
    for poly in shapes:
        xs = poly[:, 0]
        ys = poly[:, 1]
        x_min = int(np.floor(xs.min()))
        y_min = int(np.floor(ys.min()))
        x_max = int(np.ceil(xs.max()))
        y_max = int(np.ceil(ys.max()))
        bboxes.append([x_min, y_min, x_max, y_max])
    return np.array(bboxes, dtype=np.int32)


def slice_imgs(video_path: Union[str, os.PathLike],
               shapes: np.ndarray,
               batch_size: int = 1000,
               verbose: bool = True,
               save_dir: Optional[Union[str, os.PathLike]] = None):
    """
    Slice frames from a video based on given polygon coordinates and return cropped regions using GPU acceleration.
    """

    THREADS_PER_BLOCK = (16, 8, 8)

    #THREADS_PER_BLOCK = (32, 8, 8)  # (n, y, x) threads per block - adjust y,x for better occupancy
    video_meta_data = get_video_meta_data(video_path=video_path, fps_as_int=False)
    video_meta_data['frame_count'] = shapes.shape[0]
    n, w, h = video_meta_data['frame_count'], video_meta_data['width'], video_meta_data['height']
    is_color = ImageMixin.is_video_color(video=video_path)
    timer, save_temp_dir, results, video_out_path = SimbaTimer(start=True), None, None, None

    # Compute bounding boxes of polygons (one per frame)
    bboxes = get_bboxes(shapes)
    crop_heights = bboxes[:, 3] - bboxes[:, 1]
    crop_widths = bboxes[:, 2] - bboxes[:, 0]

    max_h = int(np.max(crop_heights))
    max_w = int(np.max(crop_widths))

    if save_dir is None:
        if not is_color:
            results = np.zeros((n, max_h, max_w), dtype=np.uint8)
        else:
            results = np.zeros((n, max_h, max_w, 3), dtype=np.uint8)
    else:
        save_temp_dir = os.path.join(save_dir, f'temp_{video_meta_data["video_name"]}')
        create_directory(paths=save_temp_dir, overwrite=True)
        video_out_path = os.path.join(save_dir, f'{video_meta_data["video_name"]}.mp4')

    frm_reader = AsyncVideoFrameReader(video_path=video_path, batch_size=batch_size, verbose=True, max_que_size=2)
    frm_reader.start()

    for batch_cnt in range(frm_reader.batch_cnt):
        start_img_idx, end_img_idx, batch_imgs = get_async_frame_batch(batch_reader=frm_reader, timeout=10)
        if verbose:
            print(f'Processing images {start_img_idx} - {end_img_idx} (of {n}; batch count: {batch_cnt+1}/{frm_reader.batch_cnt})...')

        batch_save_path = os.path.join(save_temp_dir, f'{batch_cnt}.mp4') if save_dir is not None else None

        batch_shapes = shapes[start_img_idx:end_img_idx].astype(np.int32)
        batch_bboxes = bboxes[start_img_idx:end_img_idx]

        x_dev = cuda.to_device(batch_shapes)
        bboxes_dev = cuda.to_device(batch_bboxes)
        batch_img_dev = cuda.to_device(batch_imgs)

        if not is_color:
            batch_results = np.zeros((batch_imgs.shape[0], max_h, max_w), dtype=np.uint8)
        else:
            batch_results = np.zeros((batch_imgs.shape[0], max_h, max_w, 3), dtype=np.uint8)
        batch_results_dev = cuda.to_device(batch_results)
        grid_n = math.ceil(batch_imgs.shape[0] / THREADS_PER_BLOCK[0])
        grid_y = math.ceil(max_h / THREADS_PER_BLOCK[1])
        grid_x = math.ceil(max_w / THREADS_PER_BLOCK[2])
        bpg = (grid_n, grid_y, grid_x)
        if batch_shapes.shape[1] == 3:
            _cuda_create_circle_masks[bpg, THREADS_PER_BLOCK](x_dev, batch_img_dev)
        else:
            _cuda_create_rectangle_masks[bpg, THREADS_PER_BLOCK](x_dev, batch_img_dev, batch_results_dev, bboxes_dev)
        if save_dir is None:
            results[start_img_idx:end_img_idx] = batch_results_dev.copy_to_host()
        else:
            frame_results = batch_results_dev.copy_to_host()
            results = {k: v for k, v in enumerate(frame_results)}
            ImageMixin().img_stack_to_video(imgs=results, fps=video_meta_data['fps'], save_path=batch_save_path, verbose=False)

    frm_reader.kill()
    timer.stop_timer()

    if save_dir:
        concatenate_videos_in_folder(in_folder=save_temp_dir, save_path=video_out_path, remove_splits=True, gpu=True)
        if verbose:
            stdout_success(msg=f'Shapes sliced in video saved at {video_out_path}.', elapsed_time=timer.elapsed_time_str)
        return None
    else:
        if verbose:
            stdout_success(msg='Shapes sliced in video.', elapsed_time=timer.elapsed_time_str)
        return results

video_path = "/mnt/c/troubleshooting/RAT_NOR/project_folder/videos/03152021_NOB_IOT_8.mp4"
data_path = "/mnt/c/troubleshooting/RAT_NOR/project_folder/csv/outlier_corrected_movement_location/03152021_NOB_IOT_8.csv"
save_dir = '/mnt/d/netholabs/yolo_videos/input/mp4_20250606083508'

get_video_meta_data(video_path)

nose_arr = read_df(file_path=data_path, file_type='csv', usecols=['Nose_x', 'Nose_y', 'Tail_base_x', 'Tail_base_y', 'Lat_left_x', 'Lat_left_y', 'Lat_right_x', 'Lat_right_y']).values.reshape(-1, 4, 2).astype(np.int32) ## READ THE BODY-PART THAT DEFINES THE HULL AND CONVERT TO ARRAY
polygons = GeometryMixin().multiframe_bodyparts_to_circle(data=nose_arr, parallel_offset=60) ## CONVERT THE BODY-PART TO POLYGONS WITH A LITTLE BUFFER
polygons = GeometryMixin().multiframe_minimum_rotated_rectangle(shapes=polygons) # CONVERT THE POLYGONS TO RECTANGLES (I.E., WITH 4 UNIQUE POINTS).
polygon_lst = [] # GET THE POINTS OF THE RECTANGLES
for i in polygons: polygon_lst.append(np.array(i.exterior.coords))
polygons = np.stack(polygon_lst, axis=0)
sliced_imgs = slice_imgs(video_path=video_path, shapes=polygons, batch_size=500, save_dir=save_dir) #SLICE THE RECTANGLES IN THE VIDEO.