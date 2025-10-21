import random
import math
import json
import base64
from typing import List, Dict, Tuple, Optional
import numpy as np

class PerlinNoise:
    def __init__(self, seed: Optional[int] = None):
        self.rand_eng = random.Random(seed)
        self.gradients = {}

    def _get_gradient(self, ix: int) -> float:
        if ix not in self.gradients:
            angle = self.rand_eng.uniform(0, 2 * math.pi)
            self.gradients[ix] = (
                self.rand_eng.uniform(-1.0, 1.0) * 0.5
            )
        return self.gradients[ix]

    def _smooth_noise(self, x: int) -> float:
        x = int(x)
        x = (x << 13) ^ x
        x = (x * (x * x * 15731 + 789221) + 1376312589) & 0x7FFFFFFF
        return 1.0 - (x / 1073741824.0)

    def _cosine_interpolate(self, a: float, b: float, x: float) -> float:
        ft = x * math.pi
        f = (1.0 - math.cos(ft)) * 0.5
        return a * (1.0 - f) + b * f

    def _interpolated_noise(self, x: float) -> float:
        integer_x = int(math.floor(x))
        fractional_x = x - integer_x
        v1 = self._smooth_noise(integer_x)
        v2 = self._smooth_noise(integer_x + 1)
        return self._cosine_interpolate(v1, v2, fractional_x)

    def noise(self, x: float, persistence: float = 0.5, octaves: int = 3) -> float:
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        for _ in range(octaves):
            total += self._interpolated_noise(x * frequency) * amplitude
            max_value += amplitude
            frequency *= 2
            amplitude *= persistence
        if max_value == 0:
            return 0
        return clamp(total, -0.8, 0.8)

perlin = PerlinNoise()


def clamp(x: float, lowerlimit: float, upperlimit: float) -> float:
    return max(lowerlimit, min(x, upperlimit))


def point_subtract(p1: Dict[str, float], p2: Dict[str, float]) -> Dict[str, float]:
    return {"x": p1["x"] - p2["x"], "y": p1["y"] - p2["y"]}


def point_add(p1: Dict[str, float], p2: Dict[str, float]) -> Dict[str, float]:
    return {"x": p1["x"] + p2["x"], "y": p1["y"] + p2["y"]}


def point_scale(p: Dict[str, float], s: float) -> Dict[str, float]:
    return {"x": p["x"] * s, "y": p["y"] * s}


def magnitude(p: Dict[str, float]) -> float:
    return math.sqrt(p["x"] ** 2 + p["y"] ** 2)


def get_bezier_point(t: float, points: List[Dict[str, float]]) -> Dict[str, float]:
    n = len(points) - 1
    if n < 0:
        raise ValueError("Need at least one point for Bézier curve")
    if n == 0:
        return points[0]

    if n == 1:
        p0, p1 = points
        x = (1 - t) * p0["x"] + t * p1["x"]
        y = (1 - t) * p0["y"] + t * p1["y"]
        return {"x": x, "y": y}
    if n == 2:
        p0, p1, p2 = points
        x = (1 - t) ** 2 * p0["x"] + 2 * (1 - t) * t * p1["x"] + t**2 * p2["x"]
        y = (1 - t) ** 2 * p0["y"] + 2 * (1 - t) * t * p1["y"] + t**2 * p2["y"]
        return {"x": x, "y": y}
    if n == 3:
        p0, p1, p2, p3 = points
        x = (
            (1 - t) ** 3 * p0["x"]
            + 3 * (1 - t) ** 2 * t * p1["x"]
            + 3 * (1 - t) * t**2 * p2["x"]
            + t**3 * p3["x"]
        )
        y = (
            (1 - t) ** 3 * p0["y"]
            + 3 * (1 - t) ** 2 * t * p1["y"]
            + 3 * (1 - t) * t**2 * p2["y"]
            + t**3 * p3["y"]
        )
        return {"x": x, "y": y}
    
    x, y = 0.0, 0.0
    for i in range(n + 1):
        bernstein = math.comb(n, i) * (1 - t) ** (n - i) * t**i
        x += points[i]["x"] * bernstein
        y += points[i]["y"] * bernstein
    return {"x": x, "y": y}


