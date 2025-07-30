from manim import *
import math
import numpy as np
from typing import Optional, Tuple

def ChineseMathTex(*texts, font="SimSun", tex_to_color_map={}, **kwargs):
	tex_template = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
	tex_template.add_to_preamble(r"\usepackage{amsmath}")
	tex_template.add_to_preamble(r"\usepackage{xeCJK}")
	tex_template.add_to_preamble(rf"\setCJKmainfont{{{font}}}")

	combined_chinesetext = []
	for text in texts:
		chinesetext = ""
		for i in range(len(text)):
			if ('\u4e00' <= text[i] <= '\u9fff') or ('\u3000' <= text[i] <= '\u303f') or ('\uff00' <= text[i] <= '\uffef'):
				chinesetext += rf"\text{{{text[i]}}}"
			else:
				chinesetext += text[i]
		combined_chinesetext.append(chinesetext)

	new_dict = {}
	for key in tex_to_color_map.keys():
		new_key = ""
		for char in key:
			if ('\u4e00' <= char <= '\u9fff') or ('\u3000' <= char <= '\u303f') or ('\uff00' <= char <= '\uffef'):
				new_key += rf"\text{{{char}}}"
			else:
				new_key += char
		new_dict[new_key] = tex_to_color_map[key]

	return MathTex(*combined_chinesetext, tex_template=tex_template, tex_to_color_map=new_dict, **kwargs)

def LabelDot(dot_label, dot_pos, label_pos=DOWN, buff=0.1):
	dot = Dot().move_to(dot_pos)
	label = MathTex(dot_label).next_to(dot, label_pos, buff=buff)
	return VGroup(dot, label)

def MathTexLine(formula: MathTex, direction=UP, buff=0.5, **kwargs):
	line = Line(**kwargs)
	tex = formula.next_to(line, direction, buff=buff)
	return VGroup(line, tex)

def MathTexBrace(formula: MathTex, direction=UP, buff=0.5, **kwargs):
	brace = Brace(direction=direction, **kwargs)
	tex = formula.next_to(brace, direction, buff=buff)
	return VGroup(brace, tex)

def MathTexDoublearrow(formula: MathTex, direction=UP, buff=0.5, **kwargs):
	doublearrow = DoubleArrow(**kwargs)
	tex = formula.next_to(doublearrow, direction, buff=buff)
	return VGroup(doublearrow, tex)

def ExtendedLine(line: Line, extend_distance: float) -> Line:
	start_point = line.get_start()
	end_point = line.get_end()
	direction_vector = end_point - start_point
	vector_length = np.linalg.norm(direction_vector)
	if vector_length < 1e-8:
		return line.copy()
	unit_direction_vector = direction_vector / vector_length
	new_start_point = start_point - extend_distance * unit_direction_vector
	new_end_point = end_point + extend_distance * unit_direction_vector
	new_line = Line(new_start_point, new_end_point).match_style(line)
	return new_line

def CircleInt(circle1: Circle, circle2: Circle):
	circle1_center = circle1.get_center()
	circle1_radius = circle1.radius
	circle2_center = circle2.get_center()
	circle2_radius = circle2.radius
	x1, y1, _ = circle1_center
	x2, y2, _ = circle2_center
	d = math.sqrt((x2 - x1) ** 2+(y2 - y1) ** 2)
	if d > circle1_radius + circle2_radius or d < abs(circle1_radius - circle2_radius):
		return None
	a = (circle1_radius ** 2 - circle2_radius ** 2 + d ** 2)/(2 * d)
	h = math.sqrt(circle1_radius ** 2 - a ** 2)
	xm = x1 + a * (x2 - x1)/d
	ym = y1 + a * (y2 - y1)/d
	xs1 = xm + h * (y2 - y1)/d
	xs2 = xm - h * (y2 - y1)/d
	ys1 = ym - h * (x2 - x1)/d
	ys2 = ym + h * (x2 - x1)/d
	return [xs1, ys1, 0], [xs2, ys2, 0]

