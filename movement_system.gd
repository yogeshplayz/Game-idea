extends Node2D

# A simple 2D character movement system for Godot.
# Use apply_input(x_axis, y_axis) each frame, then call update_motion(delta).

export var max_speed: float = 250.0
export var accel: float = 1000.0
export var friction: float = 600.0

var velocity: Vector2 = Vector2.ZERO
var acceleration: Vector2 = Vector2.ZERO
var size: Vector2 = Vector2.ZERO

func apply_input(x_axis: float, y_axis: float) -> void:
    var x = clamp(x_axis, -1.0, 1.0)
    var y = clamp(y_axis, -1.0, 1.0)
    var direction = Vector2(x, y)

    if direction.length() > 0.0:
        direction = direction.normalized()
        acceleration = direction * accel
    else:
        acceleration = Vector2.ZERO

func apply_force(force: Vector2) -> void:
    acceleration += force

func update_motion(delta: float) -> void:
    if delta <= 0.0:
        return

    velocity += acceleration * delta

    if acceleration == Vector2.ZERO:
        var speed = velocity.length()
        if speed > 0.0:
            var decel_amount = friction * delta
            var new_speed = max(0.0, speed - decel_amount)
            if new_speed == 0.0:
                velocity = Vector2.ZERO
            else:
                velocity = velocity.normalized() * new_speed

    if velocity.length() > max_speed:
        velocity = velocity.normalized() * max_speed

    position += velocity * delta

func set_size(width: float, height: float) -> void:
    size = Vector2(width, height)

func get_aabb() -> Rect2:
    if size == Vector2.ZERO:
        return Rect2()
    var top_left = position - size * 0.5
    return Rect2(top_left, size)

static func aabb_collide(a: Rect2, b: Rect2) -> bool:
    return a.intersects(b)
