# Osmo内核实现

## 综述

游戏对战平台的实现需要两套方案：Python和HTML+CSS+JavaScript。

一种典型的思路是：通过Python处理两个AI函数，然后将对局结果保存为文件（可以存储每一帧的状态；或类似于MPEG，存储『关键帧』和『增量』，即玩家操作）；通过JavaScript读取文件，然后使用HTML Canvas进行绘制，实现对局回放。

更进一步，为了现场效果和观看体验，回放时可以选定上帝视角，或跟随任意星体的视角；可以自由缩放；可以方便的进行直播或导出为视频。

目前已有用JavaScript实现的单机游戏版本，接下来需要将其移植为Python版本，并实现人机对战和AI对战。

## 常数

坐标原点为左上角。x轴向右，y轴向下。所有坐标、速度均用`list`表示，先x后y。

喷气方向是对于地面参考系而言的（对人类玩家更为友好）。

碰撞和发射仍然涉及到换系的问题（这样更加严格）。

## 文件

| 文件 | 描述 |
| - | - |
| `camera.py` | 控制摄像机视角 |
| `cell.py` | 星体基本单元 |
| `consts.py` | 定义常数 |
| `gui.py` | 图形界面（用于人机对战和复盘） |
| `kernel.py` | 内核（用于AI对战） |
| `player.py` | 用于编写AI函数 |
| `world.py` | 游戏的世界 |

## 数据结构

为了高效地保存游戏数据，是否需要使用sqlite？

## 类

内核需要定义数个类。玩家需要一个Player类。

### Cell

| 属性名称 | 描述 |
| - | - |
| `pos` | x、y坐标（List） |
| `veloc` | x、y方向速度（List） |
| `radius` | 半径（Float） |
| `isplayer` | 标记是否为玩家控制（Bool） |
| `collide_group` | 在处理碰撞时，相接触的两个或更多球具有相同的`collide_group`（Int） |
| `dead` | 标记死亡状态（Bool） |

| 方法名称 | 描述 | 输入 | 输出 |
| - | - | - | - |
| `distance_from` | 计算与另一个球的最小距离 | 另一个球（Cell） | 距离（Float） |
| `collide` | 判断是否碰撞 | 另一个球（Cell） | 是否碰撞（Bool） |
| `area` | 计算面积 | 无 | 面积（Float） |
| `stay_in_bounds` | 将出界的球移回界内 | 无 | 无 |
| `limit_speed` | 将超速的球制动 | 无 | 无 |
| `move` | 移动 | 时间间隔（Float） | 无 |

### World

| 属性名称 | 描述 |
| - | - |
| `cells` | 所有球构成的数组（List） |
| `result` | 游戏状态/结果（Bool） |

| 方法名称 | 描述 | 输入 | 输出 |
| - | - | - | - |
| `new_game` | 创建新游戏 | 无 | 无 |
| `save_game` | 保存游戏 | 无 | 无 |
| `game_over` | 游戏结束 | 失败方的ID（Int） | 无 |
| `eject` | 计算弹射结果 | 球（Cell）和角度（Float） | 无 |
| `absorb` | 计算碰撞吸收 | `collide_group`（Int） | 无 |
| `update` | 计算新一帧 | 时间间隔（Float） | 无 |

### Player

Player接受当前状态（即`world.cells`），返回弹射角度（单位为弧度），或者`None`（不弹射）。

## 内核

内核的运转方式：

两个AI函数各提供一个Player。

游戏开始，初始化。根据规则的不同，初始化方式不同。

---

初始化视为第0帧，所有球具有位置和速度。（此时应避免球接触，即使接触也不做处理）

将当前状态输入给玩家，玩家决定是否弹射。若是，执行弹射过程。

---

【保存第0帧，进入第1帧】

所有存活的球根据位置、速度和步长运动。

执行碰撞检测，特别需要处理多体碰撞和穿越边缘的碰撞。（先使用O(n^2)的naive算法，未来可以通过划分单元格等方式加速检测过程）

处理所有碰撞（完全非弹性），进行质量转移和动量守恒计算。（此时可能出现新的碰撞，不做处理；玩家死亡则游戏结束）

将当前状态输入给玩家，玩家决定是否弹射。若是，执行弹射过程。

---

【保存第1帧，进入第2帧】

所有存活的球根据位置、速度和步长运动。

……

---

【以此类推】

## 已知Bug

在macOS上使用双指滑动可能会触发错误（使用Homebrew安装的Python）

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

https://bugs.python.org/issue10731

https://stackoverflow.com/questions/16995969/inertial-scrolling-in-mac-os-x-with-tkinter-and-python

https://discourse.brew.sh/t/idle3-crash-despite-tkinter-correct-version/3780/3

https://discourse.brew.sh/t/cannot-get-python-to-use-tcl-tk-version-8-6/3563/6

https://github.com/Homebrew/homebrew-core/pull/34424

https://www.python.org/download/mac/tcltk/

https://stackoverflow.com/questions/53930597/updating-tcl-tk-version-of-homebrew-python3-on-macos

https://www.activestate.com/products/activetcl/downloads/
