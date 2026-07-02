"""
movement_system.py

A simple 2D character movement system suitable for prototypes or as a starting point
for a small game. Features:
- Vector2 utility
- Character class with position, velocity, acceleration
- Input handling helpers (WASD / arrow style)
- Friction, max speed, acceleration
- Basic axis-aligned rectangle collision helper
- Example simulation in __main__ demonstrating movement updates

This file is framework-agnostic (no pygame dependency) and can be integrated into
an engine loop by calling Character.update(dt) each frame and using apply_input()
or apply_force() to influence movement.
"""
from dataclasses import dataclass
import math
from typing import Tuple, Optional


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2":
        return self.__mul__(scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vector2":
        l = self.length()
        if l == 0:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)

    def clamp(self, max_length: float) -> "Vector2":
        l = self.length()
        if l <= max_length:
            return Vector2(self.x, self.y)
        return self.normalized() * max_length


class Character:
    """A simple 2D character with physics-style movement.

    Usage:
        c = Character()
        c.apply_input(x_axis, y_axis)  # values between -1 and 1
        c.update(dt)
    """

    def __init__(
        self,
        position: Optional[Vector2] = None,
        max_speed: float = 250.0,  # units per second
        accel: float = 1000.0,  # units per second^2
        friction: float = 600.0,  # units per second^2 when no input
    ):
        self.position = position or Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = max_speed
        self.accel = accel
        self.friction = friction

        # Optional bounding box for simple AABB collision: (w, h)
        self.size: Optional[Tuple[float, float]] = None

    def apply_input(self, x_axis: float, y_axis: float) -> None:
        """Apply player input as normalized axis values (-1..1).

        This sets acceleration towards the input direction. Use update(dt) to
        integrate velocity and position.
        """
        # Clamp inputs to range
        x = max(-1.0, min(1.0, x_axis))
        y = max(-1.0, min(1.0, y_axis))

        direction = Vector2(x, y)
        if direction.length() > 0:
            # Prefer consistent top speed in diagonals by normalizing input
            direction = direction.normalized()
            self.acceleration = direction * self.accel
        else:
            # No input -> remove acceleration and let friction slow the character
            self.acceleration = Vector2(0, 0)

    def apply_force(self, force: Vector2) -> None:
        """Apply an external force (units/s^2) to the character's acceleration.
        Useful for impulses, knockbacks, or gravity-like effects.
        """
        self.acceleration = Vector2(self.acceleration.x + force.x, self.acceleration.y + force.y)

    def update(self, dt: float) -> None:
        """Integrate motion over dt seconds.

        - Updates velocity from acceleration
        - Applies friction when there's no input acceleration
        - Clamps to max_speed
        - Updates position
        """
        if dt <= 0:
            return

        # Integrate velocity: v = v + a * dt
        self.velocity = Vector2(self.velocity.x + self.acceleration.x * dt, self.velocity.y + self.acceleration.y * dt)

        # If no acceleration, apply friction to reduce velocity toward zero
        if self.acceleration.length() == 0:
            speed = self.velocity.length()
            if speed > 0:
                decel_amount = self.friction * dt
                new_speed = max(0.0, speed - decel_amount)
                if new_speed == 0:
                    self.velocity = Vector2(0, 0)
                else:
                    self.velocity = self.velocity.normalized() * new_speed

        # Clamp speed
        self.velocity = self.velocity.clamp(self.max_speed)

        # Update position: p = p + v * dt
        self.position = Vector2(self.position.x + self.velocity.x * dt, self.position.y + self.velocity.y * dt)

    def set_size(self, width: float, height: float) -> None:
        self.size = (width, height)

    def aabb(self) -> Optional[Tuple[float, float, float, float]]:
        """Returns AABB as (left, top, right, bottom) if size is set, otherwise None."""
        if self.size is None:
            return None
        w, h = self.size
        left = self.position.x - w / 2
        top = self.position.y - h / 2
        right = left + w
        bottom = top + h
        return (left, top, right, bottom)


def aabb_collide(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> bool:
    """Check AABB collision between rectangles formatted as (l, t, r, b)."""
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


# Example usage: a simple headless simulation loop
if __name__ == "__main__":
    import time

    c = Character(position=Vector2(0, 0), max_speed=200, accel=800, friction=600)
    c.set_size(32, 32)

    # Simulate pressing right for 0.6s, then no input for 0.8s
    timeline = [
        (0.6, (1.0, 0.0)),  # move right
        (0.8, (0.0, 0.0)),  # stop input, friction slows
    ]

    print("Starting simulation")
    for duration, input_axis in timeline:
        elapsed = 0.0
        while elapsed < duration:
            dt = 1.0 / 60.0
            c.apply_input(*input_axis)
            c.update(dt)
            elapsed += dt
            # Print every 0.1s
            if int(elapsed * 10) != int((elapsed - dt) * 10):
                print(f"t={elapsed:.2f}s pos=({c.position.x:.2f}, {c.position.y:.2f}) vel=({c.velocity.x:.2f}, {c.velocity.y:.2f})")
            # tiny sleep so demo doesn't rush in real time when run manually
            time.sleep(0.001)

    print("Final position:", c.position)
