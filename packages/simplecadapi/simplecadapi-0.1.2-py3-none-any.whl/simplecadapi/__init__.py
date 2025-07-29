"""
SimpleCAD API - 简化的CAD建模Python API
基于CADQuery实现，提供直观的几何建模接口
"""

# 导入核心类
from .core import (
    CoordinateSystem, Point, Line, Sketch, Body,
    WORLD_CS, LocalCoordinateSystem, get_current_cs
)

import cadquery as cq

from rich import traceback
# 启用Rich的详细错误追踪
traceback.install(show_locals=True, suppress=[cq])

# 基础构造操作
from .operations import (
    # 基础几何
    make_point, make_line, make_angle_arc, make_three_point_arc, make_segment, make_spline,
    make_sketch,
    make_rectangle, make_circle, make_triangle, make_ellipse,
    
    # 便利函数
    make_box, make_cylinder, make_sphere,
    
    # 三维建模
    extrude, revolve, loft, sweep,
    
    # 实体编辑
    shell, fillet, chamfer,
    
    # 布尔运算
    cut, union, intersect,
    
    # 高级操作
    make_linear_pattern, make_2d_pattern, make_radial_pattern, helical_sweep,
    
    # 变换
    translate_body, rotate_body,
    
    # 导出
    export_step, export_stl
)


from .advanced import (
    make_round_spring, make_square_spring,
     make_bolt_body_with_triangle_thread   
)

__version__ = "0.1.2"
__author__ = "SimpleCAD Team"

__all__ = [
    # 核心类
    "CoordinateSystem", "Point", "Line", "Sketch", "Body",
    "WORLD_CS", "LocalCoordinateSystem", "get_current_cs",
    
    # 基础操作
    "make_point", "make_line", "make_sketch", "make_angle_arc", "make_three_point_arc", "make_segment", "make_spline",
    "make_rectangle", "make_circle", "make_triangle", "make_ellipse",
    
    # 便利函数  
    "make_box", "make_cylinder", "make_sphere",
    
    # 三维建模
    "extrude", "revolve", "loft", "sweep",
    
    # 实体编辑
    "shell", "fillet", "chamfer",
    
    # 布尔运算
    "cut", "union", "intersect",
    
    # 高级操作
    "make_linear_pattern", "make_2d_pattern", "make_radial_pattern", "helical_sweep",

    # 变换
    "translate_body", "rotate_body",
    
    # 导出
    "export_step", "export_stl",
    
    # 高级建模
    "make_round_spring", "make_square_spring",
     "make_bolt_body_with_triangle_thread"
]