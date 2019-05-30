# Osmo内核实现

## -----------------若只需AI接口部分信息，请直接跳到Player部分-----------------

## 综述

游戏对战平台的实现需要两套方案：Python和HTML+CSS+JavaScript。  
一种典型的思路是：通过Python处理两个AI函数，然后将对局结果保存为文件；通过JavaScript读取文件，然后使用HTML Canvas进行绘制，实现对局回放。  
更进一步，为了现场效果和观看体验，回放时可以选定上帝视角，或跟随任意星体的视角；可以自由缩放；可以方便的进行直播或导出为视频。

## 安装

通过`git clone`或DOWNLOAD ZIP下载后，在本`README.md`文件所在的目录执行：

```bash
pip install -r requirements.txt
```

或

```bash
pip3 install -r requirements.txt
```

在使用某些IDE，并关联了此GitHub仓库的情况下，可以自动保持更新。

## 文件

### `src`目录

| 文件 | 描述 |
| - | - |
| `camera.py` | 控制摄像机视角 |
| `cell.py` | 星体基本单元 |
| `consts.py` | 定义常数 |
| `database.py` | 定义数据库 |
| `gui.py` | 图形界面（用于人机对战和复盘） |
| `kernel.py` | 内核（用于AI对战） |
| `player.py` | 用于编写AI函数 |
| `settings.py` | 用于存储自定义设置 |
| `world.py` | 游戏的世界 |

在`settings.py`中设置`ENABLE_DATABASE`为`True`，并运行`gui.py`或`kernel.py`，对战完成后，数据文件（`db`格式）会保存在`src/data`目录下。为了高效地保存游戏数据，以便进行复盘，我们使用了`sqlite`来保存每一帧的状态。（除此之外，还有另外一种保存数据的思路：类似于MPEG，存储『关键帧』和『增量』，即玩家操作）

### `frontend`目录

在此目录下执行

```bash
python -m http.server
```

或

```bash
python3 -m http.server
```

然后使用浏览器（请勿使用IE等不支持较新HTML标准的浏览器）打开`http://localhost:8000`即可。

在此页面中，可以上传前文中提到的数据文件，进行复盘。

## 内核

内核需要定义数个类。玩家需要一个Player类。  
**所有代码都非常易读（一定程度上self-documenting），可以通读代码获取所需要的信息。下面将简要地进行介绍，而具体内容不再赘述。**

### 常数和定义

坐标原点为左上角。x轴向右，y轴向下。所有坐标、速度均用`list`表示，先x后y。

### Cell

每个星体数据为一个`Cell`，包含形如`pos`，`veloc`等参数。其中`pos=[x, y]`，`veloc=[v_x, v_y]`。  
`x, y, v_x, v_y, radius`分别代表星体的x坐标，y坐标，x速度分量，y速度分量，半径，均为浮点数。

| 属性名称 | 描述 |
| - | - |
| `id` | 玩家ID（Int） |
| `pos` | x、y坐标（List） |
| `veloc` | x、y方向速度（List） |
| `radius` | 半径（Float） |
| `collide_group` | 在处理碰撞时，相接触的两个或更多星体具有相同的`collide_group`（Int） |
| `dead` | 标记死亡状态（Bool） |

| 方法名称 | 描述 | 输入 | 输出 |
| - | - | - | - |
| `distance_from` | 计算与另一个星体的最小距离 | 另一个星体（Cell） | 距离（Float） |
| `collide` | 判断是否碰撞 | 另一个星体（Cell） | 是否碰撞（Bool） |
| `area` | 计算面积 | 无 | 面积（Float） |
| `stay_in_bounds` | 将出界的星体移回界内 | 无 | 无 |
| `limit_speed` | 将超速的星体制动 | 无 | 无 |
| `move` | 移动 | 时间间隔（Float） | 无 |
| `copy` | 获得一个复制 | 无 | 这个星体的复制（Cell） |

### World

