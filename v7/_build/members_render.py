# -*- coding: utf-8 -*-
"""
社員名冊渲染器：從 _build/data/members.json 產生 members.html 的社員區 HTML。
被 build.py 呼叫（也被一次性遷移腳本使用）。

資料驅動化第一階段（2026-07-10）：新增／修改社員只改 members.json，
中英列表由 build.py 一起重生，不再手改兩份 HTML。
"""
import json
import os

CID = "data-astro-cid-hu6ywz6e"  # Astro 時代的 scoped-CSS 屬性，樣式相依，保留

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "members.json")

MARK_START = "<!--MEMBERS:START-->"
MARK_END = "<!--MEMBERS:END-->"


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _lv(value, lang):
    """取 {"zh":..,"en":..} 的當語言值；純字串代表兩語共用。"""
    if isinstance(value, dict):
        return value[lang]
    return value


def render_card(card, lang):
    out = []
    role_attr = f' data-role="{card["dataRole"]}"' if card.get("dataRole") else ""
    out.append(f'<article class="member-card"{role_attr} {CID}>')

    profile = card.get("profile")
    if profile:
        btn = _lv(card["profileBtn"], lang)
        out.append(
            f'<a class="profile-btn" href="{profile}" {CID}>{btn} <span class="arrow" {CID}>→</span></a>'
        )

    head_open = (
        f'<a class="member-head" href="{profile}" {CID}>' if profile else f'<div class="member-head" {CID}>'
    )
    out.append(head_open)
    out.append(f'<div class="avatar" style="{_lv(card["avatarStyle"], lang)}" {CID}></div>')
    out.append(f'<div class="info" {CID}>')
    out.append(f'<div class="name" {CID}>{_lv(card["name"], lang)}</div>')
    out.append(f'<div class="role" {CID}>{_lv(card["role"], lang)}</div>')
    out.append("</div>")
    out.append("</a>" if profile else "</div>")

    if card.get("theme") or card.get("chips"):
        out.append(f'<div class="member-body" {CID}>')
        if card.get("theme"):
            out.append(f'<p class="theme-line" {CID}>{_lv(card["theme"], lang)}</p>')
        if card.get("chips"):
            out.append(f'<div class="focus-row" {CID}>')
            for chip in card["chips"]:
                out.append(
                    f'<span class="focus-chip {chip["cls"]}" {CID}>{_lv(chip["label"], lang)}</span>'
                )
            out.append("</div>")
        out.append("</div>")

    out.append("</article>")
    return " ".join(out)


def render_members(data, lang):
    out = [MARK_START]
    for i, section in enumerate(data["sections"]):
        style = ' style="margin-top:48px;"' if i == 0 else ' style="margin-top:32px;"'
        if i > 0:
            out.append(
                f'<hr style="margin:56px 0 0;border:0;border-top:1px dashed var(--line);" {CID}>'
            )
        out.append(
            f'<h3 class="member-section-sub"{style} {CID}>{_lv(section["title"], lang)}</h3>'
        )
        if section.get("desc"):
            out.append(f'<p class="section-divider-desc" {CID}>{_lv(section["desc"], lang)}</p>')
        out.append(f'<div class="member-grid" {CID}>')
        for card in section["cards"]:
            out.append(f'<!-- {_lv(card["name"], "zh")} -->')
            out.append(render_card(card, lang))
        out.append("</div>")
    if data.get("trailing"):
        out.append(_lv(data["trailing"], lang))
    out.append(MARK_END)
    return " ".join(out)


def apply_members(page_html, lang):
    """把頁面中 MEMBERS 標記區換成由 JSON 渲染的內容；無標記則原樣返回。"""
    if MARK_START not in page_html or MARK_END not in page_html:
        return page_html
    data = load_data()
    start = page_html.index(MARK_START)
    end = page_html.index(MARK_END) + len(MARK_END)
    return page_html[:start] + render_members(data, lang) + page_html[end:]