def get_bezier_derivative(t: float, points: List[Dict[str, float]]) -> Dict[str, float]:
    n = len(points) - 1
    if n < 1:
        return {"x": 0.0, "y": 0.0}
    
    derivative_points = []
    for i in range(n):
        dp = point_subtract(points[i + 1], points[i])
        derivative_points.append(point_scale(dp, n))

    return get_bezier_point(t, derivative_points)


def approx_arc_length(points: List[Dict[str, float]], n_segments: int = 50) -> float:
    length = 0.0
    prev_point = get_bezier_point(0, points)
    for i in range(1, n_segments + 1):
        t = i / n_segments
        current_point = get_bezier_point(t, points)
        length += magnitude(point_subtract(current_point, prev_point))
        prev_point = current_point
    return length

def log_normal_velocity_profile(
    t: float, duration: float, mu: float, sigma: float
) -> float:
    if t <= 0 or duration <= 0:
        return 0
    
    t = min(t, duration)

    try:
        log_t = math.log(t)
    except ValueError:
        return 0  # Avoid log(0)

    exponent = -((log_t - mu) ** 2) / (2 * sigma**2)
    denominator = t * sigma * math.sqrt(2 * math.pi)

    if denominator == 0:
        return 0
    
    pdf_val = (1.0 / denominator) * math.exp(exponent)
    return pdf_val


