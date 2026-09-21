from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import streamlit as st

from src.config import AppConfig
from src.diagnosis_service import ApiDiagnosisService, DiagnosisError, MockDiagnosisService
from src.models import DiagnosisResult
from src.report_parser import split_report


ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="叶知 · 农作物病害诊断",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_styles() -> None:
    css = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def load_config() -> AppConfig:
    try:
        secrets: Any = st.secrets
        return AppConfig.load(secrets)
    except FileNotFoundError:
        return AppConfig.load()


def initialize_state() -> None:
    defaults = {
        "result": None,
        "history": [],
        "active_page": "智能诊断",
        "service_mode": "演示模式",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar(config: AppConfig) -> tuple[str, str]:
    with st.sidebar:
        st.markdown("## 🌿 叶知")
        st.caption("农作物病害多模态诊断")
        page = st.radio(
            "导航",
            ["智能诊断", "诊断记录", "使用指南"],
            key="active_page",
        )
        st.divider()
        st.markdown("#### 数据来源")
        mode = st.radio(
            "运行模式",
            ["演示模式", "真实接口"],
            key="service_mode",
            help="模型未完成前使用演示模式；拿到内网穿透地址后切换真实接口。",
        )
        api_url = st.text_input(
            "诊断服务地址",
            value=config.api_url,
            disabled=mode == "演示模式",
            placeholder="https://example.com",
        ).strip()
        if mode == "真实接口":
            if st.button("检查服务连接", use_container_width=True):
                try:
                    health = ApiDiagnosisService(api_url, config.api_timeout).health()
                    st.success(f"服务可用：{health.get('status', 'ok')}")
                except DiagnosisError as exc:
                    st.error(str(exc))
        st.divider()
        st.caption("诊断结果仅供参考，请结合田间情况并咨询当地农技人员。")
    return page, api_url


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="hero-kicker">Crop Health Intelligence</div>
          <h1>拍一片叶子，读懂作物健康</h1>
          <p>上传或拍摄发病叶片，系统将给出候选病害、可信度、诊断依据和处置建议。</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def selected_image() -> tuple[bytes, str, str] | None:
    source = st.radio("图片来源", ["上传图片", "摄像头拍摄"], horizontal=True)
    if source == "上传图片":
        uploaded = st.file_uploader(
            "选择叶片照片",
            type=["jpg", "jpeg", "png", "webp"],
            help="建议使用清晰的叶片特写，文件不超过 10MB。",
        )
    else:
        uploaded = st.camera_input("拍摄叶片")

    if uploaded is None:
        return None

    image_bytes = uploaded.getvalue()
    mime_type = getattr(uploaded, "type", None) or "image/jpeg"
    filename = getattr(uploaded, "name", None) or "camera.jpg"
    st.image(image_bytes, caption="待诊断图片", use_container_width=True)
    return image_bytes, filename, mime_type


def run_diagnosis(
    image: tuple[bytes, str, str], mode: str, api_url: str, timeout: int
) -> DiagnosisResult | None:
    image_bytes, filename, mime_type = image
    service = (
        MockDiagnosisService()
        if mode == "演示模式"
        else ApiDiagnosisService(api_url, timeout)
    )

    try:
        with st.status("正在分析叶片…", expanded=True) as status:
            st.write("✓ 图片已准备")
            st.write("正在运行专用病害分类器…")
            result = service.diagnose(image_bytes, filename, mime_type)
            st.write("✓ 已获得候选病害")
            st.write("✓ 智能复核完成")
            status.update(label="诊断完成", state="complete", expanded=False)
    except DiagnosisError as exc:
        st.error(str(exc))
        return None
    except Exception as exc:  # 保证演示时页面不会因未知异常整体中断
        st.error(f"诊断过程中发生异常：{exc}")
        return None

    st.session_state.result = result
    history = list(st.session_state.history)
    history.insert(0, result.to_dict())
    st.session_state.history = history[:20]
    return result


def confidence_meta(level: str) -> tuple[str, str]:
    return {
        "high": ("高可信度", "confidence-high"),
        "medium": ("需智能复核", "confidence-medium"),
        "low": ("低可信度", "confidence-low"),
    }.get(level, ("可信度未知", "confidence-low"))


def render_result(result: DiagnosisResult) -> None:
    label, css_class = confidence_meta(result.confidence_level)
    safe_name = html.escape(result.classifier_top1)
    st.markdown('<div class="section-label">DIAGNOSIS RESULT</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <section class="result-hero">
          <span class="confidence-pill {css_class}">{label}</span>
          <div class="result-name">{safe_name}</div>
          <div class="small-note">分类置信度 {result.confidence:.1%} · 用时 {result.elapsed_ms / 1000:.1f} 秒</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 候选判断")
    for index, candidate in enumerate(result.candidates, start=1):
        name_col, score_col = st.columns([4, 1])
        with name_col:
            st.markdown(f"**{index}. {candidate.label_cn}**  ·  `{candidate.label_en}`")
            st.progress(candidate.score)
        with score_col:
            st.metric("概率", f"{candidate.score:.1%}")

    st.markdown("### 智能诊断报告")
    if result.vlm_report:
        sections = split_report(result.vlm_report)
        for row_start in range(0, len(sections), 2):
            row = sections[row_start : row_start + 2]
            columns = st.columns(len(row))
            for column, (title, content) in zip(columns, row):
                with column:
                    st.markdown(
                        '<section class="report-section">'
                        f"<h4>{html.escape(title)}</h4>"
                        f"<p>{html.escape(content).replace(chr(10), '<br>')}</p>"
                        "</section>",
                        unsafe_allow_html=True,
                    )
    else:
        st.warning(f"智能复核暂不可用：{result.vlm_error or '未返回报告'}")

    st.info("结果仅供辅助判断。用药前请核对农药标签、登记作物与安全间隔期，并咨询当地农技人员。")


def diagnosis_page(mode: str, api_url: str, timeout: int) -> None:
    render_hero()
    left, right = st.columns([1.45, 0.75], gap="large")
    with left:
        st.markdown("### 叶片采集")
        image = selected_image()
        diagnose_clicked = st.button(
            "开始智能诊断",
            type="primary",
            use_container_width=True,
            disabled=image is None,
        )
    with right:
        st.markdown("### 拍摄建议")
        with st.container(border=True):
            st.markdown(
                """
                - 让病斑区域占据画面主体
                - 使用自然光，避免强烈反光
                - 保持焦点清晰，减少背景杂物
                - 正反面症状不同时可分别诊断
                """
            )
        st.caption(f"当前：{'本地模拟数据' if mode == '演示模式' else api_url}")

    if diagnose_clicked and image is not None:
        run_diagnosis(image, mode, api_url, timeout)

    result = st.session_state.result
    if isinstance(result, DiagnosisResult):
        render_result(result)


def history_page() -> None:
    st.title("诊断记录")
    st.caption("当前阶段记录保存在浏览器会话中，后续可接入 SQLite 或业务数据库。")
    history = st.session_state.history
    if not history:
        st.info("暂无诊断记录。完成一次图片诊断后，结果会出现在这里。")
        return

    for index, item in enumerate(history, start=1):
        with st.expander(
            f"{index}. {item['classifier_top1']} · {float(item['confidence']):.1%}",
            expanded=index == 1,
        ):
            st.write(item.get("vlm_report") or item.get("vlm_error") or "暂无智能报告")
            st.caption(f"诊断耗时：{int(item.get('elapsed_ms', 0)) / 1000:.1f} 秒")

    if st.button("清空当前会话记录"):
        st.session_state.history = []
        st.rerun()


def guide_page() -> None:
    st.title("使用指南")
    tab_photo, tab_scope, tab_notice = st.tabs(["拍摄方法", "支持范围", "结果说明"])
    with tab_photo:
        st.markdown(
            """
            ### 怎样拍出更容易识别的照片

            1. 选择具有代表性的病叶，不要只拍整片田地。
            2. 让叶片占画面的三分之二以上，并对焦病斑。
            3. 避免滤镜、强背光、水滴遮挡和过度压缩。
            4. 同一植株可以从不同角度分别诊断，再综合判断。
            """
        )
    with tab_scope:
        st.markdown(
            """
            当前模型规划覆盖番茄、苹果、玉米、葡萄、马铃薯、桃、甜椒、草莓和柑橘等
            **14 种作物、38 个类别**。水稻、小麦和黄瓜暂不在专用分类模型覆盖范围内。
            """
        )
    with tab_notice:
        st.warning(
            "AI 结果不能替代实验室检测或专业农技人员判断。低可信度、症状持续扩大或涉及大面积用药时，"
            "请联系当地农业技术推广部门。"
        )


load_styles()
initialize_state()
config = load_config()
page, configured_api_url = render_sidebar(config)

if page == "智能诊断":
    diagnosis_page(st.session_state.service_mode, configured_api_url, config.api_timeout)
elif page == "诊断记录":
    history_page()
else:
    guide_page()

