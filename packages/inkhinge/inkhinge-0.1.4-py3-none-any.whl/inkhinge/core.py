"""inkhinge包的核心功能模块"""
"read_to_csv:"
import os
import numpy as np
import pandas as pd
from spectrochempy_omnic import OMNICReader as read
from decimal import Decimal, Context, ROUND_HALF_UP


def read_to_csv(input_path, output_path=None, background_path=None, overwrite=False, recursive=False, precision=20):
    """
    读取Omnic SPA/SRS文件并转换为CSV格式

    参数:
        input_path (str): 输入SPA/SRS文件路径或包含这些文件的目录路径
        output_path (str): 输出CSV文件路径或目录路径
        background_path (str): 背景BG.spa文件路径
        overwrite (bool): 是否覆盖已存在的文件
        recursive (bool): 是否递归处理子目录(仅在处理目录时有效)
        precision (int): 输出数据的小数位数精度

    返回:
        处理结果信息(成功转换的文件数量或单个文件的输出路径)
    """
    def float_to_fixed_str(value, precision=20):
        """
        将浮点数转换为指定精度的定点小数表示字符串
        不使用科学计数法，确保数据精度
        """
        if np.isnan(value):
            return 'nan'
        try:
            # 使用Decimal确保精确表示
            ctx = Context(prec=max(25, precision + 5), rounding=ROUND_HALF_UP)
            dec = ctx.create_decimal(str(value))
            return f"{dec:.{precision}f}"
        except:
            # 处理非数字值
            return str(value)

    def detect_data_type(reader):
        """检测数据类型并返回相应的标题和单位"""
        data_type_mapping = {
            0: ("Absorbance", "AU"),
            1: ("Transmittance", "%"),
            2: ("Reflectance", "%"),
            3: ("Single Beam", ""),
            4: ("Kubelka-Munk", "KM units"),
        }

        # 优先使用data_type属性
        if hasattr(reader, 'data_type') and reader.data_type in data_type_mapping:
            return data_type_mapping[reader.data_type]

        # 尝试从元数据或文件名推断
        if hasattr(reader, 'title'):
            title = reader.title.lower()
            if "absorbance" in title:
                return "Absorbance", "AU"
            elif "transmittance" in title or "透过率" in title:
                return "Transmittance", "%"
            elif "reflectance" in title:
                return "Reflectance", "%"
            elif "single beam" in title or "单光束" in title:
                return "Single Beam", ""
            elif "kubelka-munk" in title or "km" in title:
                return "Kubelka-Munk", "KM units"

        # 默认使用Y轴信息
        y_title = reader.y_title or "Intensity"
        y_units = reader.y_units or ""

        # 特殊处理Kubelka-Munk
        if "kubelka" in y_title.lower() or "km" in y_title.lower():
            return "Kubelka-Munk", "KM units"

        return y_title, y_units

    def calculate_kubelka_munk(reflectance):
        """计算Kubelka-Munk值"""
        # 确保反射率在有效范围内
        reflectance = np.clip(reflectance, 0.0001, 0.9999)
        return ((1 - reflectance) **2) / (2 * reflectance)

    def extract_spectral_data(reader):
        """
        从读取器中提取光谱数据和对应的X轴数据
        返回: (光谱数据, X轴数据, X轴标题, X轴单位)
        """
        data = reader.data  # 光谱数据
        x = reader.x  # X轴数据(通常是波长或波数)

        # 获取单位和标题
        x_units = reader.x_units or "cm^-1"
        x_title = reader.x_title or "Wavelength"

        # 确定光谱数据的正确维度
        if data.ndim == 1:
            # 单光谱数据
            spectral_data = data.reshape(1, -1)
        elif data.ndim >= 2:
            # 多光谱数据 - 确定哪一维是光谱数据
            spectral_dim = None

            # 优先检查常见维度
            if data.shape[-1] == len(x):
                spectral_dim = -1
            elif data.shape[0] == len(x):
                spectral_dim = 0

            # 如果无法确定，尝试其他维度
            if spectral_dim is None:
                for i in range(data.ndim):
                    if data.shape[i] == len(x):
                        spectral_dim = i
                        break

            # 如果仍无法确定，使用启发式方法
            if spectral_dim is None:
                # 假设光谱维度是长度最接近X轴的维度
                spectral_dim = np.argmin(np.abs(np.array(data.shape) - len(x)))
                print(f"警告: 无法确定光谱数据维度，假设为维度 {spectral_dim}")

            # 重新排列维度，使光谱数据在最后一维
            if spectral_dim != -1:
                axes = list(range(data.ndim))
                axes.remove(spectral_dim)
                axes.append(spectral_dim)
                data = data.transpose(axes)

            # 重塑为二维数组，每行是一个光谱
            spectral_data = data.reshape(-1, len(x))
        else:
            raise ValueError(f"不支持的数据维度: {data.ndim}")

        return spectral_data, x, x_title, x_units

    def apply_background_correction(sample_data, background_data, x_sample, x_bg):
        """
        应用背景校正

        参数:
            sample_data: 样本光谱数据
            background_data: 背景光谱数据
            x_sample: 样本X轴数据
            x_bg: 背景X轴数据

        返回:
            校正后的光谱数据
        """
        # 如果X轴相同，可以直接相除
        if np.array_equal(x_sample, x_bg):
            corrected_data = sample_data / background_data
        else:
            # 如果X轴不同，需要插值
            corrected_data = np.zeros_like(sample_data)
            for i, spectrum in enumerate(sample_data):
                # 插值背景数据到样本X轴上
                bg_interp = np.interp(x_sample, x_bg, background_data[0])
                # 应用校正
                corrected_data[i] = spectrum / bg_interp

        return corrected_data

    def convert_spa_to_csv(input_file, output_file=None, background_path=None, overwrite=False, precision=20):
        """
        将Omnic SPA/SRS文件转换为CSV格式

        参数:
            input_file (str): 输入SPA/SRS文件路径
            output_file (str): 输出CSV文件路径
            background_path (str): 背景BG.spa文件路径
            overwrite (bool): 是否覆盖已存在的文件
            precision (int): 输出数据的小数位数精度
        """
        # 检查输入文件
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        # 生成输出文件名
        if not output_file:
            base_name, _ = os.path.splitext(input_file)
            output_file = f"{base_name}_converted.csv"

        # 检查输出文件是否存在
        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError(f"输出文件已存在: {output_file}")

        try:
            # 读取样本文件
            print(f"正在读取样本文件: {input_file}")
            sample_reader = read(input_file)

            # 提取样本光谱数据
            sample_data, x_sample, x_title, x_units = extract_spectral_data(sample_reader)

            # 检测样本数据类型
            y_title, y_units = detect_data_type(sample_reader)

            # 读取背景文件(如果提供)
            if background_path:
                if not os.path.exists(background_path):
                    raise FileNotFoundError(f"背景文件不存在: {background_path}")

                print(f"正在读取背景文件: {background_path}")
                bg_reader = read(background_path)

                # 提取背景光谱数据
                bg_data, x_bg, _, _ = extract_spectral_data(bg_reader)

                # 应用背景校正
                if y_title == "Reflectance":
                    # 反射率数据使用除法校正
                    corrected_data = apply_background_correction(sample_data, bg_data, x_sample, x_bg)
                    y_title = "Corrected Reflectance"
                elif y_title == "Transmittance":
                    # 透射率数据使用减法校正
                    corrected_data = sample_data - bg_data
                    y_title = "Corrected Transmittance"
                else:
                    # 其他类型数据默认使用除法校正
                    corrected_data = apply_background_correction(sample_data, bg_data, x_sample, x_bg)
                    y_title = f"Corrected {y_title}"

                # 使用校正后的数据
                spectral_data = corrected_data
            else:
                # 没有背景文件，直接使用原始数据
                spectral_data = sample_data

            # 打印元数据信息
            print(f"数据维度: {spectral_data.shape}")
            print(f"X轴: {x_title} ({x_units})")
            print(f"数据类型: {y_title} ({y_units})")

            # 创建DataFrame并应用高精度格式化
            df = pd.DataFrame()
            df[f"{x_title} ({x_units})"] = [float_to_fixed_str(val, precision) for val in x_sample]

            # 检查是否需要计算Kubelka-Munk值
            if y_title == "Reflectance" or y_title == "Corrected Reflectance":
                km_data = calculate_kubelka_munk(spectral_data)
                km_title = "Kubelka-Munk"
                km_units = "KM units"

                # 添加Kubelka-Munk数据列
                if km_data.shape[0] == 1:
                    df[f"{km_title} ({km_units})"] = [float_to_fixed_str(val, precision) for val in km_data[0]]
                else:
                    for i in range(km_data.shape[0]):
                        df[f"{km_title}_{i + 1} ({km_units})"] = [float_to_fixed_str(val, precision) for val in km_data[i]]

            # 添加原始光谱数据列
            if spectral_data.shape[0] == 1:
                # 单光谱
                df[f"{y_title} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[0]]
            else:
                # 多光谱 - 尝试确定更有意义的列名
                if hasattr(sample_reader, 'spectra_titles') and len(sample_reader.spectra_titles) == spectral_data.shape[0]:
                    # 使用光谱标题作为列名
                    for i, title in enumerate(sample_reader.spectra_titles):
                        clean_title = title.strip() or f"{y_title}_{i + 1}"
                        df[f"{clean_title} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[i]]
                else:
                    # 使用编号列名
                    for i in range(spectral_data.shape[0]):
                        df[f"{y_title}_{i + 1} ({y_units})"] = [float_to_fixed_str(val, precision) for val in
                                                                spectral_data[i]]

            # 保存为CSV
            df.to_csv(output_file, index=False, na_rep='nan')
            print(f"成功转换并保存至: {output_file}")
            return output_file

        except Exception as e:
            print(f"转换失败: {str(e)}")
            return None

    def batch_convert_spa_to_csv(input_dir, output_dir=None, background_path=None, overwrite=False, recursive=False,
                                 precision=20):
        """
        批量转换目录中的SPA/SRS文件为CSV格式
        """
        # 检查输入目录
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")

        # 创建输出目录
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 收集所有SPA/SRS文件
        spa_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(('.spa', '.srs')):
                    spa_files.append(os.path.join(root, file))

            if not recursive:
                break

        if not spa_files:
            print(f"在目录 {input_dir} 中未找到SPA/SRS文件")
            return

        # 转换每个文件
        success_count = 0
        for spa_file in spa_files:
            try:
                # 生成输出文件路径
                if output_dir:
                    rel_path = os.path.relpath(spa_file, input_dir)
                    base_name, _ = os.path.splitext(rel_path)
                    output_file = os.path.join(output_dir, f"{base_name}.csv")
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                else:
                    output_file = None

                # 转换文件
                result = convert_spa_to_csv(spa_file, output_file, background_path, overwrite, precision)
                if result:
                    success_count += 1
            except Exception as e:
                print(f"处理文件 {spa_file} 时出错: {str(e)}")

        print(f"批量转换完成: 成功 {success_count}/{len(spa_files)}")
        return success_count

    # 判断输入是文件还是目录
    if os.path.isfile(input_path):
        # 处理单个文件
        return convert_spa_to_csv(input_path, output_path, background_path, overwrite, precision)
    elif os.path.isdir(input_path):
        # 处理目录
        return batch_convert_spa_to_csv(input_path, output_path, background_path, overwrite, recursive, precision)
    else:
        raise ValueError(f"输入路径不存在: {input_path}")

def add_numbers(a: int | float, b: int | float) -> int | float:
    """
    将两个数字相加的简单函数

    参数:
        a (int|float): 第一个数字
        b (int|float): 第二个数字

    返回:
        int|float: 两个数字的和

    示例:
        >>> add_numbers(1, 2)
        3
        >>> add_numbers(1.5, 2.5)
        4.0
    """
    return a + b


def multiply_numbers(a: int | float, b: int | float) -> int | float:
    """
    将两个数字相乘的简单函数

    参数:
        a (int|float): 第一个数字
        b (int|float): 第二个数字

    返回:
        int|float: 两个数字的乘积

    示例:
        >>> multiply_numbers(2, 3)
        6
        >>> multiply_numbers(2.5, 3)
        7.5
    """
    return a * b

