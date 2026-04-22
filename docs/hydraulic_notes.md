# 阻力计算说明

## 管程压降

管程先根据流速和管内径计算雷诺数：

`Re_i = rho * v_i * d_i / mu`

摩擦因子采用课程设计常用分段式：

- 层流：`f = 64 / Re`
- 湍流：`f = 0.3164 / Re^0.25`

总压降由沿程损失和局部损失组成：

`ΔP_t = f * (L_total / d_i) * rho * v_i^2 / 2 + ζ * rho * v_i^2 / 2`

其中 `ζ` 包括入口、出口和回弯损失。

## 壳程压降

壳程采用课程设计版的简化 Kern 思路。先用统一壳程几何定义计算横流速度：

`v_s = m_h / (rho * A_s)`

再计算壳程雷诺数：

`Re_s = rho * v_s * d_e / mu`

然后采用简化摩擦因子模型，得到壳程压降：

`ΔP_s = f_s * (N_b + 1) * (D_s / d_e) * rho * v_s^2 / 2`

其中：

- `A_s` 为壳程横流面积
- `d_e` 为壳程当量直径
- `N_b` 为挡板间流通段数

## 中间量释义

- `tube_velocity_m_s`：管程速度
- `shell_velocity_m_s`：壳程速度
- `tube_reynolds`：管程雷诺数
- `shell_reynolds`：壳程雷诺数
- `tube_friction_factor`：管程摩擦因子
- `shell_friction_factor`：壳程摩擦因子

## 合格判定

- 管程压降小于 `allowable_tube_pressure_drop_pa`，判定管程合格
- 壳程压降小于 `allowable_shell_pressure_drop_pa`，判定壳程合格
- 若任一侧超限，程序抛出异常并给出超限值