def LineCircleInt(line: Line, circle: Circle):
	p1 = line.get_start()
	p2 = line.get_end()
	c = circle.get_center()
	r = circle.radius
	dx, dy, _ = p2 - p1
	cx, cy, _ = p1 - c
	a = dx**2 + dy**2
	b = 2 * (dx * cx + dy * cy)
	c = cx**2 + cy**2 - r**2
	discriminant = b**2 - 4 * a * c
	if discriminant < 0:
		return None
	t1 = (-b + math.sqrt(discriminant)) / (2 * a)
	t2 = (-b - math.sqrt(discriminant)) / (2 * a)
	intersections = []
	for t in [t1, t2]:
		if 0 <= t <= 1:
			intersection = p1 + t * (p2 - p1)
			intersections.append(intersection)
	try:
		return intersections[0], intersections[1]
	except Exception:
		try:
			return intersections[0]
		except Exception:
			return None

def LineInt(line1: Line, line2: Line) -> Optional[Tuple[float, float]]:
	def det(a, b):
		return a[0] * b[1] - a[1] * b[0]
	p1 = line1.get_start()[:2]
	p2 = line1.get_end()[:2]
	p3 = line2.get_start()[:2]
	p4 = line2.get_end()[:2]
	xdiff = (p1[0] - p2[0], p3[0] - p4[0])
	ydiff = (p1[1] - p2[1], p3[1] - p4[1])
	div = det(xdiff, ydiff)
	if div == 0:
		return None
	d = (det(p1, p2), det(p3, p4))
	x = det(d, xdiff) / div
	y = det(d, ydiff) / div
	return [x, y, 0]

def LineArcInt(line: Line, arc: Arc) -> list:
	"""计算线段与圆弧的交点（修正版）"""
	# 获取线段起点和终点（仅x,y坐标）
	p1 = line.start[:2]
	p2 = line.end[:2]

	# 处理线段退化为点的情况
	direction = p2 - p1
	length = np.linalg.norm(direction)
	if length < 1e-8:
		return None

	# 获取圆弧参数（关键修正：使用ManimCE的正确属性）
	center = arc.arc_center[:2]  # 圆弧中心（x,y）
	radius = arc.radius             # 半径
	start_angle = arc.start_angle   # 起始角度（弧度）
	angle = arc.angle               # 角度跨度（弧度，正=逆时针，负=顺时针）

	# 线段参数方程转换（以圆弧中心为原点）
	p1_centered = p1 - center
	p2_centered = p2 - center
	dx = p2_centered[0] - p1_centered[0]
	dy = p2_centered[1] - p1_centered[1]

	# 联立线段与圆的方程（二次方程）
	a = dx**2 + dy**2
	b = 2 * (p1_centered[0] * dx + p1_centered[1] * dy)
	c = p1_centered[0]**2 + p1_centered[1]**2 - radius**2
	discriminant = b**2 - 4*a*c

	# 无实根（直线与圆无交点）
	if discriminant < 0:
		return None

	# 计算t值（线段参数）
	sqrt_d = np.sqrt(discriminant)
	t1 = (-b + sqrt_d) / (2*a)
	t2 = (-b - sqrt_d) / (2*a)
	t_values = []
	for t in [t1, t2]:
		if 0 <= t <= 1 and (len(t_values) == 0 or abs(t - t_values[0]) > 1e-8):
			t_values.append(t)

	# 检查交点是否在圆弧范围内（关键修正：角度判断+容差）
	intersections = []
	TOLERANCE = 1e-6  # 角度容差（弧度）
	for t in t_values:
		# 计算交点相对圆弧中心的坐标
		x = p1_centered[0] + t * dx
		y = p1_centered[1] + t * dy
		theta = np.arctan2(y, x) % (2 * np.pi)  # 交点角度（0~2π弧度）

		# 圆弧的角度范围（模2π处理）
		start_angle_mod = start_angle % (2 * np.pi)
		end_angle_mod = (start_angle + angle) % (2 * np.pi)

		# 判断角度是否在圆弧范围内（带容差）
		if angle > 0:  # 逆时针圆弧
			if start_angle_mod < end_angle_mod:
				valid = (start_angle_mod - TOLERANCE <= theta <= end_angle_mod + TOLERANCE)
			else:
				valid = (theta >= start_angle_mod - TOLERANCE) or (theta <= end_angle_mod + TOLERANCE)
		else:  # 顺时针圆弧
			if end_angle_mod < start_angle_mod:
				valid = (end_angle_mod - TOLERANCE <= theta <= start_angle_mod + TOLERANCE)
			else:
				valid = (theta <= start_angle_mod + TOLERANCE) or (theta >= end_angle_mod - TOLERANCE)

		if valid:
			# 转换为绝对坐标（添加z=0）
			intersection = [x + center[0], y + center[1], 0.0]
			intersections.append(intersection)
	try:
		return intersections[0], intersections[1]
	except Exception:
		try:
			return intersections[0]
		except Exception:
			return None

