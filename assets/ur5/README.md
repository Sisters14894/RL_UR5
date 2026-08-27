# UR5 模型文件

这份 URDF 是后续 Isaac Lab / URDF 转换用的**工程仿真模型**。为了保持仓库轻量，它没有内嵌官方视觉网格，而是用圆柱、球等基础几何体近似外观和碰撞体。关节树、几何变换、质量、质心、惯量、关节限位来自下列一手参数来源。

## 文件

- `ur5.urdf`: 自包含模型，只依赖 XML，不依赖外部 mesh。
- `source_manifest.txt`: 数值溯源链接。

## 来源与约定

截图中的 UR5 DH 值是：

| 关节 | d / m | a / m |
|---:|---:|---:|
| 1 | 0.089159 | 0 |
| 2 | 0 | -0.425 |
| 3 | 0 | -0.39225 |
| 4 | 0.10915 | 0 |
| 5 | 0.09465 | 0 |
| 6 | 0.0823 | 0 |

URDF 不直接以一张 DH 表描述机械臂，而是使用相邻连杆坐标系的偏移和旋转。本文件采用 ROS Industrial UR description 的标准关节约定，因此同一组几何也对应上述 DH。关节轴顺序为：

```text
shoulder_pan_joint -> shoulder_lift_joint -> elbow_joint ->
wrist_1_joint -> wrist_2_joint -> wrist_3_joint
```

末端法兰为 `flange` 连杆。工具坐标系或夹爪应当从 `flange` 继续添加。

注意：DH 表里的距离没有直接包含肩部横向偏移和肘部小偏移；ROS 官方模型使用的补充值是：

- 肩部偏移：`0.13585 m`
- 肘部偏移：`0.0165 m`

这些值已经体现在 URDF 几何说明和 `configs/robot/ur5.yaml` 中。

## 后续转换

环境装好后执行 Isaac Lab 的 URDF importer 时优先使用这个路径：

```powershell
D:\Sis\Documents\RL_UR5\assets\ur5\ur5.urdf
```

转换前需要确认的选项：

1. 合并固定关节。
2. 保留六个 revolute 关节。
3. 使用米制单位，重力方向为负 Z。
4. 第一次先检查生成的 USD 关节顺序是否与本 README 的顺序一致。