| 属性名称 | 描述 |
| - | - |
| `cells` | 所有星体构成的数组（List） |
| `result` | 游戏状态/结果（Bool） |
| `cells_count` | 存活星体数（Int） |
| `recorders` | 记录比赛状态 |
| `frame_count` | 当前帧数（Int） |
| `database` | 保存游戏的数据库 |

| 方法名称 | 描述 | 输入 | 输出 |
| - | - | - | - |
| `new_game` | 创建新游戏 | 无 | 无 |
| `check_point` | 游戏检查点 | Flag | 无 |
| `game_over` | 游戏结束 | 获胜方的ID（Int）和获胜原因 | 无 |
| `eject` | 计算弹射结果 | 星体（Cell）和角度（Float） | 无 |
| `absorb` | 计算碰撞吸收 | `collide_group`（Int） | 无 |
| `update` | 计算新一帧 | 时间间隔（Float） | 无 |
| `update_recorders` | 更新比赛状态 | 无 | 无 |

### Player

各组需要编写类`Player`，其必须包含至少两个实例方法：`__init__`和`strategy`，其参数及要求返回值如下：

`def __init__(self, id, arg)`

`id`为星体编号（0或1）。

`arg`为一个字典，其中`['world']`项为`world.py`中的`WorldStat`类，包含三个属性：
* `total_frames`：总游戏帧数
* `frame`：当前帧数
* `timer`：一个list，第0，1项分别为两玩家剩余思考时间（单位为秒）

`arg`的其余项均在每局游戏间（即两个玩家的所有对局中）保留，玩家可自行在其中添加或改变项，通过之前的战斗历史来适当改变策略。

`def strategy(self, allcells)`

`allcells`为一个list，其中包含所有当前存活的星体。编号0，1的星体为玩家星体，之后所有星体均为自由星体。

**注意：星体在`allcells`中的索引可能与前述的星体编号不同，星体编号用每个`Cell`的`id`属性表示。**

要求`strategy`方法返回一个值，即弹射角度`theta`，采用弧度制，可为`[0, 2π)`内的任意浮点数（表示弹射方向与y轴的夹角，逆时针为正）。若不弹射，返回`None`。  

**注意：这里涉及到换系和速度叠加的问题。`theta`是发起弹射的、运动的星体的参考系中的角度，弹射出的部分的运动速度还需要叠加上星体原先的运动速度。**

玩家还可自由在其中添加辅助函数，方便进行运算。

### 内核的运转方式

两个AI函数各提供一个Player。

游戏开始，初始化。根据规则的不同，初始化方式不同。

---

初始化视为第0帧，所有星体具有位置和速度。（此时应避免星体接触，即使接触也不做处理）

将当前状态输入给玩家，玩家决定是否弹射。若是，执行弹射过程。

---

【保存第0帧，进入第1帧】

所有存活的星体根据位置、速度和步长运动。

执行碰撞检测，特别需要处理多体碰撞和穿越边缘的碰撞。（先使用O(n^2)的naive算法，未来可以通过划分单元格等方式加速检测过程）

处理所有碰撞（完全非弹性），进行质量转移和动量守恒计算。（此时可能出现新的碰撞，不做处理；玩家死亡则游戏结束）

将当前状态输入给玩家，玩家决定是否弹射。若是，执行弹射过程。

---

【保存第1帧，进入第2帧】

所有存活的星体根据位置、速度和步长运动。

……

---

【以此类推】

## TODO

- [x] 将用JavaScript实现的单机游戏版本移植为Python版本
- [x] 实现人机对战和AI对战
- [x] 实现任意摄像机视角回放
- [x] 实现JavaScript对局回放
- [ ] 实现基于RTMP或HTTP-FLV（WebSocket）的直播推流
- [ ] 压缩数据库体积

## FAQ

> 装不上`pygame`咋办？

不用担心，`pygame`并不是一个关键的依赖（图形界面基于`tkinter`），在`src/settings.py`中设置`ENABLE_JNTM`为`False`，然后将`pygame`从`requirements.txt`中移除即可。

## 已知Bug

在macOS上使用双指滑动可能会触发错误（使用Homebrew安装的Python）

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```