def TangentPoint(p1, p2, line_start, line_end):
    """
    计算以两点p1和p2为圆上的点，且与线段相切的切点坐标

    参数:
    p1, p2: 圆上的两个点，格式为(x, y)或(x, y, z)
    line_start, line_end: 线段的起点和终点，格式为(x, y)或(x, y, z)

    返回:
    切点坐标(x, y, 0)，若无法计算则返回None
    """

    # 确保所有输入都是三维坐标
    def to_3d(point):
        if len(point) == 2:
            return np.array([point[0], point[1], 0.0])
        return np.array(point[:3])

    p1 = to_3d(p1)
    p2 = to_3d(p2)
    line_start = to_3d(line_start)
    line_end = to_3d(line_end)

    # 计算线段方向向量
    line_direction = line_end - line_start
    line_length = np.linalg.norm(line_direction)

    # 处理线段退化为点的情况
    if line_length < 1e-8:
        # 检查线段端点是否在圆上
        dist_p1 = np.linalg.norm(line_start - p1)
        dist_p2 = np.linalg.norm(line_start - p2)
        if abs(dist_p1 - dist_p2) < 1e-8:
            return line_start
        return None

    line_direction = line_direction / line_length

    # 计算线段p1-p2的中点
    midpoint = (p1 + p2) / 2

    # 计算线段p1-p2的方向向量
    p1p2_direction = p2 - p1
    p1p2_length = np.linalg.norm(p1p2_direction)

    if p1p2_length < 1e-8:
        # p1和p2重合，无法确定唯一的圆
        return None

    p1p2_direction = p1p2_direction / p1p2_length

    # 计算线段p1-p2的垂直向量（在二维平面上）
    perpendicular_dir = np.array([-p1p2_direction[1], p1p2_direction[0], 0.0])

    # 构建线性方程组求解圆心c = midpoint + t * perpendicular_dir
    cross_perp_line = np.cross(perpendicular_dir, line_direction)
    cross_mid_line = np.cross(midpoint - line_start, line_direction)

    a = np.dot(perpendicular_dir, perpendicular_dir) - np.dot(cross_perp_line, cross_perp_line)
    b = 2 * (np.dot(midpoint - p1, perpendicular_dir) - np.dot(cross_mid_line, cross_perp_line))
    c = np.dot(midpoint - p1, midpoint - p1) - np.dot(cross_mid_line, cross_mid_line)

    # 处理a接近零的特殊情况（退化为一次方程）
    if abs(a) < 1e-8:
        if abs(b) < 1e-8:
            return None  # 无解或无穷多解
        t = -c / b
        centers = [midpoint + t * perpendicular_dir]
    else:
        # 计算判别式
        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            # 无实数解
            return None

        # 求解t
        sqrt_d = np.sqrt(discriminant)
        t1 = (-b + sqrt_d) / (2 * a)
        t2 = (-b - sqrt_d) / (2 * a)

        # 计算可能的圆心
        centers = [midpoint + t * perpendicular_dir for t in [t1, t2]]

    # 计算对应的切点（在直线上）
    valid_tangents = []
    for center in centers:
        # 计算从line_start到center的向量在直线方向上的投影
        projection = np.dot(center - line_start, line_direction)

        # 检查投影是否在线段范围内 [0, line_length]
        if 0 <= projection <= line_length:
            # 计算切点
            tangent_point = line_start + projection * line_direction

            # 验证切点到圆心的距离是否等于圆心到p1的距离
            radius = np.linalg.norm(center - p1)
            dist_to_tangent = np.linalg.norm(center - tangent_point)

            if abs(radius - dist_to_tangent) < 1e-6:
                valid_tangents.append(tangent_point)

    # 选择距离p1和p2较近的解
    if not valid_tangents:
        return None

    # 如果有多个解，选择第一个
    return valid_tangents[0]