class EnhancedDataGenerator:
    def __init__(self):
        self.dPoints: List[Tuple[int, int]] = []
        self.timestamp: int = 0
        self.perlin_noise = PerlinNoise()

        self.TARGET_DT: int = 15
        
        self.BASE_DURATION_FACTOR: float = 25.0
        
        self.DISTANCE_POWER: float = 0.45
        
        self.MIN_STROKE_DURATION: int = 80
        self.MAX_STROKE_DURATION: int = 1500
        
        self.MIN_PAUSE_DURATION: int = 40
        self.MAX_PAUSE_DURATION: int = 250
        
        self.VELOCITY_SIGMA: float = 0.45
        self.PEAK_TIME_RATIO: float = (
            0.25
        )
        
        self.CONTROL_POINT_DEVIATION_FACTOR: float = 0.35
        
        self.PERLIN_NOISE_SCALE: float = 0.8
        self.PERLIN_NOISE_FREQ: float = (
            0.05
        )

    def random_value(self, min_value: float, max_value: float) -> float:
        return random.uniform(min_value, max_value)

    def generate_d_points(
        self, num_points_range: Tuple[int, int] = (3, 6)
    ) -> List[Tuple[int, int]]:
        self.dPoints = []
        num_points = int(self.random_value(num_points_range[0], num_points_range[1]))
        
        last_x, last_y = 700, 200
        min_dist_sq = 150**2
        for i in range(num_points):
            while True:
                x = int(self.random_value(700, 1320))
                y = int(self.random_value(300, 700))
                if i == 0 or (x - last_x) ** 2 + (y - last_y) ** 2 > min_dist_sq:
                    self.dPoints.append((x, y))
                    last_x, last_y = x, y
                    break
        return self.dPoints

    def _calculate_stroke_duration(self, distance: float) -> int:
        if distance < 1:
            return self.MIN_STROKE_DURATION

        duration = self.BASE_DURATION_FACTOR * (distance**self.DISTANCE_POWER)
        
        duration *= self.random_value(0.85, 1.15)

        return int(clamp(duration, self.MIN_STROKE_DURATION, self.MAX_STROKE_DURATION))

    def _generate_control_points(
        self, start_pt: Dict[str, float], end_pt: Dict[str, float]
    ) -> List[Dict[str, float]]:

        # Using Cubic Bézier for potentially smoother curves
        dist_vec = point_subtract(end_pt, start_pt)
        dist = magnitude(dist_vec)

        if dist < 1e-6:  # Avoid division by zero if points are identical
            return [start_pt, start_pt, end_pt, end_pt]

        # Normal vector (perpendicular)
        norm_vec = {"x": -dist_vec["y"] / dist, "y": dist_vec["x"] / dist}

        # Midpoint
        mid_pt = point_add(start_pt, point_scale(dist_vec, 0.5))

        # Calculate deviation magnitude
        deviation = (
            dist * self.CONTROL_POINT_DEVIATION_FACTOR * self.random_value(0.5, 1.5)
        )

        # Randomly flip direction of deviation
        if random.random() < 0.5:
            deviation *= -1

        # Add Perlin noise influence to deviation
        noise_val = self.perlin_noise.noise(
            mid_pt["x"] * 0.01 + mid_pt["y"] * 0.02
        )  # Use coords for noise seed
        deviation += dist * 0.1 * noise_val  # Smaller extra deviation from noise

        # Control point 1: Offset from point ~1/3 along the line
        cp1_base = point_add(
            start_pt, point_scale(dist_vec, self.random_value(0.25, 0.4))
        )
        cp1_offset = point_scale(
            norm_vec, deviation * self.random_value(0.8, 1.2)
        )  # Slight variation
        cp1 = point_add(cp1_base, cp1_offset)

        # Control point 2: Offset from point ~2/3 along the line (opposite side?)
        cp2_base = point_add(
            start_pt, point_scale(dist_vec, self.random_value(0.6, 0.75))
        )
        # Often good to have cp2 deviation related but maybe different magnitude/direction
        cp2_dev_factor = self.random_value(
            -0.6, -1.1
        )  # Try offsetting other way usually
        cp2_offset = point_scale(norm_vec, deviation * cp2_dev_factor)
        cp2 = point_add(cp2_base, cp2_offset)

        # Clamp control points to reasonable bounds if necessary (e.g., screen limits)
        # cp1['x'] = clamp(cp1['x'], 0, 1920) ... etc.

        return [start_pt, cp1, cp2, end_pt]

    def generate_stroke(
        self, control_points: List[Dict[str, float]], start_time: int
    ) -> Tuple[List[Dict[str, int]], int]:
        """
        Generates the points for a single stroke (Bézier segment) using a kinematic model.
        Returns the list of points and the end timestamp.
        """
        path: List[Dict[str, int]] = []
        curve_len = approx_arc_length(control_points)
        duration = self._calculate_stroke_duration(curve_len)

        # If duration or length is negligible, just add end point
        if duration < self.TARGET_DT or curve_len < 1.0:
            end_pt = control_points[-1]
            final_time = start_time + duration
            path.append(
                {
                    "timestamp": int(final_time),
                    "type": 0,
                    "x": int(end_pt["x"]),
                    "y": int(end_pt["y"]),
                }
            )
            return path, int(final_time)

        # Calculate log-normal parameters based on duration
        # Mu influences the peak time. Peak time = exp(mu).
        # Let peak time be PEAK_TIME_RATIO * duration.
        # Clamp peak time to avoid issues near t=0 or t=duration
        peak_time = clamp(
            duration * self.PEAK_TIME_RATIO, self.TARGET_DT, duration - self.TARGET_DT
        )
        mu = math.log(peak_time)
        sigma = self.VELOCITY_SIGMA

        # Integrate the velocity profile numerically to scale it correctly
        # We want Integral(v(t) dt) from 0 to duration = curve_len
        time_steps_for_integral = np.linspace(
            0, duration, 100
        )  # 100 steps for integration
        dt_integral = duration / 99.0
        unscaled_velocity_integral = 0.0
        for t_step in time_steps_for_integral:
            unscaled_velocity_integral += (
                log_normal_velocity_profile(t_step, duration, mu, sigma) * dt_integral
            )

        if unscaled_velocity_integral < 1e-6:
            # Avoid division by zero if profile is flat (e.g., duration too short)
            velocity_scale_factor = 1.0  # Effectively constant speed
        else:
            velocity_scale_factor = curve_len / unscaled_velocity_integral

        # Simulate the movement over time
        current_time = 0.0
        current_u = 0.0  # Parameter along Bezier curve [0, 1]
        last_added_point_time = -self.TARGET_DT  # Ensure first point is added

        # Add the starting point
        start_pt = control_points[0]
        path.append(
            {
                "timestamp": int(start_time),
                "type": 0,
                "x": int(start_pt["x"]),
                "y": int(start_pt["y"]),
            }
        )

        noise_offset_x = 0.0
        noise_offset_y = 0.0

        while current_u < 1.0 and current_time < duration:
            # Calculate target speed at this time
            inst_velocity = log_normal_velocity_profile(
                current_time + 1e-6, duration, mu, sigma
            )  # Add epsilon to avoid log(0)
            scaled_velocity = inst_velocity * velocity_scale_factor

            # Calculate derivative (speed vector w.r.t 'u') at current position on curve
            deriv_vec = get_bezier_derivative(current_u, control_points)
            speed_wrt_u = magnitude(deriv_vec)

            # Calculate how much 'u' should advance in TARGET_DT
            # ds = velocity * dt --> Arc length to travel
            # ds ≈ speed_wrt_u * du --> Relate arc length to parameter change
            # du ≈ ds / speed_wrt_u = (velocity * dt) / speed_wrt_u
            if speed_wrt_u < 1e-3:  # Avoid division by zero if derivative is tiny
                du = 0.0
                # If speed is also tiny, just advance time. If speed is high, means curve is sharp, advance u more?
                # This case usually happens only at u=0 or u=1 if start/end points are repeated.
                # Or if control points make a cusp. For safety, just step forward slightly in u.
                if scaled_velocity > 1e-3:
                    du = 0.01  # Arbitrary small step
            else:
                du = (scaled_velocity * self.TARGET_DT) / speed_wrt_u

            # Update u, ensuring it doesn't overshoot 1.0
            current_u = min(current_u + du, 1.0)
            current_time += self.TARGET_DT

            # Add point to path if enough time has passed since last added point
            # This check avoids adding points too densely if dt is very small
            if (
                current_time - last_added_point_time >= self.TARGET_DT * 0.9
            ):  # Allow slight tolerance

                pos = get_bezier_point(current_u, control_points)

                # Add Perlin noise perturbation
                # Noise depends on time and position to make it less repetitive
                noise_t = current_time * self.PERLIN_NOISE_FREQ * 0.01
                noise_x_coord = pos["x"] * self.PERLIN_NOISE_FREQ * 0.001
                noise_y_coord = pos["y"] * self.PERLIN_NOISE_FREQ * 0.001

                # Use two independent noise sources for x and y
                noise_offset_x = (
                    self.perlin_noise.noise(noise_t + noise_x_coord, octaves=2)
                    * self.PERLIN_NOISE_SCALE
                )
                noise_offset_y = (
                    self.perlin_noise.noise(noise_t + noise_y_coord + 42.0, octaves=2)
                    * self.PERLIN_NOISE_SCALE
                )  # Offset seed for y

                final_x = pos["x"] + noise_offset_x
                final_y = pos["y"] + noise_offset_y

                # Append point, ensuring timestamp increases
                actual_time = int(start_time + current_time)
                # Ensure timestamp doesn't decrease due to rounding
                if not path or actual_time > path[-1]["timestamp"]:
                    path.append(
                        {
                            "timestamp": actual_time,
                            "type": 0,
                            "x": int(final_x),
                            "y": int(final_y),
                        }
                    )
                    last_added_point_time = current_time
                elif len(path) > 0:  # Update last point if time hasn't advanced enough
                    path[-1]["x"] = int(final_x)
                    path[-1]["y"] = int(final_y)

            # Safety break if u isn't advancing
            if du < 1e-6 and speed_wrt_u < 1e-3:
                if current_u < 0.99:  # Only break if not already near the end
                    # print(f"Warning: Stuck at u={current_u:.4f}, t={current_time:.1f}. Breaking stroke.")
                    break
                else:  # If near end, just force completion
                    current_u = 1.0

        # Ensure the very last point is exactly the endpoint and at the correct time
        end_pt = control_points[-1]
        final_time = start_time + duration
        # Only add if significantly different from last point or if path is empty
        if (
            not path
            or abs(path[-1]["x"] - int(end_pt["x"])) > 1
            or abs(path[-1]["y"] - int(end_pt["y"])) > 1
            or final_time > path[-1]["timestamp"] + 5
        ):
            # Update last point's time if needed, or add new point
            if path and final_time <= path[-1]["timestamp"]:
                final_time = (
                    path[-1]["timestamp"] + self.TARGET_DT // 2
                )  # Ensure time increases

            path.append(
                {
                    "timestamp": int(final_time),
                    "type": 0,
                    "x": int(end_pt["x"]),
                    "y": int(end_pt["y"]),
                }
            )
            return path, int(final_time)
        else:  # Otherwise, update the last point to be exactly the end point/time
            path[-1]["x"] = int(end_pt["x"])
            path[-1]["y"] = int(end_pt["y"])
            path[-1]["timestamp"] = int(final_time)
            return path, int(final_time)

    def generate_motion_data(self) -> List[Dict[str, int]]:
        """Generates the full motion path by connecting dPoints with strokes."""
        self.timestamp = int(self.random_value(0, 70))  # Initial random delay
        motion_curve_data: List[Dict[str, int]] = []
        current_pos = {"x": 700.0, "y": 200.0}  # Initial position (float for precision)

        if not self.dPoints:
            self.generate_d_points()

        for i in range(len(self.dPoints)):
            start_pt = current_pos
            end_pt = {"x": float(self.dPoints[i][0]), "y": float(self.dPoints[i][1])}

            # Generate control points for the cubic Bézier curve
            control_points = self._generate_control_points(start_pt, end_pt)

            # Generate the stroke points based on kinematic model
            stroke_path, self.timestamp = self.generate_stroke(
                control_points, self.timestamp
            )

            # Add generated points, avoiding duplicates if start/end are close
            if stroke_path:
                # Ensure first point isn't identical to previous segment's last point
                if (
                    motion_curve_data
                    and stroke_path[0]["x"] == motion_curve_data[-1]["x"]
                    and stroke_path[0]["y"] == motion_curve_data[-1]["y"]
                    and stroke_path[0]["timestamp"]
                    <= motion_curve_data[-1]["timestamp"]
                ):
                    motion_curve_data.extend(stroke_path[1:])
                else:
                    motion_curve_data.extend(stroke_path)

            # Update current position for the next segment
            current_pos = end_pt

            # Add a pause between strokes
            if i < len(self.dPoints) - 1:  # Don't pause after the last stroke
                pause = int(
                    self.random_value(self.MIN_PAUSE_DURATION, self.MAX_PAUSE_DURATION)
                )
                self.timestamp += pause
                # Optional: Add a stationary point during the pause?
                # motion_curve_data.append({
                #     "timestamp": self.timestamp,
                #     "type": 0,
                #     "x": int(current_pos['x']),
                #     "y": int(current_pos['y'])
                # })

        # Clean up: Remove consecutive points with identical x, y, and type
        cleaned_data = []
        if motion_curve_data:
            cleaned_data.append(motion_curve_data[0])
            for i in range(1, len(motion_curve_data)):
                prev = cleaned_data[-1]
                curr = motion_curve_data[i]
                # Keep if position changed OR timestamp is significantly different
                if (
                    curr["x"] != prev["x"]
                    or curr["y"] != prev["y"]
                    or curr["timestamp"] > prev["timestamp"] + 5
                ):  # Keep if time moved significantly
                    # If position is same but time moved, update time of prev point instead? No, add new.
                    # Ensure time increases monotonically
                    if curr["timestamp"] <= prev["timestamp"]:
                        curr["timestamp"] = prev["timestamp"] + 1  # Force increase

                    cleaned_data.append(curr)
                # else: # If identical pos and very close time, just update timestamp of previous?
                # prev['timestamp'] = curr['timestamp'] # This might merge pauses - careful

        return cleaned_data

    def generate_key_data(self) -> str:
        """Generates keyboard event data (unchanged from original)."""
        key_timestamp = int(self.random_value(0, 70))
        key_curve_data: List[Dict[str, int]] = []

        for _ in range(int(self.random_value(5, 15))):  # Reduced number for realism
            key_timestamp += int(self.random_value(800, 4000))  # Adjusted timing
            key_curve_data.append(
                {
                    "timestamp": key_timestamp,
                    "type": int(self.random_value(1, 3)),  # 1=down, 2=up? Assuming this
                    "extra": 0,  # Keycode would go here usually
                }
            )

        return ";".join(
            f"{p['timestamp']},{p['type']},{p['extra']}" for p in key_curve_data
        )

    def generate(self) -> str:
        """Generates the complete base64 encoded data string."""
        self.generate_d_points()
        motion_data = self.generate_motion_data()
        key_data = self.generate_key_data()

        # Filter motion data - remove points too close in time if needed?
        # The cleaning step in generate_motion_data helps

        data = {
            "mbio": motion_data,
            "tbio": "",
            "kbio": "",
        }  # Assuming tbio is unused

        data_json = json.dumps(data, separators=(",", ":"))
        return base64.b64encode(data_json.encode("utf-8")).decode("utf-8")
