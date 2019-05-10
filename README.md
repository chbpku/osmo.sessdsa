# Osmo内核实现

## 综述

游戏对战平台的实现需要两套方案：Python和HTML+CSS+JavaScript。

一种典型的思路是：通过Python处理两个AI函数，然后将对局结果（即每一帧的状态，或类似于MPEG，存储『关键帧』和玩家操作）保存为文件；通过JavaScript读取文件，然后使用HTML Canvas进行绘制，实现对局回放。

更进一步，为了现场效果和观看体验，回放时可以选定上帝视角，或跟随任意星体的视角；可以自由缩放；可以方便的进行直播或导出为视频。

目前已有用JavaScript实现的单机游戏版本，接下来需要将其移植为Python版本，并实现人机对战和AI对战。

## 常数

坐标原点为左上角。x轴向右，y轴向下。所有坐标、速度均用list表示，先x后y。

喷气方向是对于地面参考系而言的。

碰撞和发射仍然涉及到换系的问题（更加严格）。

## 类

内核需要定义数个类。玩家需要一个Player类。

### Cell
| 属性名称 | 描述 |
| - | - |
| `pos` | x、y坐标 |
| `veloc` | x、y方向速度 |
| `radius` | 半径 |
| `dead` | 标记死亡状态 |

| 方法名称 | 描述 | 输入 | 输出 |
| - | - | - | - |
| `move` | 移动 | 时间间隔 | 无 |
| `destroy` | 死亡 | 无 | 无 |

### World

### Player

## 内核

内核的运转方式：

两个AI函数各提供一个Player。

游戏开始，初始化。根据规则的不同，初始化方式不同。

---

初始化视为第0帧，所有球具有位置和速度。（此时应避免球接触，即使接触也不做处理）

所有球根据位置、速度和步长运动。

【保存第0帧】

---

进入第1帧，执行碰撞检测，特别需要处理多体碰撞和穿越边缘的碰撞。（先使用O(n^2)的naive算法，未来可以通过划分单元格等方式加速检测过程）

处理所有碰撞（完全非弹性），进行质量转移和动量守恒计算。（此时可能出现新的碰撞，不做处理）

将当前状态输入给玩家，玩家决定是否喷气。若是，执行喷射过程。（同上）

【保存第1帧】

---

## 已知Bug

在macOS上使用双指滑动将会触发错误（使用Homebrew安装的Python）

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
