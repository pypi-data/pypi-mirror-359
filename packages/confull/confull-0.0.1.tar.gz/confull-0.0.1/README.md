# confull 多格式配置管理器说明文档

[Zh](https://github.com/zisull/confull/blob/main/README.md)  / [En](https://github.com/zisull/confull/blob/main/doc/README-en.md)

## 一、概述

```cmd
pip install confull
```

## 一、概述

本配置管理器是一个多格式的配置管理工具，支持 `dict` 与 `ini`、`xml`、`json`、`toml`、`yaml` 等格式的读写与自动保存。它提供了便捷的接口来管理配置数据，并且可以根据需要切换配置文件和格式。



## 二、类和方法说明

### 1. `Config` 类

该类是配置管理器的核心类，负责管理配置数据的读写、保存等操作。

#### 初始化方法 `__init__`

```python
def __init__(self, data: dict = None, file: str = "config", way: str = "toml", replace: bool = False,
             auto_save: bool = True, backup: bool = False):
```

- 参数说明
  - `data`：初始配置数据，类型为 `dict`，默认为 `None`。
  - `file`：配置文件名（可无扩展名），默认为 `"config"`。
  - `way`：配置文件格式，支持 `json`、`toml`、`yaml`、`ini`、`xml`，默认为 `"toml"`。
  - `replace`：是否覆盖已有配置文件，布尔值，默认为 `False`。
  - `auto_save`：是否自动保存，布尔值，默认为 `True`。
  - `backup`：是否备份原配置文件，布尔值，默认为 `False`。

#### 属性

- `json`：以 json 字符串格式返回配置数据。
- `dict`：以 `dict` 格式返回配置数据，也可用于批量设置配置数据。
- `auto_save`：是否自动保存，可读写属性。
- `backup`：是否备份原配置文件，可读写属性。
- `str`：以字符串格式返回配置数据。
- `file_path`：配置文件路径。
- `file_path_abs`：配置文件绝对路径。

#### 方法

- `read(key: str, default=None)`：读取配置项，支持点号路径，如 `a.b.c`。若配置项不存在，返回默认值。
- `write(key: str, value, overwrite_mode: bool = False)`：写入配置项，支持点号路径。若 `overwrite_mode` 为 `True`，路径冲突时会覆盖。写入后若 `auto_save` 为 `True`，则自动保存。
- `del_clean()`：清空所有配置并删除配置文件。
- `update(data: dict)`：批量更新配置项，支持点号路径。更新后若 `auto_save` 为 `True`，则自动保存。
- `set_data(data: dict)`：用 `dict` 完全替换配置数据。替换后若 `auto_save` 为 `True`，则自动保存。
- `del_key(key: str)`：删除指定配置项，支持点号路径。删除后若 `auto_save` 为 `True`，则自动保存。
- `_load()`：从文件加载配置，内部方法。
- `load(file: str = None, way: str = None)`：切换配置文件或格式（不自动加载内容）。
- `mark_dirty()`：标记配置已更改。
- `save()`：保存配置到文件。
- `save_to_file(file: str = None, way: str = None)`：另存为指定文件和格式。
- `_ensure_file_exists()`：确保配置文件存在，内部方法。
- `_backup_file()`：备份原配置文件，内部方法。
- `_recursive_update(original, new_data)`：递归更新配置，支持点号路径，内部方法。
- `validate_format(_way)`：校验并返回合法格式名，静态方法。
- `ensure_extension(file)`：确保文件名有正确扩展名。

## 三、使用示例

### 1. 初始化配置管理器

```python
from confull import Config

# 使用默认参数初始化
config = Config()

# 使用自定义参数初始化
data = {'a': {'b': 'c'}}
config = Config(data=data, file='custom_config', way='json')
```

### 2. 读取和写入配置项

```python
# 写入配置项
config.write('a.b', 'new_value')  # 也可以写为 : config.a.b = 'new_value'
# 读取配置项
value = config.read('a.b')  # value = config.a.b
print(value)  # 输出: new_value
```

### 3. 批量更新配置项

```python
new_data = {'a': {'b': 'updated_value'}, 'd': 'e'}
config.update(new_data)
```

### 4. 保存和另存配置文件

```python
# 保存配置文件
config.save()

# 另存为指定文件和格式
config.save_to_file(file='backup_config', way='yaml')
```

### 5. 删除配置项和清空配置

```python
# 删除配置项
config.del_key('a.b')

# 清空配置并删除文件
config.del_clean()
```

### 6.# 读写方法示例

```
# 读写方法示例
from confull import Config

cc = Config()
cc.write('学校名称', '大学')
cc.学校.日期 = "2021-01-01"
print(cc.read('学校.日期'))
print(cc['学校名称'])
print(cc.学校.日期)
print(cc)
cc.pop('学校名称')
print(cc)
cc.clear()  # 字典方式清空配置data
print(cc)
cc.del_clean()

# 字典方式设置值示例
cc = Config()
cc.dict = {'地点': '北京', '图书': {'数量': 100, '价格': 10.5}, '学生': {'数量': 1000, '年龄': 20}}
print(cc)
cc.del_clean()

# 强制覆写示例
dic_ = {'学校': 'pass'}
cc = Config(data=dic_)
cc.write('学校.大学', '大学', overwrite_mode=True)  # overwrite_mode=True 强制覆写，但会导致原路径被删除
print(cc)
cc.del_clean()
```



## 四、注意事项

- 当使用 `write`、`update`、`set_data`、`del_key` 等方法修改配置数据时，若 `auto_save` 为 `True`，会自动保存配置文件。
- 若配置文件格式不支持，会抛出 `ValueError` 异常。
- 在使用 `INIConfigHandler` 保存配置时，若数据不是嵌套字典，会将其包装在一个默认的 `'默认'` 节中。

## 尾语

作者水平有限，尽可能简化配置文件的读写流程，让使用者可以用一种更加直观、便捷的方式去操作配置信息。

2024 年 11 月 19 日   zisull@qq.com
