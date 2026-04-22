from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from config import DesignConfig
from main import run_design
from src.file_io import (
    export_excel_report,
    export_word_report,
    load_config_from_excel,
    load_config_from_json,
    write_parameter_template_excel,
)
from src.utils import DesignError


class DesignApp:
    """Desktop UI for shell-and-tube cooler course design."""

    FLOAT_FIELDS: list[tuple[str, str]] = [
        ("hot_mass_flow_kg_s", "煤油质量流量 (kg/s)"),
        ("hot_inlet_temp_c", "煤油入口温度 (℃)"),
        ("hot_outlet_temp_c", "煤油出口温度 (℃)"),
        ("cold_inlet_temp_c", "冷却水入口温度 (℃)"),
        ("cold_outlet_temp_c", "冷却水出口温度 (℃)"),
        ("hot_pressure_mpa", "煤油压力 (MPa)"),
        ("cold_pressure_mpa", "冷却水压力 (MPa)"),
        ("tube_outer_diameter_m", "管外径 (m)"),
        ("tube_inner_diameter_m", "管内径 (m)"),
        ("pitch_ratio", "管间距比"),
        ("layout_angle_deg", "布管角 (deg)"),
        ("shell_clearance_m", "壳体单边间隙 (m)"),
        ("baffle_spacing_ratio", "挡板间距比"),
        ("baffle_spacing_min_m", "挡板间距最小值 (m)"),
        ("baffle_spacing_max_m", "挡板间距最大值 (m)"),
        ("baffle_cut_ratio", "挡板切口率"),
        ("tube_wall_thermal_conductivity_w_m_k", "管壁导热系数 (W/m/K)"),
        ("fouling_resistance_tube_m2_k_w", "管侧污垢热阻 (m2·K/W)"),
        ("fouling_resistance_shell_m2_k_w", "壳侧污垢热阻 (m2·K/W)"),
        ("initial_overall_u_w_m2_k", "初选总传热系数 U (W/m2/K)"),
        ("tube_velocity_min_m_s", "管程最小流速 (m/s)"),
        ("tube_velocity_max_m_s", "管程最大流速 (m/s)"),
        ("shell_velocity_min_m_s", "壳程最小流速 (m/s)"),
        ("shell_velocity_max_m_s", "壳程最大流速 (m/s)"),
        ("allowable_tube_pressure_drop_pa", "许用管程压降 (Pa)"),
        ("allowable_shell_pressure_drop_pa", "许用壳程压降 (Pa)"),
        ("area_margin_min", "面积裕量最小值"),
        ("area_margin_max", "面积裕量最大值"),
        ("tube_inlet_loss_coefficient", "入口局部阻力系数"),
        ("tube_return_loss_coefficient_per_pass", "回弯局部阻力系数"),
        ("tube_outlet_loss_coefficient", "出口局部阻力系数"),
        ("shell_friction_factor_constant", "壳程摩擦系数常数"),
    ]
    INT_FIELDS: list[tuple[str, str]] = [
        ("shell_passes", "壳程数"),
        ("tube_passes", "管程数"),
        ("max_iterations", "最大迭代次数"),
    ]
    BOOL_FIELDS: list[tuple[str, str]] = [
        ("use_u_recalculation", "启用 U 校核复算"),
        ("strict_property_range", "物性越界严格报错"),
        ("print_intermediate", "命令行打印中间量"),
        ("export_markdown_tables", "启用 Markdown 表输出"),
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("固定管板式管壳式煤油冷却器设计程序")
        self.root.geometry("1440x900")
        self.root.configure(bg="#eef3f8")
        self.current_config = DesignConfig(print_intermediate=False)
        self.current_design = None
        self.workspace_dir = Path(__file__).resolve().parent

        self.string_vars: dict[str, tk.StringVar] = {}
        self.bool_vars: dict[str, tk.BooleanVar] = {}
        self.treeviews: dict[str, ttk.Treeview] = {}
        self.card_value_labels: dict[str, ttk.Label] = {}
        self.card_note_labels: dict[str, ttk.Label] = {}
        self.presentation_widgets: dict[str, ttk.Label] = {}

        self.status_var = tk.StringVar(value="状态：已加载默认课程设计参数。")
        self.status_banner_var = tk.StringVar(value="等待计算")
        self.conclusion_text = tk.Text(self.root, wrap="word", height=16, font=("Microsoft YaHei UI", 10))
        self.log_text = tk.Text(self.root, wrap="word", height=18, font=("Consolas", 10))

        self._configure_styles()
        self._build_layout()
        self._load_config_into_form(self.current_config)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("App.TLabelframe", background="#eef3f8")
        style.configure("App.TLabelframe.Label", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("CardTitle.TLabel", font=("Microsoft YaHei UI", 10, "bold"), background="#ffffff", foreground="#385170")
        style.configure("CardValue.TLabel", font=("Microsoft YaHei UI", 16, "bold"), background="#ffffff", foreground="#0f172a")
        style.configure("CardNote.TLabel", font=("Microsoft YaHei UI", 9), background="#ffffff", foreground="#64748b")
        style.configure("BannerTitle.TLabel", font=("Microsoft YaHei UI", 13, "bold"), background="#ffffff")

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = tk.Frame(self.root, bg="#eef3f8", padx=16, pady=14)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        tk.Label(
            header,
            text="固定管板式管壳式煤油冷却器设计界面",
            bg="#eef3f8",
            fg="#102a43",
            font=("Microsoft YaHei UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            textvariable=self.status_var,
            bg="#eef3f8",
            fg="#2c5282",
            font=("Microsoft YaHei UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        paned = ttk.Panedwindow(self.root, orient="horizontal")
        paned.grid(row=1, column=0, sticky="nsew")

        left = ttk.Frame(paned, padding=12)
        right = ttk.Frame(paned, padding=12)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=0)
        right.rowconfigure(1, weight=1)
        paned.add(left, weight=1)
        paned.add(right, weight=2)

        self._build_left_panel(left)
        self._build_right_panel(right)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        file_box = ttk.LabelFrame(parent, text="文件与操作", padding=10, style="App.TLabelframe")
        file_box.grid(row=0, column=0, sticky="ew")
        file_box.columnconfigure(0, weight=1)
        ttk.Button(file_box, text="导入 JSON 参数", command=self.import_json_parameters).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="导入 Excel 参数表", command=self.import_excel_parameters).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="导出参数 JSON", command=self.export_parameters_json).grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="导出参数 Excel 模板", command=self.export_parameter_template).grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="开始计算", command=self.run_calculation).grid(row=4, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="恢复默认参数", command=self.reset_defaults).grid(row=5, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="导出 Markdown 摘要", command=self.export_markdown_results).grid(row=6, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="导出 Excel 结果表", command=self.export_excel_results).grid(row=7, column=0, sticky="ew", pady=2)
        ttk.Button(file_box, text="导出 Word 结果表", command=self.export_word_results).grid(row=8, column=0, sticky="ew", pady=2)

        note = ttk.LabelFrame(parent, text="参数说明", padding=10, style="App.TLabelframe")
        note.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(
            note,
            text="Excel 参数表格式：第 1 列为参数名或字段名，第 2 列为参数值。\n"
            "管长候选可在单元格中写成：1.5, 2.0, 3.0, 4.5, 6.0",
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        form_frame = ttk.LabelFrame(parent, text="输入参数与工程假设", padding=10, style="App.TLabelframe")
        form_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(form_frame, highlightthickness=0, bg="#ffffff")
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.columnconfigure(1, weight=1)
        inner.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        row = 0
        for name, label in self.FLOAT_FIELDS + self.INT_FIELDS:
            ttk.Label(inner, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=4)
            variable = tk.StringVar()
            self.string_vars[name] = variable
            ttk.Entry(inner, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=4)
            row += 1

        ttk.Label(inner, text="管长候选 (m)").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=4)
        tube_length_var = tk.StringVar()
        self.string_vars["tube_length_candidates_m"] = tube_length_var
        ttk.Entry(inner, textvariable=tube_length_var).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        for name, label in self.BOOL_FIELDS:
            variable = tk.BooleanVar()
            self.bool_vars[name] = variable
            ttk.Checkbutton(inner, text=label, variable=variable).grid(row=row, column=0, columnspan=2, sticky="w", pady=3)
            row += 1

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        banner = tk.Frame(parent, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        banner.grid(row=0, column=0, sticky="ew")
        banner.columnconfigure(1, weight=1)
        self.status_indicator = tk.Label(banner, text="●", fg="#c2410c", bg="#ffffff", font=("Microsoft YaHei UI", 18, "bold"))
        self.status_indicator.grid(row=0, column=0, padx=(0, 8))
        ttk.Label(banner, textvariable=self.status_banner_var, style="BannerTitle.TLabel").grid(row=0, column=1, sticky="w")

        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        summary_frame = ttk.Frame(notebook, padding=12)
        presentation_frame = ttk.Frame(notebook, padding=12)
        thermal_frame = ttk.Frame(notebook, padding=12)
        mechanical_frame = ttk.Frame(notebook, padding=12)
        hydraulic_frame = ttk.Frame(notebook, padding=12)
        conclusion_frame = ttk.Frame(notebook, padding=12)
        log_frame = ttk.Frame(notebook, padding=12)

        notebook.add(presentation_frame, text="课程设计模式")
        notebook.add(summary_frame, text="综合概览")
        notebook.add(thermal_frame, text="传热计算")
        notebook.add(mechanical_frame, text="结构计算")
        notebook.add(hydraulic_frame, text="阻力计算")
        notebook.add(conclusion_frame, text="综合结论")
        notebook.add(log_frame, text="计算日志")

        self._build_presentation_page(presentation_frame)
        self._build_summary_cards(summary_frame)
        self._build_result_tree(thermal_frame, "thermal")
        self._build_result_tree(mechanical_frame, "mechanical")
        self._build_result_tree(hydraulic_frame, "hydraulic")

        conclusion_frame.columnconfigure(0, weight=1)
        conclusion_frame.rowconfigure(0, weight=1)
        self.conclusion_text.grid(in_=conclusion_frame, row=0, column=0, sticky="nsew")

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text.grid(in_=log_frame, row=0, column=0, sticky="nsew")
        self.conclusion_text.configure(state="disabled")
        self.log_text.configure(state="disabled")

    def _build_summary_cards(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        parent.columnconfigure(3, weight=1)

        cards = [
            ("heat_duty", "热负荷", "等待计算"),
            ("required_area", "所需面积", "等待计算"),
            ("selected_geometry", "结构方案", "等待计算"),
            ("pressure_state", "阻力校核", "等待计算"),
        ]
        self.card_frames: dict[str, tk.Frame] = {}
        for index, (key, title, note) in enumerate(cards):
            frame = tk.Frame(parent, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
            frame.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < len(cards) - 1 else 0)
            ttk.Label(frame, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
            value_label = ttk.Label(frame, text="--", style="CardValue.TLabel")
            value_label.grid(row=1, column=0, sticky="w", pady=(10, 6))
            note_label = ttk.Label(frame, text=note, style="CardNote.TLabel")
            note_label.grid(row=2, column=0, sticky="w")
            self.card_frames[key] = frame
            self.card_value_labels[key] = value_label
            self.card_note_labels[key] = note_label

    def _build_presentation_page(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=0)
        parent.rowconfigure(3, weight=1)
        parent.rowconfigure(4, weight=1)

        title_box = tk.Frame(parent, bg="#ffffff", padx=16, pady=14, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        title_box.grid(row=0, column=0, sticky="ew")
        title_box.columnconfigure(0, weight=1)
        ttk.Label(title_box, text="课程设计答辩展示页", style="BannerTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            title_box,
            text="集中展示题目工况、核心计算结果、结构方案与合格判定，适合老师快速查看。",
            style="CardNote.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        middle = ttk.Frame(parent)
        middle.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=1)
        middle.rowconfigure(0, weight=1)

        input_box = tk.Frame(middle, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        input_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        result_box = tk.Frame(middle, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        result_box.grid(row=0, column=1, sticky="nsew")
        input_box.columnconfigure(1, weight=1)
        result_box.columnconfigure(1, weight=1)

        ttk.Label(input_box, text="题目工况", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        input_fields = [
            ("hot_mass_flow", "煤油质量流量"),
            ("hot_temp_span", "煤油进出口温度"),
            ("cold_temp_span", "冷却水进出口温度"),
            ("pressure_span", "工作压力"),
        ]
        for row, (key, label) in enumerate(input_fields, start=1):
            ttk.Label(input_box, text=label, style="CardNote.TLabel").grid(row=row, column=0, sticky="w", pady=6)
            widget = ttk.Label(input_box, text="--", style="CardValue.TLabel")
            widget.grid(row=row, column=1, sticky="e", pady=6)
            self.presentation_widgets[key] = widget

        ttk.Label(result_box, text="核心结果", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        result_fields = [
            ("heat_duty", "热负荷"),
            ("water_flow", "冷却水流量"),
            ("u_value", "总传热系数"),
            ("area_pair", "所需/实际面积"),
            ("geometry", "最终结构方案"),
            ("pressure_drop", "管/壳程压降"),
        ]
        for row, (key, label) in enumerate(result_fields, start=1):
            ttk.Label(result_box, text=label, style="CardNote.TLabel").grid(row=row, column=0, sticky="w", pady=6)
            widget = ttk.Label(result_box, text="--", style="CardValue.TLabel")
            widget.grid(row=row, column=1, sticky="e", pady=6)
            self.presentation_widgets[key] = widget

        bottom = ttk.Frame(parent)
        bottom.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)

        pass_box = tk.Frame(bottom, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        pass_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        note_box = tk.Frame(bottom, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        note_box.grid(row=0, column=1, sticky="nsew")
        pass_box.columnconfigure(1, weight=1)
        note_box.columnconfigure(0, weight=1)

        ttk.Label(pass_box, text="合格判定", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        status_fields = [
            ("area_ok", "面积是否满足"),
            ("velocity_ok", "流速是否满足"),
            ("tube_dp_ok", "管程压降"),
            ("shell_dp_ok", "壳程压降"),
            ("overall_ok", "最终结论"),
        ]
        for row, (key, label) in enumerate(status_fields, start=1):
            ttk.Label(pass_box, text=label, style="CardNote.TLabel").grid(row=row, column=0, sticky="w", pady=6)
            widget = ttk.Label(pass_box, text="--", style="CardValue.TLabel")
            widget.grid(row=row, column=1, sticky="e", pady=6)
            self.presentation_widgets[key] = widget

        ttk.Label(note_box, text="说明与答辩提示", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        note_widget = ttk.Label(
            note_box,
            text="--",
            style="CardNote.TLabel",
            justify="left",
            wraplength=420,
        )
        note_widget.grid(row=1, column=0, sticky="nw", pady=(10, 0))
        self.presentation_widgets["presentation_note"] = note_widget

        faq_box = tk.Frame(parent, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        faq_box.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        faq_box.columnconfigure(0, weight=1)
        faq_box.rowconfigure(1, weight=1)
        ttk.Label(faq_box, text="老师常问问题", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        faq_text = tk.Text(
            faq_box,
            wrap="word",
            height=10,
            font=("Microsoft YaHei UI", 10),
            bg="#ffffff",
            fg="#334155",
            relief="flat",
            highlightthickness=0,
        )
        faq_text.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        faq_text.configure(state="disabled")
        self.faq_text = faq_text

        flow_box = tk.Frame(parent, bg="#ffffff", padx=14, pady=12, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
        flow_box.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(flow_box, text="流程示意图", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        flow_strip = tk.Frame(flow_box, bg="#ffffff")
        flow_strip.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        for col in range(9):
            flow_strip.columnconfigure(col, weight=1)

        steps = [
            ("flow_input", "输入", "工况参数\n物性表"),
            ("flow_thermal", "热工", "Q、LMTD\nU、面积"),
            ("flow_mechanical", "结构", "管长、管数\n壳径、挡板"),
            ("flow_hydraulic", "阻力", "流速、Re\n压降校核"),
            ("flow_conclusion", "结论", "是否可行\n推荐方案"),
        ]
        self.flow_step_frames: dict[str, tk.Frame] = {}
        for index, (key, title, note) in enumerate(steps):
            column = index * 2
            card = tk.Frame(flow_strip, bg="#f8fafc", padx=12, pady=10, bd=0, highlightthickness=1, highlightbackground="#dbe7f3")
            card.grid(row=0, column=column, sticky="nsew")
            tk.Label(
                card,
                text=title,
                bg="#f8fafc",
                fg="#102a43",
                font=("Microsoft YaHei UI", 11, "bold"),
            ).grid(row=0, column=0, sticky="w")
            note_label = tk.Label(
                card,
                text=note,
                bg="#f8fafc",
                fg="#52606d",
                justify="left",
                font=("Microsoft YaHei UI", 9),
            )
            note_label.grid(row=1, column=0, sticky="w", pady=(6, 0))
            self.presentation_widgets[key] = note_label
            self.flow_step_frames[key] = card

            if index < len(steps) - 1:
                arrow = tk.Label(
                    flow_strip,
                    text="→",
                    bg="#ffffff",
                    fg="#94a3b8",
                    font=("Microsoft YaHei UI", 20, "bold"),
                )
                arrow.grid(row=0, column=column + 1, sticky="nsew")

    def _build_result_tree(self, parent: ttk.Frame, name: str) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tree = ttk.Treeview(parent, columns=("item", "value", "unit", "status"), show="headings", height=16)
        tree.heading("item", text="项目")
        tree.heading("value", text="数值")
        tree.heading("unit", text="单位")
        tree.heading("status", text="状态")
        tree.column("item", width=230, anchor="w")
        tree.column("value", width=180, anchor="e")
        tree.column("unit", width=100, anchor="center")
        tree.column("status", width=110, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        tree.tag_configure("ok", background="#ecfdf3", foreground="#166534")
        tree.tag_configure("warn", background="#fff7ed", foreground="#9a3412")
        tree.tag_configure("fail", background="#fef2f2", foreground="#b91c1c")
        self.treeviews[name] = tree

    def _load_config_into_form(self, config: DesignConfig) -> None:
        for name, _label in self.FLOAT_FIELDS + self.INT_FIELDS:
            self.string_vars[name].set(str(getattr(config, name)))
        self.string_vars["tube_length_candidates_m"].set(", ".join(str(item) for item in config.tube_length_candidates_m))
        for name, _label in self.BOOL_FIELDS:
            self.bool_vars[name].set(bool(getattr(config, name)))

    def _read_form_into_config(self) -> DesignConfig:
        values: dict[str, object] = {}
        for name, _label in self.FLOAT_FIELDS:
            values[name] = float(self.string_vars[name].get().strip())
        for name, _label in self.INT_FIELDS:
            values[name] = int(self.string_vars[name].get().strip())
        values["tube_length_candidates_m"] = self.string_vars["tube_length_candidates_m"].get().strip()
        for name, _label in self.BOOL_FIELDS:
            values[name] = bool(self.bool_vars[name].get())
        values["print_intermediate"] = False
        return DesignConfig.from_mapping(values)

    def import_json_parameters(self) -> None:
        file_path = filedialog.askopenfilename(title="选择 JSON 参数文件", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            config = load_config_from_json(file_path)
        except Exception as exc:
            messagebox.showerror("导入失败", f"JSON 参数文件读取失败：\n{exc}")
            return
        self.current_config = config
        self._load_config_into_form(config)
        self.status_var.set(f"状态：已导入 JSON 参数文件 {Path(file_path).name}")
        self._append_log(f"[参数导入] JSON -> {file_path}")

    def import_excel_parameters(self) -> None:
        file_path = filedialog.askopenfilename(title="选择 Excel 参数表", filetypes=[("Excel files", "*.xlsx;*.xlsm")])
        if not file_path:
            return
        try:
            config = load_config_from_excel(file_path)
        except Exception as exc:
            messagebox.showerror("导入失败", f"Excel 参数表读取失败：\n{exc}")
            return
        self.current_config = config
        self._load_config_into_form(config)
        self.status_var.set(f"状态：已导入 Excel 参数表 {Path(file_path).name}")
        self._append_log(f"[参数导入] Excel -> {file_path}")

    def export_parameters_json(self) -> None:
        try:
            config = self._read_form_into_config()
        except Exception as exc:
            messagebox.showerror("参数错误", f"当前表单参数无法导出：\n{exc}")
            return
        file_path = filedialog.asksaveasfilename(title="保存参数 JSON", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        export_data = config.to_dict()
        export_data.pop("base_dir", None)
        Path(file_path).write_text(json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8")
        self.status_var.set(f"状态：参数已导出到 {Path(file_path).name}")
        self._append_log(f"[参数导出] JSON -> {file_path}")

    def export_parameter_template(self) -> None:
        try:
            config = self._read_form_into_config()
        except Exception as exc:
            messagebox.showerror("参数错误", f"当前表单参数无法导出 Excel 模板：\n{exc}")
            return
        file_path = filedialog.asksaveasfilename(title="保存 Excel 参数模板", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        try:
            write_parameter_template_excel(file_path, config)
        except Exception as exc:
            messagebox.showerror("导出失败", f"Excel 参数模板导出失败：\n{exc}")
            return
        self.status_var.set(f"状态：Excel 参数模板已导出到 {Path(file_path).name}")
        self._append_log(f"[参数导出] Excel 模板 -> {file_path}")

    def reset_defaults(self) -> None:
        self.current_config = DesignConfig(print_intermediate=False)
        self._load_config_into_form(self.current_config)
        self.status_var.set("状态：已恢复默认课程设计参数。")
        self._append_log("[参数重置] 已恢复默认配置")

    def run_calculation(self) -> None:
        try:
            config = self._read_form_into_config()
            design = run_design(config)
        except DesignError as exc:
            self.current_design = None
            self._update_failure_state(str(exc))
            self.status_var.set("状态：计算失败，请调整参数后重试。")
            self._append_log(f"[计算失败] {exc}")
            messagebox.showwarning("计算失败", str(exc))
            return
        except Exception as exc:
            self.status_var.set("状态：参数解析失败。")
            self._append_log(f"[参数错误] {exc}")
            messagebox.showerror("参数错误", f"参数解析或计算过程中发生错误：\n{exc}")
            return

        self.current_config = config
        self.current_design = design
        self._update_success_state(design)
        self.status_var.set("状态：计算完成，右侧结果已刷新。")
        self._append_log(self._build_log(design))

    def export_markdown_results(self) -> None:
        if self.current_design is None:
            messagebox.showinfo("暂无结果", "请先完成一次计算，再导出结果。")
            return
        file_path = filedialog.asksaveasfilename(title="保存 Markdown 摘要", defaultextension=".md", filetypes=[("Markdown files", "*.md")])
        if not file_path:
            return
        Path(file_path).write_text(self._build_export_markdown(self.current_design), encoding="utf-8")
        self.status_var.set(f"状态：Markdown 摘要已导出到 {Path(file_path).name}")
        self._append_log(f"[结果导出] Markdown -> {file_path}")

    def export_excel_results(self) -> None:
        if self.current_design is None:
            messagebox.showinfo("暂无结果", "请先完成一次计算，再导出 Excel 结果表。")
            return
        file_path = filedialog.asksaveasfilename(title="保存 Excel 结果表", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        try:
            export_excel_report(file_path, self.current_design, self.workspace_dir)
        except Exception as exc:
            messagebox.showerror("导出失败", f"Excel 结果表导出失败：\n{exc}")
            return
        self.status_var.set(f"状态：Excel 结果表已导出到 {Path(file_path).name}")
        self._append_log(f"[结果导出] Excel -> {file_path}")

    def export_word_results(self) -> None:
        if self.current_design is None:
            messagebox.showinfo("暂无结果", "请先完成一次计算，再导出 Word 结果表。")
            return
        file_path = filedialog.asksaveasfilename(title="保存 Word 结果表", defaultextension=".docx", filetypes=[("Word files", "*.docx")])
        if not file_path:
            return
        try:
            export_word_report(file_path, self.current_design)
        except Exception as exc:
            messagebox.showerror("导出失败", f"Word 结果表导出失败：\n{exc}")
            return
        self.status_var.set(f"状态：Word 结果表已导出到 {Path(file_path).name}")
        self._append_log(f"[结果导出] Word -> {file_path}")

    def _update_success_state(self, design) -> None:
        thermal = design.thermal_result
        mechanical = design.mechanical_result
        hydraulic = design.hydraulic_result

        self.status_banner_var.set("方案可行，计算结果满足面积、流速和压降约束。")
        self.status_indicator.configure(fg="#16a34a")

        self.card_value_labels["heat_duty"].configure(text=f"{thermal.heat_duty_w / 1000:.2f} kW")
        self.card_note_labels["heat_duty"].configure(text=f"LMTD = {thermal.lmtd_k:.2f} K，F = {thermal.correction_factor:.4f}")
        self._set_card_color("heat_duty", "#e8f5e9", "#b7e4c7")

        self.card_value_labels["required_area"].configure(text=f"{thermal.required_area_m2:.2f} m²")
        self.card_note_labels["required_area"].configure(text=f"U_calculated = {thermal.overall_u_calculated_w_m2_k:.2f} W/(m²·K)")
        self._set_card_color("required_area", "#eef7ff", "#bfdbfe")

        self.card_value_labels["selected_geometry"].configure(text=f"{mechanical.tube_geometry.tube_length_m:.1f} m / {mechanical.tube_geometry.tube_count} 根")
        self.card_note_labels["selected_geometry"].configure(text=f"面积裕量 = {mechanical.area_margin_ratio:.2%}")
        self._set_card_color("selected_geometry", "#fff7ed", "#fed7aa")

        pressure_ok = hydraulic.tube_pressure_drop_ok and hydraulic.shell_pressure_drop_ok
        pressure_text = "合格" if pressure_ok else "超限"
        self.card_value_labels["pressure_state"].configure(text=pressure_text)
        self.card_note_labels["pressure_state"].configure(
            text=f"管程 {hydraulic.tube_pressure_drop_pa:.0f} Pa；壳程 {hydraulic.shell_pressure_drop_pa:.0f} Pa"
        )
        self._set_card_color("pressure_state", "#ecfdf3" if pressure_ok else "#fef2f2", "#86efac" if pressure_ok else "#fecaca")

        self._fill_tree("thermal", design.result_tables["thermal"])
        self._fill_tree("mechanical", design.result_tables["mechanical"])
        self._fill_tree("hydraulic", design.result_tables["hydraulic"])
        self._set_conclusion_text("方案可行", self._build_conclusion(design))
        self._update_presentation_page(design)

    def _update_failure_state(self, reason: str) -> None:
        self.status_banner_var.set("方案不可行，请检查输入参数或放宽约束。")
        self.status_indicator.configure(fg="#dc2626")
        for key in self.card_value_labels:
            self.card_value_labels[key].configure(text="--")
            self.card_note_labels[key].configure(text="等待重新计算")
            self._set_card_color(key, "#fff7ed", "#fde68a")
        self.card_value_labels["pressure_state"].configure(text="失败")
        for tree in self.treeviews.values():
            for item in tree.get_children():
                tree.delete(item)
        self._set_conclusion_text("方案不可行", reason)
        self._clear_presentation_page(reason)

    def _fill_tree(self, name: str, rows: list[dict]) -> None:
        tree = self.treeviews[name]
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            item = row.get("项目", row.get("参数", row.get("物性", "")))
            value = row.get("值", row.get("煤油", ""))
            unit = row.get("单位", "")
            status = self._row_status_text(item, value)
            tags = (self._row_status_tag(status),)
            if isinstance(value, float):
                display_value = f"{value:.6g}"
            else:
                display_value = str(value)
            tree.insert("", "end", values=(item, display_value, unit, status), tags=tags)

    def _row_status_text(self, item: str, value) -> str:
        if isinstance(value, str) and value in {"是", "否"}:
            return "合格" if value == "是" else "超限"
        if "压降是否合格" in item or "约束是否合格" in item:
            return "合格" if value == "是" else "超限"
        if "面积裕量" in item and isinstance(value, float):
            if self.current_config.area_margin_min <= value <= self.current_config.area_margin_max:
                return "正常"
            return "关注"
        return "正常"

    @staticmethod
    def _row_status_tag(status: str) -> str:
        if status == "合格" or status == "正常":
            return "ok"
        if status == "关注":
            return "warn"
        return "fail"

    def _set_card_color(self, key: str, background: str, border: str) -> None:
        frame = self.card_frames[key]
        frame.configure(bg=background, highlightbackground=border)

    def _update_presentation_page(self, design) -> None:
        thermal = design.thermal_result
        mechanical = design.mechanical_result
        hydraulic = design.hydraulic_result
        operating = design.operating_condition

        area_ok = mechanical.actual_area_m2 >= thermal.required_area_m2
        velocity_ok = (
            self.current_config.tube_velocity_min_m_s <= hydraulic.tube_velocity_m_s <= self.current_config.tube_velocity_max_m_s
            and self.current_config.shell_velocity_min_m_s <= hydraulic.shell_velocity_m_s <= self.current_config.shell_velocity_max_m_s
        )
        overall_ok = area_ok and velocity_ok and hydraulic.tube_pressure_drop_ok and hydraulic.shell_pressure_drop_ok

        self.presentation_widgets["hot_mass_flow"].configure(text=f"{operating.hot_mass_flow_kg_s:.3f} kg/s")
        self.presentation_widgets["hot_temp_span"].configure(text=f"{operating.hot_inlet_temp_c:.0f} → {operating.hot_outlet_temp_c:.0f} ℃")
        self.presentation_widgets["cold_temp_span"].configure(text=f"{operating.cold_inlet_temp_c:.0f} → {operating.cold_outlet_temp_c:.0f} ℃")
        self.presentation_widgets["pressure_span"].configure(text=f"煤油 {operating.hot_pressure_mpa:.1f} / 水 {operating.cold_pressure_mpa:.1f} MPa")

        self.presentation_widgets["heat_duty"].configure(text=f"{thermal.heat_duty_w / 1000:.2f} kW")
        self.presentation_widgets["water_flow"].configure(text=f"{thermal.cold_mass_flow_kg_s:.3f} kg/s")
        self.presentation_widgets["u_value"].configure(text=f"{thermal.overall_u_calculated_w_m2_k:.2f} W/(m²·K)")
        self.presentation_widgets["area_pair"].configure(text=f"{thermal.required_area_m2:.2f} / {mechanical.actual_area_m2:.2f} m²")
        self.presentation_widgets["geometry"].configure(
            text=f"{mechanical.tube_geometry.tube_length_m:.1f} m，{mechanical.tube_geometry.tube_count} 根，{mechanical.tube_geometry.tubes_per_pass} 根/程"
        )
        self.presentation_widgets["pressure_drop"].configure(
            text=f"{hydraulic.tube_pressure_drop_pa/1000:.2f} / {hydraulic.shell_pressure_drop_pa/1000:.2f} kPa"
        )

        self._set_status_label("area_ok", area_ok, "满足", "不足")
        self._set_status_label("velocity_ok", velocity_ok, "满足", "异常")
        self._set_status_label("tube_dp_ok", hydraulic.tube_pressure_drop_ok, "合格", "超限")
        self._set_status_label("shell_dp_ok", hydraulic.shell_pressure_drop_ok, "合格", "超限")
        self._set_status_label("overall_ok", overall_ok, "推荐方案", "需调整")

        self.presentation_widgets["presentation_note"].configure(
            text=(
                f"本页适合答辩展示时直接讲解：先指出热负荷 {thermal.heat_duty_w / 1000:.2f} kW，"
                f"再说明采用 {mechanical.tube_geometry.tube_length_m:.1f} m、{mechanical.tube_geometry.tube_count} 根换热管的方案，"
                f"最后强调管程与壳程压降均低于许用值，因此方案可行。"
            )
        )
        self._update_flow_steps(design, overall_ok)
        self._update_faq_section(design, area_ok, velocity_ok)

    def _clear_presentation_page(self, reason: str) -> None:
        for key, widget in self.presentation_widgets.items():
            if key == "presentation_note":
                widget.configure(text=f"当前方案未通过校核：{reason}")
            else:
                widget.configure(text="--", foreground="#0f172a")
        for frame in self.flow_step_frames.values():
            frame.configure(bg="#fff7ed", highlightbackground="#fed7aa")
        self.presentation_widgets["flow_conclusion"].configure(text="方案失败\n需要调整参数", foreground="#b91c1c", bg="#fff7ed")
        self._set_faq_text(f"1. 为什么当前方案失败？\n答：{reason}\n\n2. 下一步怎么调？\n答：优先检查流速范围、面积裕量上限和许用压降设置，再重新筛选几何方案。")

    def _set_status_label(self, key: str, ok: bool, ok_text: str, fail_text: str) -> None:
        color = "#15803d" if ok else "#b91c1c"
        text = ok_text if ok else fail_text
        self.presentation_widgets[key].configure(text=text, foreground=color)

    def _update_flow_steps(self, design, overall_ok: bool) -> None:
        thermal = design.thermal_result
        mechanical = design.mechanical_result
        hydraulic = design.hydraulic_result
        steps = {
            "flow_input": ("工况已载入\n物性可插值", "#eff6ff", "#93c5fd", "#1d4ed8"),
            "flow_thermal": (f"Q={thermal.heat_duty_w/1000:.1f} kW\nA={thermal.required_area_m2:.2f} m²", "#eefbf3", "#86efac", "#166534"),
            "flow_mechanical": (f"L={mechanical.tube_geometry.tube_length_m:.1f} m\nN={mechanical.tube_geometry.tube_count} 根", "#fff7ed", "#fdba74", "#9a3412"),
            "flow_hydraulic": (f"管程 {hydraulic.tube_pressure_drop_pa/1000:.2f} kPa\n壳程 {hydraulic.shell_pressure_drop_pa/1000:.2f} kPa", "#f5f3ff", "#c4b5fd", "#6d28d9"),
            "flow_conclusion": (("推荐方案\n满足要求" if overall_ok else "方案失败\n需要调整"), "#ecfdf3" if overall_ok else "#fef2f2", "#86efac" if overall_ok else "#fca5a5", "#15803d" if overall_ok else "#b91c1c"),
        }
        for key, (text, bg, border, fg) in steps.items():
            self.flow_step_frames[key].configure(bg=bg, highlightbackground=border)
            self.presentation_widgets[key].configure(text=text, bg=bg, fg=fg)

    def _update_faq_section(self, design, area_ok: bool, velocity_ok: bool) -> None:
        thermal = design.thermal_result
        mechanical = design.mechanical_result
        hydraulic = design.hydraulic_result
        faq = (
            "1. 为什么选择水走管程、煤油走壳程？\n"
            "答：水的换热系数通常更高、黏度更低，放在管程更容易获得较高管内传热效果，同时也更便于清洗和控制压降；煤油走壳程则更符合课程设计中的常见布置。\n\n"
            "2. 为什么最终选了这个结构方案？\n"
            f"答：程序在候选管长和管数中自动筛选，最终选到管长 {mechanical.tube_geometry.tube_length_m:.1f} m、总管数 {mechanical.tube_geometry.tube_count} 根的方案，"
            f"因为它同时满足面积要求、流速约束和压降约束，且面积裕量为 {mechanical.area_margin_ratio:.2%}，属于较合理的课程设计结果。\n\n"
            "3. 为什么先用经验总传热系数，再做校核？\n"
            f"答：课程设计里通常先用经验值进行面积初选，便于快速确定设备量级；本程序先取 U_assumed={thermal.overall_u_assumed_w_m2_k:.0f} W/(m²·K) 初选，"
            f"再根据膜传热系数、污垢热阻和壁热阻校核得到 U_calculated={thermal.overall_u_calculated_w_m2_k:.2f} W/(m²·K)，这样更符合设计步骤。\n\n"
            "4. 这个方案到底有没有满足要求？\n"
            f"答：面积校核为 {'满足' if area_ok else '不满足'}，流速校核为 {'满足' if velocity_ok else '不满足'}，"
            f"管程压降 {'合格' if hydraulic.tube_pressure_drop_ok else '超限'}，壳程压降 {'合格' if hydraulic.shell_pressure_drop_ok else '超限'}，"
            "所以当前方案可以作为推荐方案。\n\n"
            "5. 这个程序和手算相比有什么价值？\n"
            "答：它能把物性插值、热工计算、结构筛选和阻力校核串成一套可重复流程，修改参数后可以快速得到新结果，也更方便展示中间量和失败原因。"
        )
        self._set_faq_text(faq)

    def _set_faq_text(self, content: str) -> None:
        self.faq_text.configure(state="normal")
        self.faq_text.delete("1.0", "end")
        self.faq_text.insert("1.0", content)
        self.faq_text.configure(state="disabled")

    def _set_conclusion_text(self, title: str, content: str) -> None:
        self.conclusion_text.configure(state="normal")
        self.conclusion_text.delete("1.0", "end")
        self.conclusion_text.insert("1.0", f"{title}\n\n{content}")
        self.conclusion_text.configure(state="disabled")

    def _append_log(self, content: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", content.strip() + "\n\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _build_conclusion(self, design) -> str:
        thermal = design.thermal_result
        mechanical = design.mechanical_result
        hydraulic = design.hydraulic_result
        return (
            f"热负荷为 {thermal.heat_duty_w:.2f} W，冷却水流量为 {thermal.cold_mass_flow_kg_s:.3f} kg/s。\n"
            f"最终选定管长 {mechanical.tube_geometry.tube_length_m:.2f} m，总管数 {mechanical.tube_geometry.tube_count} 根，"
            f"实际面积 {mechanical.actual_area_m2:.3f} m²，面积裕量 {mechanical.area_margin_ratio:.3%}。\n"
            f"管程压降 {hydraulic.tube_pressure_drop_pa:.1f} Pa，壳程压降 {hydraulic.shell_pressure_drop_pa:.1f} Pa。"
            " 当前方案满足面积、流速和压降约束，可作为课程设计推荐方案。"
        )

    def _build_log(self, design) -> str:
        thermal = design.thermal_result
        mechanical = design.mechanical_result
        hydraulic = design.hydraulic_result
        lines = [
            "[计算完成]",
            f"Q = {thermal.heat_duty_w:.2f} W",
            f"m_c = {thermal.cold_mass_flow_kg_s:.3f} kg/s",
            f"LMTD = {thermal.lmtd_k:.3f} K, F = {thermal.correction_factor:.4f}, ΔT_eff = {thermal.effective_temp_diff_k:.3f} K",
            f"U_assumed = {thermal.overall_u_assumed_w_m2_k:.2f} W/(m²·K)",
            f"U_calculated = {thermal.overall_u_calculated_w_m2_k:.2f} W/(m²·K)",
            f"A_required = {thermal.required_area_m2:.3f} m²",
            f"Candidate = {mechanical.candidate_id}",
            f"Tube velocity = {hydraulic.tube_velocity_m_s:.3f} m/s, Shell velocity = {hydraulic.shell_velocity_m_s:.3f} m/s",
            f"Tube ΔP = {hydraulic.tube_pressure_drop_pa:.1f} Pa, Shell ΔP = {hydraulic.shell_pressure_drop_pa:.1f} Pa",
        ]
        return "\n".join(lines)

    def _build_export_markdown(self, design) -> str:
        sections = ["# 计算结果摘要", "", "## 综合结论", self._build_conclusion(design), ""]
        for title, key in (("传热计算", "thermal"), ("结构计算", "mechanical"), ("阻力计算", "hydraulic")):
            sections.append(f"## {title}")
            sections.append("| 项目 | 数值 | 单位 |")
            sections.append("| --- | ---: | --- |")
            for row in design.result_tables[key]:
                item = row["项目"]
                value = row["值"]
                unit = row["单位"]
                value_text = f"{value:.6g}" if isinstance(value, float) else str(value)
                sections.append(f"| {item} | {value_text} | {unit} |")
            sections.append("")
        return "\n".join(sections)


def main() -> None:
    root = tk.Tk()
    app = DesignApp(root)
    app.run_calculation()
    root.mainloop()


if __name__ == "__main__":
    main()