def VisDrawArc(scene: Scene, arc: Arc, axis=OUT, run_time=1):
	# 获取弧线的起点、终点和圆心
	start_point = arc.point_from_proportion(0)
	end_point = arc.point_from_proportion(1)
	center = arc.get_arc_center()
	
	# 根据轴方向确定旋转的起始点和方向
	if np.array_equal(axis, OUT):  # 逆时针
		draw_arc = arc  # 使用原始弧线
		rotation_start = start_point
		total_angle = arc.get_angle()
	else:  # 顺时针 (axis=IN)
		# 创建一个与原弧线方向相反的新弧线
		draw_arc = Arc(
			start_angle=angle_of_vector(end_point - center),
			angle=-arc.get_angle(),  # 负角度表示相反方向
			radius=np.linalg.norm(end_point - center),
			arc_center=center,
			color=arc.get_color(),
			stroke_width=arc.get_stroke_width()
		)
		rotation_start = end_point
		total_angle = -arc.get_angle()
	
	# 创建移动点的标记
	moving_dot = Dot(point=rotation_start)
	
	# 创建从圆心到移动点的虚线
	radius_line = DashedLine(center, rotation_start)
	
	# 计算实际弧线的半径和起始角度
	r = np.linalg.norm(rotation_start - center)
	start_angle = angle_of_vector(rotation_start - center)
	
	# 创建一个跟踪旋转进度的变量
	progress = ValueTracker(0)
	
	# 更新移动点的位置
	moving_dot.add_updater(
		lambda d: d.move_to(
			center + r * np.array([
				np.cos(start_angle + progress.get_value() * total_angle),
				np.sin(start_angle + progress.get_value() * total_angle),
				0
			])
		)
	)
	
	# 更新半径线
	radius_line.add_updater(
		lambda l: l.become(DashedLine(center, moving_dot.get_center()))
	)
	
	# 添加所有元素到场景
	scene.add(moving_dot, radius_line)
	
	# 同步执行弧线绘制和点的旋转动画（1秒持续时间）
	scene.play(
		Create(draw_arc, rate_func=linear),  # 使用调整后的弧线
		progress.animate.set_value(1),
		run_time=run_time,
		rate_func=linear
	)
	
	# 清除更新器
	moving_dot.clear_updaters()
	radius_line.clear_updaters()
	
	# 移除临时元素
	scene.remove(moving_dot, radius_line)

class TypeWriter(Animation):
    """
    自定义打字机动画：逐个字符显示Text内容
    :param mobject: 必须是Text对象，包含要显示的文本
    :param interval: 字符间显示间隔（秒），默认0.1秒
    """
    def __init__(self, mobject, interval=2, **kwargs):
        assert isinstance(mobject, Text), "TypeWriter only supports Text mobjects."
        self.interval = interval
        self.char_count = len(mobject.submobjects)
        
        # 自动计算run_time
        if "run_time" not in kwargs:
            kwargs["run_time"] = self.char_count * self.interval
            
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        current_index = int(alpha * self.char_count)
        for i, char in enumerate(self.mobject.submobjects):
            char.set_opacity(1 if i < current_index else 0)
        return self.mobject
